"""
OPTIMIZED VENUE SHIFT ANALYSIS FOR 5M+ CLAIMS
Replace the venue-shift-analysis endpoint in aggregation.py with this code
"""

from fastapi import Query, HTTPException
from datetime import datetime, timedelta
import logging
import numpy as np
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError, OperationalError

logger = logging.getLogger(__name__)


async def get_venue_shift_recommendations_optimized(data_service, months: int = 6):
    """
    Analyze venue rating performance - OPTIMIZED FOR 5M+ CLAIMS
    Uses database-level aggregations instead of loading data into memory

    Args:
        data_service: DataServiceSQLite instance
        months: Number of months to analyze (3-24)

    Returns:
        dict: Venue shift recommendations with isolated analysis
    """
    session = None
    try:
        from app.db.schema import Claim

        logger.info(f"[5M OPTIMIZED] Starting venue shift analysis for last {months} months...")

        session = data_service.get_session()
        cutoff_date = (datetime.now() - timedelta(days=months * 30)).strftime('%Y-%m-%d')

        # Step 1: Get total recent claims count (database query)
        total_recent = session.query(func.count(Claim.CLAIMID)).filter(
            Claim.CLAIMCLOSEDDATE >= cutoff_date
        ).scalar()

        logger.info(f"Analyzing {total_recent:,} recent claims (database-level aggregation)")

        if total_recent == 0:
            return {
                "message": "No recent data available for venue shift analysis",
                "recommendations": []
            }

        # Step 2: Get control variables (database-level mode calculation)
        control_injury_query = session.query(
            Claim.PRIMARY_INJURYGROUP_CODE,
            func.count(Claim.CLAIMID).label('count')
        ).filter(
            Claim.CLAIMCLOSEDDATE >= cutoff_date,
            Claim.PRIMARY_INJURYGROUP_CODE.isnot(None)
        ).group_by(Claim.PRIMARY_INJURYGROUP_CODE).order_by(func.count(Claim.CLAIMID).desc()).first()

        control_injury = control_injury_query[0] if control_injury_query else None

        control_severity_query = session.query(
            Claim.CAUTION_LEVEL,
            func.count(Claim.CLAIMID).label('count')
        ).filter(
            Claim.CLAIMCLOSEDDATE >= cutoff_date,
            Claim.CAUTION_LEVEL.isnot(None)
        ).group_by(Claim.CAUTION_LEVEL).order_by(func.count(Claim.CLAIMID).desc()).first()

        control_severity = control_severity_query[0] if control_severity_query else None

        control_impact_query = session.query(
            Claim.IOL,
            func.count(Claim.CLAIMID).label('count')
        ).filter(
            Claim.CLAIMCLOSEDDATE >= cutoff_date,
            Claim.IOL.isnot(None)
        ).group_by(Claim.IOL).order_by(func.count(Claim.CLAIMID).desc()).first()

        control_impact = control_impact_query[0] if control_impact_query else None

        logger.info(f"Control conditions: injury={control_injury}, severity={control_severity}, impact={control_impact}")

        # Step 3: Get unique counties (database-level distinct)
        counties = session.query(
            Claim.COUNTYNAME,
            Claim.VENUESTATE
        ).filter(
            Claim.CLAIMCLOSEDDATE >= cutoff_date,
            Claim.COUNTYNAME.isnot(None)
        ).distinct().all()

        logger.info(f"Found {len(counties)} unique counties to analyze")

        venue_recommendations = []

        # Step 4: Analyze each county with database-level aggregations
        for county_name, state in counties:
            if not county_name:
                continue

            # Get current venue rating (mode - database-level)
            current_venue_query = session.query(
                Claim.VENUERATING,
                func.count(Claim.CLAIMID).label('count')
            ).filter(
                Claim.CLAIMCLOSEDDATE >= cutoff_date,
                Claim.COUNTYNAME == county_name,
                Claim.VENUERATING.isnot(None)
            ).group_by(Claim.VENUERATING).order_by(func.count(Claim.CLAIMID).desc()).first()

            if not current_venue_query or not current_venue_query[0]:
                continue

            current_venue = current_venue_query[0]

            # ISOLATED ANALYSIS: Database aggregation with full controls
            isolated_current = session.query(
                func.avg(func.abs(Claim.variance_pct)).label('avg_variance'),
                func.count(Claim.CLAIMID).label('count')
            ).filter(
                Claim.CLAIMCLOSEDDATE >= cutoff_date,
                Claim.COUNTYNAME == county_name,
                Claim.VENUERATING == current_venue,
                Claim.PRIMARY_INJURYGROUP_CODE == control_injury,
                Claim.CAUTION_LEVEL == control_severity,
                Claim.IOL == control_impact
            ).first()

            # Relax controls if sample too small
            controlled_for = ['injury_type', 'severity', 'impact']

            if not isolated_current or isolated_current[1] < 5:
                isolated_current = session.query(
                    func.avg(func.abs(Claim.variance_pct)),
                    func.count(Claim.CLAIMID)
                ).filter(
                    Claim.CLAIMCLOSEDDATE >= cutoff_date,
                    Claim.COUNTYNAME == county_name,
                    Claim.VENUERATING == current_venue,
                    Claim.PRIMARY_INJURYGROUP_CODE == control_injury
                ).first()
                controlled_for = ['injury_type']

            if not isolated_current or isolated_current[1] < 3:
                isolated_current = session.query(
                    func.avg(func.abs(Claim.variance_pct)),
                    func.count(Claim.CLAIMID)
                ).filter(
                    Claim.CLAIMCLOSEDDATE >= cutoff_date,
                    Claim.COUNTYNAME == county_name,
                    Claim.VENUERATING == current_venue
                ).first()
                controlled_for = []

            if not isolated_current or isolated_current[1] == 0:
                continue

            current_avg_variance = float(isolated_current[0] or 0)
            current_claim_count = isolated_current[1]

            # Check alternative venue ratings (database aggregations)
            venue_ratings = ['Defense Friendly', 'Neutral', 'Plaintiff Friendly']
            alternative_performances = []

            for alt_venue in venue_ratings:
                if alt_venue == current_venue:
                    continue

                # Get alternative venue performance with controls
                isolated_alt = session.query(
                    func.avg(func.abs(Claim.variance_pct)),
                    func.count(Claim.CLAIMID)
                ).filter(
                    Claim.CLAIMCLOSEDDATE >= cutoff_date,
                    Claim.VENUERATING == alt_venue,
                    Claim.PRIMARY_INJURYGROUP_CODE == control_injury,
                    Claim.CAUTION_LEVEL == control_severity,
                    Claim.IOL == control_impact
                ).first()

                if not isolated_alt or isolated_alt[1] < 5:
                    isolated_alt = session.query(
                        func.avg(func.abs(Claim.variance_pct)),
                        func.count(Claim.CLAIMID)
                    ).filter(
                        Claim.CLAIMCLOSEDDATE >= cutoff_date,
                        Claim.VENUERATING == alt_venue,
                        Claim.PRIMARY_INJURYGROUP_CODE == control_injury
                    ).first()

                if isolated_alt and isolated_alt[1] >= 3:
                    alternative_performances.append({
                        'venue': alt_venue,
                        'avg_variance': float(isolated_alt[0] or 0),
                        'sample_size': isolated_alt[1]
                    })

            # Determine recommendation
            recommendation = None
            potential_improvement = 0
            confidence = 'low'

            if alternative_performances:
                best_alt = min(alternative_performances, key=lambda x: x['avg_variance'])

                if best_alt['avg_variance'] < current_avg_variance:
                    potential_improvement = current_avg_variance - best_alt['avg_variance']

                    # Only recommend if improvement is significant
                    if potential_improvement > 2.0 or (potential_improvement / current_avg_variance) > 0.15:
                        recommendation = best_alt['venue']

                        # Confidence based on sample sizes
                        if current_claim_count >= 10 and best_alt['sample_size'] >= 10:
                            confidence = 'high'
                        elif current_claim_count >= 5 and best_alt['sample_size'] >= 5:
                            confidence = 'medium'

            # Calculate trend (database-level monthly aggregation)
            monthly_data = session.query(
                func.strftime('%Y-%m', Claim.CLAIMCLOSEDDATE).label('month'),
                func.avg(Claim.variance_pct).label('avg_var'),
                func.count(Claim.CLAIMID).label('count')
            ).filter(
                Claim.CLAIMCLOSEDDATE >= cutoff_date,
                Claim.COUNTYNAME == county_name,
                Claim.VENUERATING == current_venue,
                Claim.PRIMARY_INJURYGROUP_CODE == control_injury if len(controlled_for) > 0 else True
            ).group_by(func.strftime('%Y-%m', Claim.CLAIMCLOSEDDATE)).all()

            trend = 'stable'
            if len(monthly_data) >= 3:
                mid_point = len(monthly_data) // 2
                first_half = [m[1] for m in monthly_data[:mid_point] if m[1] is not None]
                second_half = [m[1] for m in monthly_data[mid_point:] if m[1] is not None]

                if first_half and second_half:
                    first_avg = float(np.mean(first_half))
                    second_avg = float(np.mean(second_half))

                    if abs(second_avg - first_avg) > 2.0:
                        trend = 'improving' if second_avg < first_avg else 'worsening'

            venue_recommendations.append({
                'county': county_name,
                'state': state if state else 'Unknown',
                'current_venue_rating': current_venue,
                'current_avg_variance': round(current_avg_variance, 2),
                'current_claim_count': current_claim_count,
                'recommended_venue_rating': recommendation,
                'potential_variance_reduction': round(potential_improvement, 2) if recommendation else 0,
                'confidence': confidence,
                'trend': trend,
                'isolation_quality': 'high' if current_claim_count >= 10 else 'medium' if current_claim_count >= 5 else 'low',
                'controlled_for': controlled_for
            })

        # Sort by potential improvement (highest first)
        venue_recommendations.sort(key=lambda x: x['potential_variance_reduction'], reverse=True)

        # Calculate summary stats
        total_counties = len(venue_recommendations)
        counties_with_recs = len([r for r in venue_recommendations if r['recommended_venue_rating']])
        avg_variance = np.mean([r['current_avg_variance'] for r in venue_recommendations]) if venue_recommendations else 0

        logger.info(f"✅ Venue shift analysis completed: {counties_with_recs}/{total_counties} counties with recommendations")

        return {
            "recommendations": venue_recommendations,
            "summary": {
                "total_counties_analyzed": total_counties,
                "counties_with_shift_recommendations": counties_with_recs,
                "average_current_variance": round(float(avg_variance), 2),
                "analysis_period_months": months,
                "total_recent_claims": total_recent
            },
            "control_conditions": {
                "most_common_injury": control_injury,
                "most_common_severity": control_severity,
                "most_common_impact": int(control_impact) if control_impact else None
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "analysis_type": "isolated_venue_shift",
                "optimization": "database_level_aggregation_5M_ready",
                "performance": "optimized_for_production"
            }
        }

    except OperationalError as e:
        # Database connection errors - retry logic could be added here
        logger.error(f"Database connection error in venue shift analysis: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable. Please retry in a moment."
        )

    except SQLAlchemyError as e:
        # Database query errors
        logger.error(f"Database query error in venue shift analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database query failed. Please contact support if this persists."
        )

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in venue shift analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Analysis error: {str(e)}"
        )

    finally:
        # Always close session to prevent resource leaks
        if session:
            session.close()
            logger.debug("Database session closed successfully")
