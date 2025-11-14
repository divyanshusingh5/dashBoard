"""
Aggregation API Endpoints
Handles dashboard aggregated data and materialized view queries.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import logging

from app.core.database import get_db
from app.schemas.aggregation import (
    AggregatedDataResponse,
    ExecutiveSummaryResponse,
    YearSeverityData,
    CountyYearData,
    InjuryGroupData,
    AdjusterPerformanceData,
    VenueAnalysisData,
    ExecutiveSummaryItem
)
from app.schemas.common import MessageResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/aggregation", tags=["Aggregation"])


@router.get("/dashboard", response_model=AggregatedDataResponse)
def get_dashboard_data(
    limit: int = Query(1000, ge=1, le=10000, description="Limit per category"),
    db: Session = Depends(get_db)
):
    """
    Get complete aggregated dashboard data from materialized views.

    Returns:
    - year_severity: Aggregations by year and severity
    - county_year: Aggregations by county and year
    - injury_group: Aggregations by injury group
    - adjuster_performance: Adjuster metrics
    - venue_analysis: Venue comparisons
    - kpis: Overall KPIs
    """
    try:
        result = {
            "year_severity": [],
            "county_year": [],
            "injury_group": [],
            "adjuster_performance": [],
            "venue_analysis": [],
            "kpis": {}
        }

        # Year-Severity Data
        try:
            rows = db.execute(text(f"""
                SELECT year, severity_category, claim_count,
                       avg_actual_settlement, avg_predicted_settlement,
                       avg_variance_pct, high_variance_count
                FROM mv_year_severity
                LIMIT :limit
            """), {"limit": limit}).fetchall()

            result["year_severity"] = [
                YearSeverityData(
                    year=row[0],
                    severity_category=row[1],
                    claim_count=row[2],
                    avg_actual_settlement=row[3] or 0,
                    avg_predicted_settlement=row[4] or 0,
                    avg_variance_pct=row[5] or 0,
                    high_variance_count=row[6] or 0
                ) for row in rows
            ]
        except Exception as e:
            logger.warning(f"Could not load year_severity: {e}")

        # County-Year Data
        try:
            rows = db.execute(text(f"""
                SELECT county, state, year, venue_rating, claim_count,
                       total_settlement, avg_settlement, avg_variance_pct,
                       high_variance_pct
                FROM mv_county_year
                LIMIT :limit
            """), {"limit": limit}).fetchall()

            result["county_year"] = [
                CountyYearData(
                    county=row[0],
                    state=row[1],
                    year=row[2],
                    venue_rating=row[3],
                    claim_count=row[4],
                    total_settlement=row[5] or 0,
                    avg_settlement=row[6] or 0,
                    avg_variance_pct=row[7] or 0,
                    high_variance_pct=row[8] or 0
                ) for row in rows
            ]
        except Exception as e:
            logger.warning(f"Could not load county_year: {e}")

        # Injury Group Data
        try:
            rows = db.execute(text(f"""
                SELECT injury_group, injury_type, body_part, severity_category,
                       claim_count, avg_settlement, avg_predicted, avg_variance_pct
                FROM mv_injury_group
                LIMIT :limit
            """), {"limit": limit}).fetchall()

            result["injury_group"] = [
                InjuryGroupData(
                    injury_group=row[0],
                    injury_type=row[1],
                    body_part=row[2],
                    severity_category=row[3],
                    claim_count=row[4],
                    avg_settlement=row[5] or 0,
                    avg_predicted=row[6] or 0,
                    avg_variance_pct=row[7] or 0
                ) for row in rows
            ]
        except Exception as e:
            logger.warning(f"Could not load injury_group: {e}")

        # Adjuster Performance Data
        try:
            rows = db.execute(text(f"""
                SELECT adjuster_name, claim_count, avg_actual_settlement,
                       avg_predicted_settlement, avg_variance_pct,
                       high_variance_count, high_variance_pct
                FROM mv_adjuster_performance
                LIMIT :limit
            """), {"limit": limit}).fetchall()

            result["adjuster_performance"] = [
                AdjusterPerformanceData(
                    adjuster_name=row[0],
                    claim_count=row[1],
                    avg_actual_settlement=row[2] or 0,
                    avg_predicted_settlement=row[3] or 0,
                    avg_variance_pct=row[4] or 0,
                    high_variance_count=row[5] or 0,
                    high_variance_pct=row[6] or 0
                ) for row in rows
            ]
        except Exception as e:
            logger.warning(f"Could not load adjuster_performance: {e}")

        # Venue Analysis Data
        try:
            rows = db.execute(text(f"""
                SELECT venue_rating, state, county, claim_count,
                       avg_settlement, avg_predicted, avg_variance_pct
                FROM mv_venue_analysis
                LIMIT :limit
            """), {"limit": limit}).fetchall()

            result["venue_analysis"] = [
                VenueAnalysisData(
                    venue_rating=row[0],
                    state=row[1],
                    county=row[2],
                    claim_count=row[3],
                    avg_settlement=row[4] or 0,
                    avg_predicted=row[5] or 0,
                    avg_variance_pct=row[6] or 0
                ) for row in rows
            ]
        except Exception as e:
            logger.warning(f"Could not load venue_analysis: {e}")

        # KPIs
        try:
            kpi_row = db.execute(text("SELECT * FROM mv_kpi_summary")).first()
            if kpi_row:
                result["kpis"] = {
                    "total_claims": kpi_row[0],
                    "avg_settlement": round(kpi_row[1] or 0, 2),
                    "avg_days": round(kpi_row[2] or 0, 2),
                    "avg_abs_variance": round(kpi_row[3] or 0, 2),
                    "high_variance_pct": round(kpi_row[4] or 0, 2),
                    "overprediction_rate": round(kpi_row[5] or 0, 2),
                    "underprediction_rate": round(kpi_row[6] or 0, 2)
                }
        except Exception as e:
            logger.warning(f"Could not load kpis: {e}")
            result["kpis"] = {}

        return AggregatedDataResponse(**result)

    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executive-summary", response_model=ExecutiveSummaryResponse)
def get_executive_summary(
    limit: int = Query(50, ge=1, le=1000, description="Number of top drivers to return"),
    db: Session = Depends(get_db)
):
    """
    Get executive summary with top variance drivers.

    Returns top factors driving prediction variance sorted by absolute deviation.
    """
    try:
        rows = db.execute(text("""
            SELECT factor, category, claims, avg_deviation,
                   abs_avg_deviation, status
            FROM mv_factor_combinations
            ORDER BY abs_avg_deviation DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()

        total = db.execute(text("SELECT COUNT(*) FROM mv_factor_combinations")).scalar()

        top_drivers = [
            ExecutiveSummaryItem(
                factor=row[0],
                category=row[1],
                claims=row[2],
                avg_deviation=row[3] or 0,
                abs_avg_deviation=row[4] or 0,
                status=row[5]
            ) for row in rows
        ]

        return ExecutiveSummaryResponse(
            top_drivers=top_drivers,
            total_analyzed=total or 0
        )

    except Exception as e:
        logger.error(f"Error fetching executive summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-cache", response_model=MessageResponse)
