"""
Materialized Views for PostgreSQL - Fast Aggregation for 100K+ Records

This module manages PostgreSQL materialized views for dashboard performance.
The actual views are created via create_materialized_views_postgres.py script.

Usage:
    from app.db.materialized_views import check_materialized_views_exist, refresh_all_materialized_views

    # Check if views exist
    if not check_materialized_views_exist():
        print("Run create_materialized_views_postgres.py first")

    # Refresh views after data updates
    refresh_all_materialized_views()
"""

from sqlalchemy import text
from app.db.schema import get_engine
import logging

logger = logging.getLogger(__name__)


def create_all_materialized_views():
    """
    For PostgreSQL, materialized views should be created via the standalone script:
    backend/create_materialized_views_postgres.py

    This function just checks if they exist and provides helpful messages.
    """
    engine = get_engine()

    logger.info("Checking PostgreSQL materialized views...")

    with engine.connect() as conn:
        try:
            # Check if we're using PostgreSQL
            result = conn.execute(text("SELECT version()")).fetchone()
            db_version = result[0] if result else ""

            if "PostgreSQL" not in db_version:
                logger.warning("Not using PostgreSQL - materialized views may not work correctly")
                return False

            # Check if materialized views exist
            exists = check_materialized_views_exist()

            if not exists:
                logger.warning("⚠ Materialized views not found!")
                logger.warning("Run: python create_materialized_views_postgres.py")
                return False

            logger.info("✓ All PostgreSQL materialized views exist")
            return True

        except Exception as e:
            logger.error(f"Error checking materialized views: {str(e)}")
            return False


def refresh_all_materialized_views():
    """
    Refresh all PostgreSQL materialized views
    Call this after data updates
    """
    engine = get_engine()

    logger.info("Refreshing all PostgreSQL materialized views...")

    views = [
        'mv_year_severity',
        'mv_county_year',
        'mv_injury_group',
        'mv_adjuster_performance',
        'mv_venue_analysis',
        'mv_kpi_summary'
    ]

    with engine.connect() as conn:
        try:
            for view in views:
                logger.info(f"Refreshing {view}...")
                conn.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
                conn.commit()

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
    Get statistics about PostgreSQL materialized views
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
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {view}")).scalar()
                    stats[view] = {
                        'row_count': result,
                        'exists': True
                    }
                except Exception:
                    stats[view] = {
                        'row_count': 0,
                        'exists': False
                    }

            return stats

        except Exception as e:
            logger.error(f"Error getting view stats: {str(e)}")
            return {}


def check_materialized_views_exist():
    """
    Check if PostgreSQL materialized views exist
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
                # Check in PostgreSQL's pg_matviews
                result = conn.execute(text(f"""
                    SELECT matviewname
                    FROM pg_matviews
                    WHERE schemaname = 'public'
                    AND matviewname = '{view}'
                """)).fetchone()

                if result is None:
                    logger.warning(f"Materialized view {view} does not exist")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error checking views: {str(e)}")
            return False
