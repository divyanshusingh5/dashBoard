"""
Aggregation API - Optimized for real-time dashboard data
Computes all aggregations from SQLite database
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.services.data_service_sqlite import data_service_sqlite as data_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/aggregated")
async def get_aggregated_data(use_fast: bool = Query(True, description="Use materialized views for fast aggregation")):
    """
    Get all aggregated data for dashboard
    OPTIMIZED: Uses pre-computed materialized views for 5M+ records (60x faster)
    Set use_fast=false to force real-time computation (slower)
    """
    try:
        if use_fast:
            # Use materialized views (FAST - recommended for 5M+ records)
            logger.info("Using materialized views for aggregation (FAST mode)...")
            result = await data_service.get_aggregated_data_fast()

            if not result or not result.get('yearSeverity'):
                logger.warning("Materialized views empty or not found, falling back to real-time computation...")
                use_fast = False
            else:
                # Calculate variance drivers from aggregated data
                variance_drivers = []

                # Use injury group variance as driver
                for item in result.get('injuryGroup', []):
                    avg_var = item.get('avg_variance_pct', 0)
                    if avg_var and abs(avg_var) > 5:
                        variance_drivers.append({
                            'factor_name': f"Injury: {item.get('injury_group', 'Unknown')}",
                            'factor_value': item.get('severity_category', 'Unknown'),
                            'claim_count': item.get('claim_count', 0),
                            'avg_variance_pct': round(float(avg_var), 2),
                            'contribution_score': round(abs(float(avg_var)) * 2, 2),
                            'correlation_strength': 'Strong' if abs(avg_var) > 15 else 'Moderate' if abs(avg_var) > 10 else 'Weak'
                        })

                # Use county variance as driver
                for item in result.get('countyYear', []):
                    avg_var = item.get('avg_variance_pct', 0)
                    if avg_var and abs(avg_var) > 8:
                        variance_drivers.append({
                            'factor_name': f"County: {item.get('county', 'Unknown')}",
                            'factor_value': f"{item.get('state', '')}, {item.get('year', '')}",
                            'claim_count': item.get('claim_count', 0),
                            'avg_variance_pct': round(float(avg_var), 2),
                            'contribution_score': round(abs(float(avg_var)) * 1.5, 2),
                            'correlation_strength': 'Strong' if abs(avg_var) > 15 else 'Moderate'
                        })

                result['varianceDrivers'] = sorted(
                    variance_drivers,
                    key=lambda x: x['contribution_score'],
                    reverse=True
                )[:30]

                # Add metadata
                total_claims = sum(item.get('claim_count', 0) for item in result.get('yearSeverity', []))
                result['metadata'] = {
                    "total_claims": total_claims,
                    "generated_at": datetime.now().isoformat(),
                    "source": "materialized_views",
                    "performance": "fast"
                }

                logger.info(f"Returned aggregated data for {total_claims} claims from materialized views")
                return result

        # Fallback to real-time computation (SLOW - for small datasets or when views don't exist)
        logger.info("Loading claims for real-time aggregation (SLOW mode)...")
        claims = await data_service.get_full_claims_data()

        if not claims:
            raise HTTPException(status_code=404, detail="No claims data available")

        df = pd.DataFrame(claims)
        logger.info(f"Loaded {len(df)} claims for aggregation")

        # Extract year from CLAIMCLOSEDDATE
        df['year'] = pd.to_datetime(df['CLAIMCLOSEDDATE'], errors='coerce').dt.year
        df['year'] = df['year'].fillna(2024).astype(int)

        # Calculate one year ago
        current_year = datetime.now().year
        one_year_ago = current_year - 1

        # 1. Year-Severity Summary
        year_severity = df.groupby(['year', 'CAUTION_LEVEL']).agg({
            'CLAIMID': 'count',
            'DOLLARAMOUNTHIGH': ['sum', 'mean'],
            'CAUSATION_HIGH_RECOMMENDATION': ['sum', 'mean'],
            'variance_pct': 'mean'
        }).reset_index()

        year_severity.columns = ['year', 'severity_category', 'claim_count',
                                 'total_actual_settlement', 'avg_actual_settlement',
                                 'total_predicted_settlement', 'avg_predicted_settlement',
                                 'avg_variance_pct']

        # Add variance counts efficiently
        year_severity['overprediction_count'] = 0
        year_severity['underprediction_count'] = 0
        year_severity['high_variance_count'] = 0

        for idx, row in year_severity.iterrows():
            subset = df[(df['year'] == row['year']) & (df['CAUTION_LEVEL'] == row['severity_category'])]
            year_severity.at[idx, 'overprediction_count'] = int((subset['variance_pct'] > 0).sum())
            year_severity.at[idx, 'underprediction_count'] = int((subset['variance_pct'] < 0).sum())
            year_severity.at[idx, 'high_variance_count'] = int((subset['variance_pct'].abs() >= 15).sum())

        # 2. County-Year Summary
        county_year = df.groupby(['COUNTYNAME', 'VENUESTATE', 'year', 'VENUERATING']).agg({
            'CLAIMID': 'count',
            'DOLLARAMOUNTHIGH': ['sum', 'mean'],
            'variance_pct': 'mean'
        }).reset_index()

        county_year.columns = ['county', 'state', 'year', 'venue_rating', 'claim_count',
                               'total_settlement', 'avg_settlement', 'avg_variance_pct']

        county_year['high_variance_count'] = 0
        county_year['high_variance_pct'] = 0.0
        county_year['overprediction_count'] = 0
        county_year['underprediction_count'] = 0

        for idx, row in county_year.iterrows():
            subset = df[(df['COUNTYNAME'] == row['county']) & (df['year'] == row['year'])]
            hvc = int((subset['variance_pct'].abs() >= 15).sum())
            county_year.at[idx, 'high_variance_count'] = hvc
            county_year.at[idx, 'high_variance_pct'] = round((hvc / row['claim_count'] * 100) if row['claim_count'] > 0 else 0, 2)
            county_year.at[idx, 'overprediction_count'] = int((subset['variance_pct'] > 0).sum())
            county_year.at[idx, 'underprediction_count'] = int((subset['variance_pct'] < 0).sum())

        # 3. Injury Group Summary
        injury_group = df.groupby(['PRIMARY_INJURYGROUP_CODE', 'CAUTION_LEVEL']).agg({
            'CLAIMID': 'count',
            'DOLLARAMOUNTHIGH': ['mean', 'sum'],
            'CAUSATION_HIGH_RECOMMENDATION': 'mean',
            'variance_pct': 'mean'
        }).reset_index()

        injury_group.columns = ['injury_group', 'severity_category', 'claim_count',
                                'avg_settlement', 'total_settlement', 'avg_predicted',
                                'avg_variance_pct']
        injury_group['body_region'] = 'General'

        # 4. Adjuster Performance
        adjuster_perf = df.groupby('ADJUSTERNAME').agg({
            'CLAIMID': 'count',
            'DOLLARAMOUNTHIGH': 'mean',
            'CAUSATION_HIGH_RECOMMENDATION': 'mean',
            'variance_pct': 'mean'
        }).reset_index()

        adjuster_perf.columns = ['adjuster_name', 'claim_count', 'avg_actual_settlement',
                                 'avg_predicted_settlement', 'avg_variance_pct']

        adjuster_perf['high_variance_count'] = 0
        adjuster_perf['high_variance_pct'] = 0.0
        adjuster_perf['overprediction_count'] = 0
        adjuster_perf['underprediction_count'] = 0

        for idx, row in adjuster_perf.iterrows():
            subset = df[df['ADJUSTERNAME'] == row['adjuster_name']]
            hvc = int((subset['variance_pct'].abs() >= 15).sum())
            adjuster_perf.at[idx, 'high_variance_count'] = hvc
            adjuster_perf.at[idx, 'high_variance_pct'] = round((hvc / row['claim_count'] * 100) if row['claim_count'] > 0 else 0, 2)
            adjuster_perf.at[idx, 'overprediction_count'] = int((subset['variance_pct'] > 0).sum())
            adjuster_perf.at[idx, 'underprediction_count'] = int((subset['variance_pct'] < 0).sum())

        # 5. Venue Analysis
        venue_analysis = df.groupby(['VENUERATING', 'VENUESTATE', 'COUNTYNAME']).agg({
            'CLAIMID': 'count',
            'DOLLARAMOUNTHIGH': 'mean',
            'CAUSATION_HIGH_RECOMMENDATION': 'mean',
            'variance_pct': 'mean',
            'RATINGWEIGHT': 'mean'
        }).reset_index()

        venue_analysis.columns = ['venue_rating', 'state', 'county', 'claim_count',
                                  'avg_settlement', 'avg_predicted', 'avg_variance_pct',
                                  'avg_venue_rating_point']

        venue_analysis['high_variance_count'] = 0
        venue_analysis['high_variance_pct'] = 0.0

        for idx, row in venue_analysis.iterrows():
            subset = df[(df['VENUERATING'] == row['venue_rating']) & (df['COUNTYNAME'] == row['county'])]
            hvc = int((subset['variance_pct'].abs() >= 15).sum())
            venue_analysis.at[idx, 'high_variance_count'] = hvc
            venue_analysis.at[idx, 'high_variance_pct'] = round((hvc / row['claim_count'] * 100) if row['claim_count'] > 0 else 0, 2)

        # 6. Variance Drivers (correlation analysis)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        variance_drivers = []

        for col in numeric_cols:
            if col != 'variance_pct' and df[col].notna().sum() > 0:
                try:
                    corr = df[col].corr(df['variance_pct'])
                    if not pd.isna(corr) and abs(corr) > 0.05:
                        variance_drivers.append({
                            'factor_name': col,
                            'factor_value': 'Varies',
                            'claim_count': len(df),
                            'avg_variance_pct': float(df['variance_pct'].mean()),
                            'contribution_score': float(abs(corr) * 100),
                            'correlation_strength': 'Strong' if abs(corr) > 0.5 else 'Moderate' if abs(corr) > 0.3 else 'Weak'
                        })
                except:
                    pass

        variance_drivers_sorted = sorted(variance_drivers, key=lambda x: x['contribution_score'], reverse=True)[:30]

        logger.info("Aggregation completed successfully")

        return {
            "yearSeverity": year_severity.to_dict('records'),
            "countyYear": county_year.to_dict('records'),
            "injuryGroup": injury_group.to_dict('records'),
            "adjusterPerformance": adjuster_perf.to_dict('records'),
            "venueAnalysis": venue_analysis.to_dict('records'),
            "varianceDrivers": variance_drivers_sorted,
            "metadata": {
                "total_claims": len(df),
                "recent_year_claims": len(df[df['year'] >= one_year_ago]),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error in aggregation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Aggregation error: {str(e)}")


@router.get("/recent-trends")
async def get_recent_trends(months: int = Query(12, ge=1, le=36, description="Months to look back")):
    """
    Get trends for recent data (last N months)
    For weight recalibration decisions
    """
    try:
        claims = await data_service.get_full_claims_data()
        if not claims:
            raise HTTPException(status_code=404, detail="No claims data")

        df = pd.DataFrame(claims)
        df['CLAIMCLOSEDDATE'] = pd.to_datetime(df['CLAIMCLOSEDDATE'], errors='coerce')

        # Filter recent data
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        recent_df = df[df['CLAIMCLOSEDDATE'] >= cutoff_date]

        if len(recent_df) == 0:
            return {"message": "No recent data available", "trends": []}

        # Monthly trends
        recent_df['month'] = recent_df['CLAIMCLOSEDDATE'].dt.to_period('M')
        monthly_trends = recent_df.groupby('month').agg({
            'CLAIMID': 'count',
            'variance_pct': ['mean', 'std', 'median'],
            'DOLLARAMOUNTHIGH': 'mean'
        }).reset_index()

        monthly_trends['month'] = monthly_trends['month'].astype(str)
        monthly_trends.columns = ['month', 'claim_count', 'avg_variance', 'std_variance',
                                  'median_variance', 'avg_settlement']

        return {
            "period_months": months,
            "total_recent_claims": len(recent_df),
            "monthly_trends": monthly_trends.to_dict('records'),
            "summary": {
                "avg_variance": float(recent_df['variance_pct'].mean()),
                "median_variance": float(recent_df['variance_pct'].median()),
                "std_variance": float(recent_df['variance_pct'].std()),
                "high_variance_rate": float((recent_df['variance_pct'].abs() >= 15).sum() / len(recent_df) * 100)
            }
        }

    except Exception as e:
        logger.error(f"Error getting recent trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/venue-shift-analysis")
async def get_venue_shift_recommendations(
    months: int = Query(
        default=6,
        ge=1,
        le=24,
        description="Analysis period in months (1-24)"
    )
):
    """
    Analyze venue rating performance and recommend potential shifts
    OPTIMIZED FOR 5M+ CLAIMS - Uses database-level aggregations
    Uses isolated analysis to control for injury type, severity, and impact
    Returns recommendations for venue rating adjustments by county
    """
    # Use the optimized implementation from aggregation_optimized_venue_shift.py
    from app.api.endpoints.aggregation_optimized_venue_shift import get_venue_shift_recommendations_optimized

    try:
        logger.info(f"[OPTIMIZED] Starting venue shift analysis for last {months} months...")
        return await get_venue_shift_recommendations_optimized(data_service, months)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in venue shift analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Venue shift analysis error: {str(e)}")


@router.post("/refresh-cache")
async def refresh_materialized_views():
    """
    Refresh all materialized views (pre-computed aggregation tables)

    Call this endpoint after:
    - Importing new CSV data
    - Manual data updates
    - Weekly/daily maintenance

    This will recompute all aggregations from the claims table
    Takes 5-30 seconds depending on data size (5M records ~30s)
    """
    try:
        from app.db.materialized_views import refresh_all_materialized_views
        import asyncio

        logger.info("Starting materialized view refresh...")
        start_time = datetime.now()

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(None, refresh_all_materialized_views)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        if success:
            logger.info(f"Materialized views refreshed in {duration:.2f}s")
            return {
                "status": "success",
                "message": "Materialized views refreshed successfully",
                "duration_seconds": round(duration, 2),
                "timestamp": end_time.isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to refresh materialized views")

    except Exception as e:
        logger.error(f"Error refreshing materialized views: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Refresh error: {str(e)}")


@router.get("/cache-status")
async def get_cache_status():
    """
    Get status of materialized views (cache)
    Shows row counts and last update times
    """
    try:
        from app.db.materialized_views import get_materialized_view_stats, check_materialized_views_exist
        import asyncio

        loop = asyncio.get_event_loop()

        # Check if views exist
        views_exist = await loop.run_in_executor(None, check_materialized_views_exist)

        if not views_exist:
            return {
                "status": "not_initialized",
                "message": "Materialized views not found. Run POST /refresh-cache to create them.",
                "views_exist": False
            }

        # Get stats
        stats = await loop.run_in_executor(None, get_materialized_view_stats)

        return {
            "status": "active",
            "message": "Materialized views are active and ready",
            "views_exist": True,
            "statistics": stats,
            "total_aggregated_rows": sum(v.get('row_count', 0) for v in stats.values())
        }

    except Exception as e:
        logger.error(f"Error getting cache status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executive-summary")
async def get_executive_summary(
    version_id: Optional[int] = Query(None, description="Filter by Version ID"),
    year: Optional[int] = Query(None, description="Filter by Year"),
    severity: Optional[str] = Query(None, description="Filter by Severity Level (Low/Medium/High)"),
    county: Optional[str] = Query(None, description="Filter by County"),
    injury_type: Optional[str] = Query(None, description="Filter by Injury Type"),
    venue_rating: Optional[str] = Query(None, description="Filter by Venue Rating"),
    limit: int = Query(100, description="Max number of results to return")
):
    """
    Get executive summary with multi-factor performance analysis
    Shows top variance factors across ALL dimensions (Severity, Injury, Venue, IOL, County)
    """
    try:
        import asyncio
        loop = asyncio.get_event_loop()

        def get_summary():
            from sqlalchemy import text, create_engine
            from pathlib import Path

            db_path = Path('app/db/claims_analytics.db')
            engine = create_engine(f'sqlite:///{db_path}')

            with engine.connect() as conn:
                # Build WHERE clause
                where_clauses = []
                if version_id is not None:
                    where_clauses.append(f"version_id = {version_id}")
                if year is not None:
                    where_clauses.append(f"year = {year}")
                if severity:
                    where_clauses.append(f"severity_level = '{severity}'")
                if county:
                    where_clauses.append(f"county = '{county}'")
                if injury_type:
                    where_clauses.append(f"injury_type = '{injury_type}'")
                if venue_rating:
                    where_clauses.append(f"venue_rating = '{venue_rating}'")

                where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""

                query = text(f"""
                    SELECT
                        factor_combination,
                        severity_level,
                        injury_type,
                        body_part,
                        venue_rating,
                        county,
                        state,
                        impact_on_life,
                        version_id,
                        year,
                        claim_count,
                        avg_actual,
                        avg_predicted,
                        avg_deviation_pct,
                        abs_avg_deviation_pct,
                        min_deviation,
                        max_deviation,
                        risk_level,
                        total_dollar_error,
                        avg_dollar_error
                    FROM mv_executive_summary
                    WHERE 1=1 {where_sql}
                    ORDER BY abs_avg_deviation_pct DESC
                    LIMIT {limit}
                """)

                result = conn.execute(query)
                rows = result.fetchall()
                columns = result.keys()

                return [dict(zip(columns, row)) for row in rows]

        data = await loop.run_in_executor(None, get_summary)

        return {
            "status": "success",
            "count": len(data),
            "filters": {
                "version_id": version_id,
                "year": year,
                "severity": severity,
                "county": county,
                "injury_type": injury_type,
                "venue_rating": venue_rating
            },
            "data": data
        }

    except Exception as e:
        logger.error(f"Error getting executive summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-variance-factors")
async def get_top_variance_factors(
    dimension: Optional[str] = Query(None, description="Filter by dimension (Severity/Injury Type/Venue Rating/Impact on Life/County)")
):
    """
    Get top 10 high-variance factors by each dimension
    Dimensions: Severity, Injury Type, Venue Rating, Impact on Life, County
    """
    try:
        import asyncio
        loop = asyncio.get_event_loop()

        def get_top_factors():
            from sqlalchemy import text, create_engine
            from pathlib import Path

            db_path = Path('app/db/claims_analytics.db')
            engine = create_engine(f'sqlite:///{db_path}')

            with engine.connect() as conn:
                where_sql = f" WHERE dimension = '{dimension}'" if dimension else ""

                query = text(f"""
                    SELECT
                        dimension,
                        factor_value,
                        total_claims,
                        avg_deviation,
                        total_error,
                        risk_level,
                        county,
                        state
                    FROM mv_top_variance_factors
                    {where_sql}
                    ORDER BY dimension, avg_deviation DESC
                """)

                result = conn.execute(query)
                rows = result.fetchall()
                columns = result.keys()

                return [dict(zip(columns, row)) for row in rows]

        data = await loop.run_in_executor(None, get_top_factors)

        # Group by dimension
        grouped = {}
        for item in data:
            dim = item['dimension']
            if dim not in grouped:
                grouped[dim] = []
            grouped[dim].append(item)

        return {
            "status": "success",
            "count": len(data),
            "filter": {"dimension": dimension},
            "data": data,
            "grouped_by_dimension": grouped
        }

    except Exception as e:
        logger.error(f"Error getting top variance factors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/county-comparison")
async def get_county_comparison(
    severity: Optional[str] = Query(None, description="Severity Level (Low/Medium/High)"),
    injury: Optional[str] = Query(None, description="Injury Type"),
    venue: Optional[str] = Query(None, description="Venue Rating"),
    iol: Optional[int] = Query(None, description="Impact on Life (1-5)"),
    version_id: Optional[int] = Query(None, description="Version ID"),
    limit: int = Query(50, description="Max counties to return")
):
    """
    Compare similar factors across counties
    For a given factor combination (severity, injury, venue, IOL),
    show which counties have the highest/lowest variance
    """
    try:
        import asyncio
        loop = asyncio.get_event_loop()

        def get_comparison():
            from sqlalchemy import text, create_engine
            from pathlib import Path

            db_path = Path('app/db/claims_analytics.db')
            engine = create_engine(f'sqlite:///{db_path}')

            with engine.connect() as conn:
                # Build WHERE clause
                where_clauses = []
                if severity:
                    where_clauses.append(f"severity_level = '{severity}'")
                if injury:
                    where_clauses.append(f"injury_type = '{injury}'")
                if venue:
                    where_clauses.append(f"venue_rating = '{venue}'")
                if iol is not None:
                    where_clauses.append(f"impact_on_life = {iol}")
                if version_id is not None:
                    where_clauses.append(f"version_id = {version_id}")

                where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

                query = text(f"""
                    SELECT
                        severity_level,
                        injury_type,
                        venue_rating,
                        impact_on_life,
                        version_id,
                        county,
                        state,
                        county_full,
                        claim_count,
                        deviation_pct,
                        avg_actual,
                        avg_predicted,
                        avg_dollar_error,
                        total_dollar_error,
                        risk_level,
                        rank_in_group,
                        counties_with_same_factors
                    FROM mv_county_comparison
                    {where_sql}
                    ORDER BY deviation_pct DESC
                    LIMIT {limit}
                """)

                result = conn.execute(query)
                rows = result.fetchall()
                columns = result.keys()

                return [dict(zip(columns, row)) for row in rows]

        data = await loop.run_in_executor(None, get_comparison)

        return {
            "status": "success",
            "count": len(data),
            "filters": {
                "severity": severity,
                "injury": injury,
                "venue": venue,
                "impact_on_life": iol,
                "version_id": version_id
            },
            "data": data,
            "message": f"Showing top {len(data)} counties with matching factors" if data else "No matching factor combinations found"
        }

    except Exception as e:
        logger.error(f"Error getting county comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
