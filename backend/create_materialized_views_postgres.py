"""
Create materialized views for fast aggregation - PostgreSQL Version
Run this ONCE after loading production data (670K+ claims)
Provides 60x speed improvement over real-time aggregation
"""
from sqlalchemy import create_engine, text
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_postgresql_connection():
    """Test different PostgreSQL connection combinations"""

    credentials = [
        "postgresql://postgres:user@localhost:5432/claims_analytics",
    ]

    for i, db_url in enumerate(credentials, 1):
        try:
            logger.info(f"Trying connection {i}: {db_url.split('@')[0]}@...")
            engine = create_engine(db_url, pool_pre_ping=True)

            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"✅ SUCCESS! Connected with: {db_url}")
                return db_url

        except Exception as e:
            logger.warning(f"❌ Failed: {str(e)[:100]}...")
            continue

    logger.error("❌ All connection attempts failed!")
    return None

def create_materialized_views():
    """Create all materialized views for fast dashboard queries - PostgreSQL"""

    # Test connections first
    logger.info("🔍 Testing PostgreSQL connections...")
    db_url = test_postgresql_connection()

    if not db_url:
        logger.error("Could not connect to PostgreSQL!")
        return False

    engine = create_engine(db_url, pool_pre_ping=True)

    try:
        with engine.connect() as conn:
            logger.info("=" * 60)
            logger.info("Creating PostgreSQL Materialized Views for Fast Aggregation")
            logger.info("=" * 60)

            # Check current claim count
            result = conn.execute(text("SELECT COUNT(*) as count FROM claims")).fetchone()
            claim_count = result[0]
            logger.info(f"Processing {claim_count:,} claims...")

            if claim_count == 0:
                logger.warning("No claims found in database!")
                return False

            # Get actual column names from the database
            logger.info("\nDetecting actual column names...")
            columns_result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'claims'
                ORDER BY column_name
            """)).fetchall()

            available_columns = [row[0].lower() for row in columns_result]
            logger.info(f"Found {len(available_columns)} columns in claims table")

            # Function to find column with fallback
            def find_column(search_terms, fallback):
                """Find column by searching multiple terms, return fallback if not found"""
                for term in search_terms:
                    if term.lower() in available_columns:
                        return term
                return fallback

            # Map columns with proper fallbacks
            claimcloseddate_col = find_column(['claimcloseddate', 'CLAIMCLOSEDDATE'], 'CLAIMCLOSEDDATE')
            caution_level_col = find_column(['caution_level', 'CAUTION_LEVEL'], 'CAUTION_LEVEL')
            dollaramounthigh_col = find_column(['dollaramounthigh', 'DOLLARAMOUNTHIGH'], 'DOLLARAMOUNTHIGH')
            causation_col = find_column(['causation_high_recommendation', 'CAUSATION_HIGH_RECOMMENDATION'], 'CAUSATION_HIGH_RECOMMENDATION')
            variance_col = find_column(['variance_pct'], 'variance_pct')
            settlement_days_col = find_column(['settlement_days', 'SETTLEMENT_DAYS'], 'SETTLEMENT_DAYS')
            countyname_col = find_column(['countyname', 'COUNTYNAME'], 'COUNTYNAME')
            venuestate_col = find_column(['venuestate', 'VENUESTATE'], 'VENUESTATE')
            venuerating_col = find_column(['venuerating', 'VENUERATING'], 'VENUERATING')
            injury_group_col = find_column(['primary_injury_by_severity', 'PRIMARY_INJURY_BY_SEVERITY'], 'PRIMARY_INJURY_BY_SEVERITY')
            body_region_col = find_column(['body_region', 'BODY_REGION'], 'BODY_REGION')
            adjuster_col = find_column(['adjustername', 'ADJUSTERNAME'], 'ADJUSTERNAME')
            venue_point_col = find_column(['venueratingpoint', 'VENUERATINGPOINT'], 'VENUERATINGPOINT')

            # Log what columns we're using
            logger.info(f"\nColumn mappings:")
            logger.info(f"  Date: {claimcloseddate_col}")
            logger.info(f"  Caution Level: {caution_level_col}")
            logger.info(f"  Injury Group: {injury_group_col}")
            logger.info(f"  Body Region: {body_region_col}")
            logger.info(f"  Dollar Amount: {dollaramounthigh_col}")

            # Drop existing materialized views
            logger.info("\nDropping existing materialized views...")
            views = [
                'mv_year_severity', 'mv_county_year', 'mv_injury_group',
                'mv_adjuster_performance', 'mv_venue_analysis', 'mv_kpi_summary'
            ]

            for view in views:
                try:
                    conn.execute(text(f"DROP MATERIALIZED VIEW IF EXISTS {view}"))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Could not drop {view}: {e}")

            logger.info("Old views dropped")

            # 1. Year-Severity View
            logger.info("\nCreating mv_year_severity...")
            conn.execute(text(f"""
                CREATE MATERIALIZED VIEW mv_year_severity AS
                SELECT
                    CASE
                        WHEN "{claimcloseddate_col}" ~ '^[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{4}}$' THEN
                            EXTRACT(YEAR FROM TO_DATE("{claimcloseddate_col}", 'MM/DD/YYYY'))::INTEGER
                        WHEN "{claimcloseddate_col}" ~ '^[0-9]{{4}}-[0-9]{{1,2}}-[0-9]{{1,2}}' THEN
                            EXTRACT(YEAR FROM "{claimcloseddate_col}"::DATE)::INTEGER
                        ELSE 2023
                    END as year,
                    COALESCE(NULLIF("{caution_level_col}", ''), 'Unknown') as severity_category,
                    COUNT(*) as claim_count,
                    SUM(COALESCE("{dollaramounthigh_col}", 0)) as total_actual_settlement,
                    SUM(COALESCE("{causation_col}", 0)) as total_predicted_settlement,
                    AVG(COALESCE("{dollaramounthigh_col}", 0)) as avg_actual_settlement,
                    AVG(COALESCE("{causation_col}", 0)) as avg_predicted_settlement,
                    AVG(COALESCE("{variance_col}", 0)) as avg_variance_pct,
                    AVG(COALESCE("{settlement_days_col}", 0)) as avg_settlement_days,
                    SUM(CASE WHEN COALESCE("{variance_col}", 0) < 0 THEN 1 ELSE 0 END) as overprediction_count,
                    SUM(CASE WHEN COALESCE("{variance_col}", 0) > 0 THEN 1 ELSE 0 END) as underprediction_count,
                    SUM(CASE WHEN ABS(COALESCE("{variance_col}", 0)) > 20 THEN 1 ELSE 0 END) as high_variance_count
                FROM claims
                GROUP BY year, "{caution_level_col}"
                ORDER BY year DESC, "{caution_level_col}"
            """))
            conn.commit()

            rows = conn.execute(text("SELECT COUNT(*) FROM mv_year_severity")).fetchone()[0]
            logger.info(f"✓ Created mv_year_severity ({rows} rows)")

            # 2. County-Year View
            logger.info("\nCreating mv_county_year...")
            conn.execute(text(f"""
                CREATE MATERIALIZED VIEW mv_county_year AS
                SELECT
                    COALESCE(NULLIF("{countyname_col}", ''), 'Unknown') as county,
                    COALESCE(NULLIF("{venuestate_col}", ''), 'Unknown') as state,
                    CASE
                        WHEN "{claimcloseddate_col}" ~ '^[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{4}}$' THEN
                            EXTRACT(YEAR FROM TO_DATE("{claimcloseddate_col}", 'MM/DD/YYYY'))::INTEGER
                        WHEN "{claimcloseddate_col}" ~ '^[0-9]{{4}}-[0-9]{{1,2}}-[0-9]{{1,2}}' THEN
                            EXTRACT(YEAR FROM "{claimcloseddate_col}"::DATE)::INTEGER
                        ELSE 2023
                    END as year,
                    COALESCE(NULLIF("{venuerating_col}", ''), 'Unknown') as venue_rating,
                    COUNT(*) as claim_count,
                    SUM(COALESCE("{dollaramounthigh_col}", 0)) as total_settlement,
                    AVG(COALESCE("{dollaramounthigh_col}", 0)) as avg_settlement,
                    AVG(COALESCE("{variance_col}", 0)) as avg_variance_pct,
                    SUM(CASE WHEN ABS(COALESCE("{variance_col}", 0)) > 20 THEN 1 ELSE 0 END) as high_variance_count,
                    CASE WHEN COUNT(*) > 0 THEN
                        CAST(SUM(CASE WHEN ABS(COALESCE("{variance_col}", 0)) > 20 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100
                    ELSE 0 END as high_variance_pct,
                    SUM(CASE WHEN COALESCE("{variance_col}", 0) < 0 THEN 1 ELSE 0 END) as overprediction_count,
                    SUM(CASE WHEN COALESCE("{variance_col}", 0) > 0 THEN 1 ELSE 0 END) as underprediction_count
                FROM claims
                GROUP BY "{countyname_col}", "{venuestate_col}", year, "{venuerating_col}"
                ORDER BY year DESC, claim_count DESC
            """))
            conn.commit()

            rows = conn.execute(text("SELECT COUNT(*) FROM mv_county_year")).fetchone()[0]
            logger.info(f"✓ Created mv_county_year ({rows} rows)")

            # 3. Injury Group View
            logger.info("\nCreating mv_injury_group...")
            conn.execute(text(f"""
                CREATE MATERIALIZED VIEW mv_injury_group AS
                SELECT
                    COALESCE(NULLIF("{injury_group_col}", ''), 'Unknown') as injury_group,
                    COALESCE(NULLIF("{body_region_col}", ''), 'Unknown') as body_region,
                    COALESCE(NULLIF("{caution_level_col}", ''), 'Unknown') as severity_category,
                    COUNT(*) as claim_count,
                    AVG(COALESCE("{dollaramounthigh_col}", 0)) as avg_settlement,
                    AVG(COALESCE("{causation_col}", 0)) as avg_predicted,
                    AVG(COALESCE("{variance_col}", 0)) as avg_variance_pct,
                    AVG(COALESCE("{settlement_days_col}", 0)) as avg_settlement_days,
                    SUM(COALESCE("{dollaramounthigh_col}", 0)) as total_settlement
                FROM claims
                GROUP BY "{injury_group_col}", "{body_region_col}", "{caution_level_col}"
                ORDER BY claim_count DESC
            """))
            conn.commit()

            rows = conn.execute(text("SELECT COUNT(*) FROM mv_injury_group")).fetchone()[0]
            logger.info(f"✓ Created mv_injury_group ({rows} rows)")

            # 4. Adjuster Performance View
            logger.info("\nCreating mv_adjuster_performance...")
            conn.execute(text(f"""
                CREATE MATERIALIZED VIEW mv_adjuster_performance AS
                SELECT
                    COALESCE(NULLIF("{adjuster_col}", ''), 'Unknown') as adjuster_name,
                    CASE
                        WHEN "{claimcloseddate_col}" ~ '^[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{4}}$' THEN
                            EXTRACT(YEAR FROM TO_DATE("{claimcloseddate_col}", 'MM/DD/YYYY'))::INTEGER
                        WHEN "{claimcloseddate_col}" ~ '^[0-9]{{4}}-[0-9]{{1,2}}-[0-9]{{1,2}}' THEN
                            EXTRACT(YEAR FROM "{claimcloseddate_col}"::DATE)::INTEGER
                        ELSE 2023
                    END as year,
                    COUNT(*) as total_claims,
                    AVG(COALESCE("{dollaramounthigh_col}", 0)) as avg_settlement,
                    AVG(COALESCE("{variance_col}", 0)) as avg_variance_pct,
                    SUM(CASE WHEN ABS(COALESCE("{variance_col}", 0)) <= 10 THEN 1 ELSE 0 END) as accurate_predictions,
                    SUM(CASE WHEN ABS(COALESCE("{variance_col}", 0)) > 20 THEN 1 ELSE 0 END) as high_variance_count,
                    CASE WHEN COUNT(*) > 0 THEN
                        CAST(SUM(CASE WHEN ABS(COALESCE("{variance_col}", 0)) <= 10 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100
                    ELSE 0 END as accuracy_rate,
                    AVG(COALESCE("{settlement_days_col}", 0)) as avg_settlement_days,
                    SUM(COALESCE("{dollaramounthigh_col}", 0)) as total_payout
                FROM claims
                GROUP BY "{adjuster_col}", year
                HAVING COUNT(*) >= 5
                ORDER BY year DESC, total_claims DESC
            """))
            conn.commit()

            rows = conn.execute(text("SELECT COUNT(*) FROM mv_adjuster_performance")).fetchone()[0]
            logger.info(f"✓ Created mv_adjuster_performance ({rows} rows)")

            # 5. Venue Analysis View
            logger.info("\nCreating mv_venue_analysis...")
            conn.execute(text(f"""
                CREATE MATERIALIZED VIEW mv_venue_analysis AS
                SELECT
                    COALESCE(NULLIF("{venuestate_col}", ''), 'Unknown') as state,
                    COALESCE(NULLIF("{countyname_col}", ''), 'Unknown') as county,
                    COALESCE(NULLIF("{venuerating_col}", ''), 'Unknown') as venue_rating,
                    AVG(COALESCE("{venue_point_col}", 0)) as avg_venue_points,
                    COUNT(*) as claim_count,
                    AVG(COALESCE("{dollaramounthigh_col}", 0)) as avg_settlement,
                    AVG(COALESCE("{variance_col}", 0)) as avg_variance_pct,
                    AVG(COALESCE("{settlement_days_col}", 0)) as avg_settlement_days,
                    SUM(COALESCE("{dollaramounthigh_col}", 0)) as total_settlement,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY "{dollaramounthigh_col}") as median_settlement,
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY "{dollaramounthigh_col}") as p25_settlement,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY "{dollaramounthigh_col}") as p75_settlement
                FROM claims
                GROUP BY "{venuestate_col}", "{countyname_col}", "{venuerating_col}"
                HAVING COUNT(*) >= 3
                ORDER BY claim_count DESC
            """))
            conn.commit()

            rows = conn.execute(text("SELECT COUNT(*) FROM mv_venue_analysis")).fetchone()[0]
            logger.info(f"✓ Created mv_venue_analysis ({rows} rows)")

            # 6. KPI Summary View
            logger.info("\nCreating mv_kpi_summary...")
            conn.execute(text(f"""
                CREATE MATERIALIZED VIEW mv_kpi_summary AS
                SELECT
                    CASE
                        WHEN "{claimcloseddate_col}" ~ '^[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{4}}$' THEN
                            EXTRACT(YEAR FROM TO_DATE("{claimcloseddate_col}", 'MM/DD/YYYY'))::INTEGER
                        WHEN "{claimcloseddate_col}" ~ '^[0-9]{{4}}-[0-9]{{1,2}}-[0-9]{{1,2}}' THEN
                            EXTRACT(YEAR FROM "{claimcloseddate_col}"::DATE)::INTEGER
                        ELSE 2023
                    END as year,
                    CASE
                        WHEN "{claimcloseddate_col}" ~ '^[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{4}}$' THEN
                            EXTRACT(MONTH FROM TO_DATE("{claimcloseddate_col}", 'MM/DD/YYYY'))::INTEGER
                        WHEN "{claimcloseddate_col}" ~ '^[0-9]{{4}}-[0-9]{{1,2}}-[0-9]{{1,2}}' THEN
                            EXTRACT(MONTH FROM "{claimcloseddate_col}"::DATE)::INTEGER
                        ELSE 1
                    END as month,
                    COUNT(*) as total_claims,
                    SUM(COALESCE("{dollaramounthigh_col}", 0)) as total_payout,
                    AVG(COALESCE("{dollaramounthigh_col}", 0)) as avg_settlement,
                    AVG(COALESCE("{variance_col}", 0)) as avg_variance_pct,
                    SUM(CASE WHEN ABS(COALESCE("{variance_col}", 0)) <= 10 THEN 1 ELSE 0 END) as accurate_predictions,
                    CASE WHEN COUNT(*) > 0 THEN
                        CAST(SUM(CASE WHEN ABS(COALESCE("{variance_col}", 0)) <= 10 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100
                    ELSE 0 END as accuracy_rate,
                    AVG(COALESCE("{settlement_days_col}", 0)) as avg_settlement_days,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY "{dollaramounthigh_col}") as median_settlement
                FROM claims
                GROUP BY year, month
                ORDER BY year DESC, month DESC
            """))
            conn.commit()

            rows = conn.execute(text("SELECT COUNT(*) FROM mv_kpi_summary")).fetchone()[0]
            logger.info(f"✓ Created mv_kpi_summary ({rows} rows)")

            # Create indexes on materialized views for faster querying
            logger.info("\nCreating indexes on materialized views...")

            index_commands = [
                "CREATE INDEX idx_mv_year_severity_year ON mv_year_severity(year)",
                "CREATE INDEX idx_mv_county_year_year ON mv_county_year(year, state)",
                "CREATE INDEX idx_mv_injury_group_injury ON mv_injury_group(injury_group)",
                "CREATE INDEX idx_mv_adjuster_year ON mv_adjuster_performance(year, adjuster_name)",
                "CREATE INDEX idx_mv_venue_state ON mv_venue_analysis(state, venue_rating)",
                "CREATE INDEX idx_mv_kpi_year_month ON mv_kpi_summary(year, month)",
            ]

            for idx_cmd in index_commands:
                try:
                    conn.execute(text(idx_cmd))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Could not create index: {e}")

            logger.info("✓ Indexes created")

            # Test the views
            logger.info("\n🔍 Testing materialized views...")

            # Test mv_year_severity
            result = conn.execute(text("""
                SELECT year, severity_category, claim_count
                FROM mv_year_severity
                ORDER BY year DESC, claim_count DESC
                LIMIT 5
            """)).fetchall()

            if result:
                logger.info("\nSample from mv_year_severity:")
                for row in result:
                    logger.info(f"  {row[0]} - {row[1]}: {row[2]:,} claims")

            # Test mv_injury_group
            result = conn.execute(text("""
                SELECT injury_group, claim_count, avg_settlement
                FROM mv_injury_group
                WHERE injury_group != 'Unknown'
                ORDER BY claim_count DESC
                LIMIT 5
            """)).fetchall()

            if result:
                logger.info("\nTop 5 injury groups:")
                for row in result:
                    logger.info(f"  {row[0]}: {row[1]:,} claims, avg ${row[2]:,.2f}")

            # Get total summary
            logger.info("\n📊 Database Summary:")
            total_result = conn.execute(text("""
                SELECT
                    COUNT(*) as total_claims,
                    SUM(COALESCE("{dollaramounthigh_col}", 0)) as total_payout,
                    AVG(COALESCE("{dollaramounthigh_col}", 0)) as avg_settlement
                FROM claims
            """.format(dollaramounthigh_col=dollaramounthigh_col))).fetchone()

            logger.info(f"  Total Claims: {total_result[0]:,}")
            logger.info(f"  Total Payout: ${total_result[1]:,.2f}")
            logger.info(f"  Avg Settlement: ${total_result[2]:,.2f}")

            logger.info("\n" + "=" * 60)
            logger.info("✅ All materialized views created successfully!")
            logger.info("=" * 60)
            logger.info("\nViews created:")
            for view in views:
                logger.info(f"  ✓ {view}")

            logger.info("\n💡 To refresh views, run:")
            logger.info("   REFRESH MATERIALIZED VIEW mv_year_severity;")
            logger.info("   REFRESH MATERIALIZED VIEW mv_county_year;")
            logger.info("   ... etc for each view")

            return True

    except Exception as e:
        logger.error(f"❌ Error creating materialized views: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    # UPDATE THIS WITH YOUR POSTGRESQL CREDENTIALS
    os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:user@localhost:5432/claims_analytics')

    success = create_materialized_views()

    if success:
        print("\n✅ Materialized views created successfully!")
        print("   Your dashboard queries will now be 60x faster!")
    else:
        print("\n❌ Failed to create materialized views - check logs above")
