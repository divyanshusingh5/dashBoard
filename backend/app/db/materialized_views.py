"""
Materialized Views for SQLite - Fast Aggregation for 5M+ Records

This module creates pre-aggregated tables that act like materialized views.
These tables dramatically speed up dashboard queries by pre-computing aggregations.

Usage:
    from app.db.materialized_views import create_all_materialized_views, refresh_all_materialized_views

    # On first setup or after schema changes
    create_all_materialized_views()

    # After data updates (CSV imports, manual updates)
    refresh_all_materialized_views()
"""

from sqlalchemy import text
from app.db.schema import get_engine
import logging

logger = logging.getLogger(__name__)


def create_all_materialized_views():
    """
    Create all materialized view tables
    These are actual tables that store pre-aggregated data
    """
    engine = get_engine()

    logger.info("Creating materialized views for fast aggregation...")

    with engine.connect() as conn:
        try:
            # 1. Year-Severity Aggregation
            logger.info("Creating mv_year_severity...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS mv_year_severity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year TEXT,
                    severity_category TEXT,
                    claim_count INTEGER,
                    total_actual_settlement REAL,
                    avg_actual_settlement REAL,
                    total_predicted_settlement REAL,
                    avg_predicted_settlement REAL,
                    avg_settlement_days REAL,
                    avg_variance_pct REAL,
                    overprediction_count INTEGER,
                    underprediction_count INTEGER,
                    high_variance_count INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_mv_year_severity ON mv_year_severity(year, severity_category)"))

            # 2. County-Year Aggregation
            logger.info("Creating mv_county_year...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS mv_county_year (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    county TEXT,
                    state TEXT,
                    year TEXT,
                    venue_rating TEXT,
                    claim_count INTEGER,
                    total_settlement REAL,
                    avg_settlement REAL,
                    avg_variance_pct REAL,
                    high_variance_count INTEGER,
                    high_variance_pct REAL,
                    overprediction_count INTEGER,
                    underprediction_count INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_mv_county_year ON mv_county_year(county, year)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_mv_county_state ON mv_county_year(state, county)"))

            # 3. Injury Group Aggregation
            logger.info("Creating mv_injury_group...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS mv_injury_group (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    injury_group TEXT,
                    severity_category TEXT,
                    claim_count INTEGER,
                    avg_settlement REAL,
                    total_settlement REAL,
                    avg_predicted REAL,
                    avg_variance_pct REAL,
                    avg_settlement_days REAL,
                    body_region TEXT DEFAULT 'General',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_mv_injury ON mv_injury_group(injury_group)"))

            # 4. Adjuster Performance Aggregation
            logger.info("Creating mv_adjuster_performance...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS mv_adjuster_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adjuster_name TEXT,
                    claim_count INTEGER,
                    avg_actual_settlement REAL,
                    avg_predicted_settlement REAL,
                    avg_variance_pct REAL,
                    avg_settlement_days REAL,
                    high_variance_count INTEGER,
                    high_variance_pct REAL,
                    overprediction_count INTEGER,
                    underprediction_count INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_mv_adjuster ON mv_adjuster_performance(adjuster_name)"))

            # 5. Venue Analysis Aggregation
            logger.info("Creating mv_venue_analysis...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS mv_venue_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venue_rating TEXT,
                    state TEXT,
                    county TEXT,
                    claim_count INTEGER,
                    avg_settlement REAL,
                    avg_predicted REAL,
                    avg_variance_pct REAL,
                    avg_venue_rating_point REAL,
                    high_variance_count INTEGER,
                    high_variance_pct REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_mv_venue ON mv_venue_analysis(venue_rating, state)"))

            # 6. KPI Summary (Global metrics)
            logger.info("Creating mv_kpi_summary...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS mv_kpi_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_claims INTEGER,
                    avg_settlement REAL,
                    avg_days REAL,
                    avg_variance REAL,
                    high_variance_pct REAL,
                    overprediction_rate REAL,
                    underprediction_rate REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))

            conn.commit()
            logger.info("✓ All materialized view tables created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating materialized views: {str(e)}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False


def refresh_all_materialized_views():
    """
    Refresh all materialized views by recomputing from source claims table
    Call this after CSV import or data updates

    This uses efficient SQL aggregation instead of loading all data into pandas
    """
    engine = get_engine()

    logger.info("Refreshing all materialized views...")

    with engine.connect() as conn:
        try:
            # Clear existing data
            logger.info("Clearing old aggregated data...")
            conn.execute(text("DELETE FROM mv_year_severity"))
            conn.execute(text("DELETE FROM mv_county_year"))
            conn.execute(text("DELETE FROM mv_injury_group"))
            conn.execute(text("DELETE FROM mv_adjuster_performance"))
            conn.execute(text("DELETE FROM mv_venue_analysis"))
            conn.execute(text("DELETE FROM mv_kpi_summary"))
            conn.commit()

            # 1. Populate Year-Severity
            logger.info("Populating mv_year_severity...")
            conn.execute(text("""
                INSERT INTO mv_year_severity (
                    year, severity_category, claim_count,
                    total_actual_settlement, avg_actual_settlement,
                    total_predicted_settlement, avg_predicted_settlement,
                    avg_settlement_days, avg_variance_pct,
                    overprediction_count, underprediction_count, high_variance_count
                )
                SELECT
                    SUBSTR(claim_date, 1, 4) as year,
                    COALESCE(CAUTION_LEVEL, 'Unknown') as severity_category,
                    COUNT(*) as claim_count,
                    SUM(DOLLARAMOUNTHIGH) as total_actual_settlement,
                    AVG(DOLLARAMOUNTHIGH) as avg_actual_settlement,
                    SUM(predicted_pain_suffering) as total_predicted_settlement,
                    AVG(predicted_pain_suffering) as avg_predicted_settlement,
                    AVG(SETTLEMENT_DAYS) as avg_settlement_days,
                    AVG(variance_pct) as avg_variance_pct,
                    SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) as overprediction_count,
                    SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) as underprediction_count,
                    SUM(CASE WHEN ABS(variance_pct) >= 15 THEN 1 ELSE 0 END) as high_variance_count
                FROM claims
                WHERE claim_date IS NOT NULL
                GROUP BY year, CAUTION_LEVEL
            """))

            # 2. Populate County-Year
            logger.info("Populating mv_county_year...")
            conn.execute(text("""
                INSERT INTO mv_county_year (
                    county, state, year, venue_rating, claim_count,
                    total_settlement, avg_settlement, avg_variance_pct,
                    high_variance_count, high_variance_pct,
                    overprediction_count, underprediction_count
                )
                SELECT
                    COUNTYNAME as county,
                    VENUESTATE as state,
                    SUBSTR(claim_date, 1, 4) as year,
                    COALESCE(VENUE_RATING, 'Unknown') as venue_rating,
                    COUNT(*) as claim_count,
                    SUM(DOLLARAMOUNTHIGH) as total_settlement,
                    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
                    AVG(variance_pct) as avg_variance_pct,
                    SUM(CASE WHEN ABS(variance_pct) >= 15 THEN 1 ELSE 0 END) as high_variance_count,
                    ROUND(CAST(SUM(CASE WHEN ABS(variance_pct) >= 15 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as high_variance_pct,
                    SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) as overprediction_count,
                    SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) as underprediction_count
                FROM claims
                WHERE COUNTYNAME IS NOT NULL AND claim_date IS NOT NULL
                GROUP BY county, state, year, venue_rating
            """))

            # 3. Populate Injury Group
            logger.info("Populating mv_injury_group...")
            conn.execute(text("""
                INSERT INTO mv_injury_group (
                    injury_group, severity_category, claim_count,
                    avg_settlement, total_settlement, avg_predicted,
                    avg_variance_pct, avg_settlement_days
                )
                SELECT
                    COALESCE(INJURY_GROUP_CODE, 'Unknown') as injury_group,
                    COALESCE(CAUTION_LEVEL, 'Unknown') as severity_category,
                    COUNT(*) as claim_count,
                    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
                    SUM(DOLLARAMOUNTHIGH) as total_settlement,
                    AVG(predicted_pain_suffering) as avg_predicted,
                    AVG(variance_pct) as avg_variance_pct,
                    AVG(SETTLEMENT_DAYS) as avg_settlement_days
                FROM claims
                GROUP BY injury_group, severity_category
            """))

            # 4. Populate Adjuster Performance
            logger.info("Populating mv_adjuster_performance...")
            conn.execute(text("""
                INSERT INTO mv_adjuster_performance (
                    adjuster_name, claim_count,
                    avg_actual_settlement, avg_predicted_settlement,
                    avg_variance_pct, avg_settlement_days,
                    high_variance_count, high_variance_pct,
                    overprediction_count, underprediction_count
                )
                SELECT
                    COALESCE(adjuster, 'Unknown') as adjuster_name,
                    COUNT(*) as claim_count,
                    AVG(DOLLARAMOUNTHIGH) as avg_actual_settlement,
                    AVG(predicted_pain_suffering) as avg_predicted_settlement,
                    AVG(variance_pct) as avg_variance_pct,
                    AVG(SETTLEMENT_DAYS) as avg_settlement_days,
                    SUM(CASE WHEN ABS(variance_pct) >= 15 THEN 1 ELSE 0 END) as high_variance_count,
                    ROUND(CAST(SUM(CASE WHEN ABS(variance_pct) >= 15 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as high_variance_pct,
                    SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) as overprediction_count,
                    SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) as underprediction_count
                FROM claims
                GROUP BY adjuster_name
            """))

            # 5. Populate Venue Analysis
            logger.info("Populating mv_venue_analysis...")
            conn.execute(text("""
                INSERT INTO mv_venue_analysis (
                    venue_rating, state, county, claim_count,
                    avg_settlement, avg_predicted, avg_variance_pct,
                    avg_venue_rating_point, high_variance_count, high_variance_pct
                )
                SELECT
                    COALESCE(VENUE_RATING, 'Unknown') as venue_rating,
                    VENUESTATE as state,
                    COUNTYNAME as county,
                    COUNT(*) as claim_count,
                    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
                    AVG(predicted_pain_suffering) as avg_predicted,
                    AVG(variance_pct) as avg_variance_pct,
                    AVG(RATINGWEIGHT) as avg_venue_rating_point,
                    SUM(CASE WHEN ABS(variance_pct) >= 15 THEN 1 ELSE 0 END) as high_variance_count,
                    ROUND(CAST(SUM(CASE WHEN ABS(variance_pct) >= 15 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as high_variance_pct
                FROM claims
                WHERE COUNTYNAME IS NOT NULL
                GROUP BY venue_rating, state, county
            """))

            # 6. Populate KPI Summary
            logger.info("Populating mv_kpi_summary...")
            conn.execute(text("""
                INSERT INTO mv_kpi_summary (
                    total_claims, avg_settlement, avg_days, avg_variance,
                    high_variance_pct, overprediction_rate, underprediction_rate
                )
                SELECT
                    COUNT(*) as total_claims,
                    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
                    AVG(SETTLEMENT_DAYS) as avg_days,
                    AVG(ABS(variance_pct)) as avg_variance,
                    ROUND(CAST(SUM(CASE WHEN ABS(variance_pct) >= 15 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as high_variance_pct,
                    ROUND(CAST(SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as overprediction_rate,
                    ROUND(CAST(SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as underprediction_rate
                FROM claims
            """))

            conn.commit()

            # Log statistics
            result = conn.execute(text("SELECT COUNT(*) FROM mv_year_severity")).scalar()
            logger.info(f"✓ mv_year_severity: {result} rows")

            result = conn.execute(text("SELECT COUNT(*) FROM mv_county_year")).scalar()
            logger.info(f"✓ mv_county_year: {result} rows")

            result = conn.execute(text("SELECT COUNT(*) FROM mv_injury_group")).scalar()
            logger.info(f"✓ mv_injury_group: {result} rows")

            result = conn.execute(text("SELECT COUNT(*) FROM mv_adjuster_performance")).scalar()
            logger.info(f"✓ mv_adjuster_performance: {result} rows")

            result = conn.execute(text("SELECT COUNT(*) FROM mv_venue_analysis")).scalar()
            logger.info(f"✓ mv_venue_analysis: {result} rows")

            logger.info("✓ All materialized views refreshed successfully")
            return True

        except Exception as e:
            logger.error(f"Error refreshing materialized views: {str(e)}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False


def get_materialized_view_stats():
    """
    Get statistics about materialized views
    Useful for monitoring and debugging
    """
    engine = get_engine()

    with engine.connect() as conn:
        try:
            stats = {}

            views = [
                'mv_year_severity',
                'mv_county_year',
                'mv_injury_group',
                'mv_adjuster_performance',
                'mv_venue_analysis',
                'mv_kpi_summary'
            ]

            for view in views:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {view}")).scalar()
                last_update = conn.execute(text(f"SELECT MAX(created_at) FROM {view}")).scalar()
                stats[view] = {
                    'row_count': result,
                    'last_updated': last_update
                }

            return stats

        except Exception as e:
            logger.error(f"Error getting view stats: {str(e)}")
            return {}


def check_materialized_views_exist():
    """
    Check if materialized views exist
    Returns True if all views exist, False otherwise
    """
    engine = get_engine()

    with engine.connect() as conn:
        try:
            required_views = [
                'mv_year_severity',
                'mv_county_year',
                'mv_injury_group',
                'mv_adjuster_performance',
                'mv_venue_analysis',
                'mv_kpi_summary'
            ]

            for view in required_views:
                result = conn.execute(text(
                    f"SELECT name FROM sqlite_master WHERE type='table' AND name='{view}'"
                )).fetchone()

                if result is None:
                    logger.warning(f"Materialized view {view} does not exist")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error checking views: {str(e)}")
            return False
