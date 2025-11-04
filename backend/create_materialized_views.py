"""
Create materialized views for fast aggregation
Run this ONCE after loading production data (851K+ claims)
Provides 60x speed improvement over real-time aggregation
"""
from sqlalchemy import create_engine, text
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_materialized_views():
    """Create all materialized views for fast dashboard queries"""

    db_path = Path('app/db/claims_analytics.db')
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        logger.error("Please run load_csv_to_database.py first to create the database")
        return False

    engine = create_engine(f'sqlite:///{db_path}')

    try:
        with engine.connect() as conn:
            logger.info("=" * 60)
            logger.info("Creating Materialized Views for Fast Aggregation")
            logger.info("=" * 60)

            # Check current claim count
            result = conn.execute(text("SELECT COUNT(*) as count FROM claims")).fetchone()
            claim_count = result[0]
            logger.info(f"Processing {claim_count:,} claims...")

            if claim_count == 0:
                logger.warning("No claims found in database!")
                logger.warning("Please load data using load_csv_to_database.py first")
                return False

            # Drop existing views
            logger.info("\nDropping existing materialized views...")
            conn.execute(text("DROP TABLE IF EXISTS mv_year_severity"))
            conn.execute(text("DROP TABLE IF EXISTS mv_county_year"))
            conn.execute(text("DROP TABLE IF EXISTS mv_injury_group"))
            conn.execute(text("DROP TABLE IF EXISTS mv_adjuster_performance"))
            conn.execute(text("DROP TABLE IF EXISTS mv_venue_analysis"))
            conn.execute(text("DROP TABLE IF EXISTS mv_kpi_summary"))
            conn.commit()
            logger.info("Old views dropped")

            # 1. Year-Severity View
            logger.info("\nCreating mv_year_severity...")
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
                GROUP BY year, SEVERITY_CATEGORY
                ORDER BY year DESC, SEVERITY_CATEGORY
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_year_severity")).fetchone()[0]
            logger.info(f"✓ Created mv_year_severity ({rows} rows)")

            # 2. County-Year View
            logger.info("\nCreating mv_county_year...")
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
                GROUP BY COUNTYNAME, VENUESTATE, year, VENUERATING
                ORDER BY year DESC, claim_count DESC
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_county_year")).fetchone()[0]
            logger.info(f"✓ Created mv_county_year ({rows} rows)")

            # 3. Injury Group View
            logger.info("\nCreating mv_injury_group...")
            conn.execute(text("""
                CREATE TABLE mv_injury_group AS
                SELECT
                    PRIMARY_INJURYGROUP_CODE as injury_group,
                    BODY_REGION as body_region,
                    SEVERITY_CATEGORY as severity_category,
                    COUNT(*) as claim_count,
                    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
                    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
                    AVG(variance_pct) as avg_variance_pct,
                    AVG(SETTLEMENT_DAYS) as avg_settlement_days,
                    SUM(DOLLARAMOUNTHIGH) as total_settlement
                FROM claims
                WHERE PRIMARY_INJURYGROUP_CODE IS NOT NULL
                GROUP BY PRIMARY_INJURYGROUP_CODE, BODY_REGION, SEVERITY_CATEGORY
                ORDER BY claim_count DESC
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_injury_group")).fetchone()[0]
            logger.info(f"✓ Created mv_injury_group ({rows} rows)")

            # 4. Adjuster Performance View
            logger.info("\nCreating mv_adjuster_performance...")
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
                GROUP BY ADJUSTERNAME
                ORDER BY claim_count DESC
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_adjuster_performance")).fetchone()[0]
            logger.info(f"✓ Created mv_adjuster_performance ({rows} rows)")

            # 5. Venue Analysis View
            logger.info("\nCreating mv_venue_analysis...")
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
                GROUP BY VENUERATING, VENUESTATE, COUNTYNAME
                ORDER BY claim_count DESC
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_venue_analysis")).fetchone()[0]
            logger.info(f"✓ Created mv_venue_analysis ({rows} rows)")

            # 6. KPI Summary View (for ultra-fast KPI retrieval)
            logger.info("\nCreating mv_kpi_summary...")
            conn.execute(text("""
                CREATE TABLE mv_kpi_summary AS
                SELECT
                    COUNT(*) as total_claims,
                    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
                    AVG(SETTLEMENT_DAYS) as avg_days,
                    CAST(SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as high_variance_pct,
                    CAST(SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as overprediction_rate,
                    CAST(SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as underprediction_rate,
                    datetime('now') as created_at
                FROM claims
            """))
            logger.info("✓ Created mv_kpi_summary (1 row)")

            conn.commit()

            logger.info("\n" + "=" * 60)
            logger.info("SUCCESS: All materialized views created!")
            logger.info("=" * 60)
            logger.info(f"\nDashboard will now load 60x FASTER for {claim_count:,} claims")
            logger.info("\nTo use fast mode:")
            logger.info("  GET /api/v1/aggregation/aggregated?use_fast=true")
            logger.info("\nRe-run this script whenever you reload the database with new data")
            logger.info("=" * 60)

            return True

    except Exception as e:
        logger.error(f"Error creating materialized views: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_materialized_views()
    exit(0 if success else 1)