def refresh_materialized_views(db: Session = Depends(get_db)):
    """
    Refresh all materialized views.

    This endpoint drops and recreates all materialized views with current data.
    Note: This can take several minutes for large datasets (5M+ claims).
    """
    try:
        from app.core import settings

        logger.info("Starting materialized view refresh...")

        if settings.is_sqlite:
            # SQLite: Drop and recreate
            views = [
                'mv_year_severity',
                'mv_county_year',
                'mv_injury_group',
                'mv_adjuster_performance',
                'mv_venue_analysis',
                'mv_factor_combinations',
                'mv_kpi_summary'
            ]

            for view in views:
                db.execute(text(f"DROP TABLE IF EXISTS {view}"))

            db.commit()

            # Load and execute create script
            from app.utils.query_loader import query_loader
            create_sql = query_loader.load_ddl("create_materialized_views.sql")

            # Execute the SQL (split by statement if needed)
            db.execute(text(create_sql))
            db.commit()

        elif settings.is_snowflake:
            # Snowflake: Use native REFRESH
            views = [
                'mv_year_severity',
                'mv_county_year',
                'mv_injury_group',
                'mv_adjuster_performance',
                'mv_venue_analysis',
                'mv_factor_combinations',
                'mv_kpi_summary'
            ]

            for view in views:
                db.execute(text(f"ALTER MATERIALIZED VIEW {view} REFRESH"))

            db.commit()

        logger.info("✅ Materialized views refreshed successfully")

        return MessageResponse(message="Materialized views refreshed successfully")

    except Exception as e:
        logger.error(f"Error refreshing materialized views: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to refresh views: {str(e)}")
