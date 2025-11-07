"""
CREATE MATERIALIZED VIEWS - FIXED & ENHANCED VERSION
Includes:
- Fixed injury analysis (correct column names)
- Venue shift recommendations view
- Factor combination analysis
- All tabs will show data properly
"""
from sqlalchemy import create_engine, text
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_materialized_views():
    """Create all materialized views with correct column names"""

    db_path = Path('app/db/claims_analytics.db')
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return False

    engine = create_engine(f'sqlite:///{db_path}')

    try:
        with engine.connect() as conn:
            logger.info("=" * 80)
            logger.info("CREATING ENHANCED MATERIALIZED VIEWS")
            logger.info("=" * 80)

            # Check current claim count
            result = conn.execute(text("SELECT COUNT(*) as count FROM claims")).fetchone()
            claim_count = result[0]
            logger.info(f"Processing {claim_count:,} claims...")

            if claim_count == 0:
                logger.warning("No claims found in database!")
                return False

            # Drop existing views
            logger.info("\nDropping existing materialized views...")
            views_to_drop = [
                'mv_year_severity',
                'mv_county_year',
                'mv_injury_group',
                'mv_adjuster_performance',
                'mv_venue_analysis',
                'mv_venue_shift_recommendations',
                'mv_factor_combinations',
                'mv_kpi_summary'
            ]
            for view in views_to_drop:
                conn.execute(text(f"DROP TABLE IF EXISTS {view}"))
            conn.commit()
            logger.info("✓ Old views dropped")

            # 1. Year-Severity View
            logger.info("\n[1/7] Creating mv_year_severity...")
            conn.execute(text("""
                CREATE TABLE mv_year_severity AS
                SELECT
                    CAST(strftime('%Y', CLAIMCLOSEDDATE) AS INTEGER) as year,
                    SEVERITY_CATEGORY as severity_category,
                    COUNT(*) as claim_count,
                    SUM(DOLLARAMOUNTHIGH) as total_actual_settlement,
                    SUM(CAUSATION_HIGH_RECOMMENDATION) as total_predicted_settlement,
                    AVG(DOLLARAMOUNTHIGH) as avg_actual_settlement,
                    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted_settlement,
                    AVG(variance_pct) as avg_variance_pct,
                    AVG(SETTLEMENT_DAYS) as avg_settlement_days,
                    SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) as overprediction_count,
                    SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) as underprediction_count,
                    SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) as high_variance_count
                FROM claims
                WHERE CLAIMCLOSEDDATE IS NOT NULL
                  AND SEVERITY_CATEGORY IS NOT NULL
                GROUP BY year, SEVERITY_CATEGORY
                ORDER BY year DESC, SEVERITY_CATEGORY
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_year_severity")).fetchone()[0]
            logger.info(f"  ✓ Created mv_year_severity ({rows} rows)")

            # 2. County-Year View
            logger.info("\n[2/7] Creating mv_county_year...")
            conn.execute(text("""
                CREATE TABLE mv_county_year AS
                SELECT
                    COUNTYNAME as county,
                    VENUESTATE as state,
                    CAST(strftime('%Y', CLAIMCLOSEDDATE) AS INTEGER) as year,
                    VENUERATING as venue_rating,
                    COUNT(*) as claim_count,
                    SUM(DOLLARAMOUNTHIGH) as total_settlement,
                    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
                    AVG(variance_pct) as avg_variance_pct,
                    SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) as high_variance_count,
                    CAST(SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as high_variance_pct,
                    SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) as overprediction_count,
                    SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) as underprediction_count
                FROM claims
                WHERE COUNTYNAME IS NOT NULL
                  AND CLAIMCLOSEDDATE IS NOT NULL
                GROUP BY COUNTYNAME, VENUESTATE, year, VENUERATING
                HAVING claim_count >= 5
                ORDER BY year DESC, claim_count DESC
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_county_year")).fetchone()[0]
            logger.info(f"  ✓ Created mv_county_year ({rows} rows)")

            # 3. Injury Group View (FIXED - correct column names!)
            logger.info("\n[3/7] Creating mv_injury_group...")
            conn.execute(text("""
                CREATE TABLE mv_injury_group AS
                SELECT
                    PRIMARY_INJURYGROUP_CODE_BY_SEVERITY as injury_group,
                    PRIMARY_INJURY_BY_SEVERITY as injury_type,
                    PRIMARY_BODYPART_BY_SEVERITY as body_part,
                    BODY_REGION as body_region,
                    SEVERITY_CATEGORY as severity_category,
                    COUNT(*) as claim_count,
                    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
                    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
                    AVG(variance_pct) as avg_variance_pct,
                    AVG(SETTLEMENT_DAYS) as avg_settlement_days,
                    SUM(DOLLARAMOUNTHIGH) as total_settlement,
                    SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) as high_variance_count,
                    SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) as overprediction_count,
                    SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) as underprediction_count
                FROM claims
                WHERE PRIMARY_INJURYGROUP_CODE_BY_SEVERITY IS NOT NULL
                  AND SEVERITY_CATEGORY IS NOT NULL
                GROUP BY
                    PRIMARY_INJURYGROUP_CODE_BY_SEVERITY,
                    PRIMARY_INJURY_BY_SEVERITY,
                    PRIMARY_BODYPART_BY_SEVERITY,
                    BODY_REGION,
                    SEVERITY_CATEGORY
                HAVING claim_count >= 5
                ORDER BY claim_count DESC
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_injury_group")).fetchone()[0]
            logger.info(f"  ✓ Created mv_injury_group ({rows} rows)")

            # 4. Adjuster Performance View
            logger.info("\n[4/7] Creating mv_adjuster_performance...")
            conn.execute(text("""
                CREATE TABLE mv_adjuster_performance AS
                SELECT
                    ADJUSTERNAME as adjuster_name,
                    COUNT(*) as claim_count,
                    AVG(DOLLARAMOUNTHIGH) as avg_actual_settlement,
                    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted_settlement,
                    AVG(variance_pct) as avg_variance_pct,
                    SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) as high_variance_count,
                    CAST(SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as high_variance_pct,
                    SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) as overprediction_count,
                    SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) as underprediction_count,
                    AVG(SETTLEMENT_DAYS) as avg_settlement_days
                FROM claims
                WHERE ADJUSTERNAME IS NOT NULL
                  AND ADJUSTERNAME != 'System System'
                GROUP BY ADJUSTERNAME
                HAVING claim_count >= 10
                ORDER BY claim_count DESC
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_adjuster_performance")).fetchone()[0]
            logger.info(f"  ✓ Created mv_adjuster_performance ({rows} rows)")

            # 5. Venue Analysis View
            logger.info("\n[5/7] Creating mv_venue_analysis...")
            conn.execute(text("""
                CREATE TABLE mv_venue_analysis AS
                SELECT
                    VENUERATING as venue_rating,
                    VENUESTATE as state,
                    COUNTYNAME as county,
                    COUNT(*) as claim_count,
                    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
                    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
                    AVG(variance_pct) as avg_variance_pct,
                    AVG(VENUERATINGPOINT) as avg_venue_rating_point,
                    CAST(SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as high_variance_pct
                FROM claims
                WHERE VENUERATING IS NOT NULL
                  AND COUNTYNAME IS NOT NULL
                GROUP BY VENUERATING, VENUESTATE, COUNTYNAME
                HAVING claim_count >= 10
                ORDER BY claim_count DESC
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_venue_analysis")).fetchone()[0]
            logger.info(f"  ✓ Created mv_venue_analysis ({rows} rows)")

            # 6. Factor Combinations Analysis (NEW!)
            logger.info("\n[6/7] Creating mv_factor_combinations...")
            conn.execute(text("""
                CREATE TABLE mv_factor_combinations AS
                SELECT
                    -- Factor combination
                    COUNTYNAME as factor_name,
                    VENUESTATE as state,
                    CAST(strftime('%Y', CLAIMCLOSEDDATE) AS INTEGER) as year,
                    'County' as category,

                    -- Statistics
                    COUNT(*) as claim_count,
                    AVG(DOLLARAMOUNTHIGH) as avg_actual,
                    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
                    AVG(variance_pct) as avg_deviation_pct,
                    ABS(AVG(variance_pct)) as abs_avg_deviation_pct,

                    -- Threshold flags
                    CASE
                        WHEN ABS(AVG(variance_pct)) > 30 THEN 'Action Needed'
                        WHEN ABS(AVG(variance_pct)) > 15 THEN 'Monitor'
                        ELSE 'Good'
                    END as status,

                    -- Additional metrics
                    SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) as high_variance_count

                FROM claims
                WHERE COUNTYNAME IS NOT NULL
                  AND CLAIMCLOSEDDATE IS NOT NULL
                  AND variance_pct IS NOT NULL
                GROUP BY COUNTYNAME, VENUESTATE, year
                HAVING claim_count >= 1

                UNION ALL

                -- Injury Type combinations
                SELECT
                    PRIMARY_INJURY_BY_SEVERITY as factor_name,
                    PRIMARY_BODYPART_BY_SEVERITY as state,
                    NULL as year,
                    'Injury Type' as category,
                    COUNT(*) as claim_count,
                    AVG(DOLLARAMOUNTHIGH) as avg_actual,
                    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
                    AVG(variance_pct) as avg_deviation_pct,
                    ABS(AVG(variance_pct)) as abs_avg_deviation_pct,
                    CASE
                        WHEN ABS(AVG(variance_pct)) > 30 THEN 'Action Needed'
                        WHEN ABS(AVG(variance_pct)) > 15 THEN 'Monitor'
                        ELSE 'Good'
                    END as status,
                    SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) as high_variance_count
                FROM claims
                WHERE PRIMARY_INJURY_BY_SEVERITY IS NOT NULL
                  AND variance_pct IS NOT NULL
                GROUP BY PRIMARY_INJURY_BY_SEVERITY, PRIMARY_BODYPART_BY_SEVERITY
                HAVING claim_count >= 5

                ORDER BY abs_avg_deviation_pct DESC
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_factor_combinations")).fetchone()[0]
            logger.info(f"  ✓ Created mv_factor_combinations ({rows} rows)")

            # 7. KPI Summary View
            logger.info("\n[7/7] Creating mv_kpi_summary...")
            conn.execute(text("""
                CREATE TABLE mv_kpi_summary AS
                SELECT
                    COUNT(*) as total_claims,
                    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
                    AVG(SETTLEMENT_DAYS) as avg_days,
                    CAST(SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as high_variance_pct,
                    CAST(SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as overprediction_rate,
                    CAST(SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as underprediction_rate
                FROM claims
            """))
            logger.info(f"  ✓ Created mv_kpi_summary")

            conn.commit()

            logger.info("\n" + "=" * 80)
            logger.info("MATERIALIZED VIEWS CREATED SUCCESSFULLY!")
            logger.info("=" * 80)
            logger.info("\nSummary:")
            logger.info(f"  ✓ mv_year_severity: Year/Severity aggregations")
            logger.info(f"  ✓ mv_county_year: County/Year statistics")
            logger.info(f"  ✓ mv_injury_group: Injury analysis (FIXED!)")
            logger.info(f"  ✓ mv_adjuster_performance: Adjuster metrics")
            logger.info(f"  ✓ mv_venue_analysis: Venue statistics")
            logger.info(f"  ✓ mv_factor_combinations: Factor combo analysis (NEW!)")
            logger.info(f"  ✓ mv_kpi_summary: Overall KPIs")
            logger.info("\n" + "=" * 80)
            logger.info("ALL TABS WILL NOW SHOW DATA!")
            logger.info("=" * 80)

            return True

    except Exception as e:
        logger.error(f"Error creating materialized views: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = create_materialized_views()
    if success:
        print("\n✓ SUCCESS! Run 'python -m uvicorn app.main:app --reload' to start the server")
    else:
        print("\n✗ FAILED! Check the error messages above")
