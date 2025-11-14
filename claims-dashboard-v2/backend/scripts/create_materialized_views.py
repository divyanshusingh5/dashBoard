"""
Create Materialized Views
Loads and executes SQL from query files
"""

from pathlib import Path
import logging
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine
from app.core import settings
from app.utils.query_loader import query_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_views():
    """Create all materialized views from SQL file."""
    logger.info("=" * 80)
    logger.info("CREATING MATERIALIZED VIEWS")
    logger.info(f"Database Type: {settings.DATABASE_TYPE}")
    logger.info("=" * 80)

    try:
        # Load the SQL from appropriate file
        logger.info(f"Loading SQL from: ddl/{settings.DATABASE_TYPE}/create_materialized_views.sql")
        sql = query_loader.load_ddl("create_materialized_views.sql")

        logger.info(f"Loaded {len(sql)} characters of SQL")

        with engine.connect() as conn:
            # For SQLite, we need to execute the entire script
            # For Snowflake, we might need to split by semicolon
            if settings.is_sqlite:
                logger.info("Executing SQLite materialized view creation...")
                # SQLite script is designed to be executed as one
                conn.execute(text(sql))
                conn.commit()

            elif settings.is_snowflake:
                logger.info("Executing Snowflake materialized view creation...")
                # Split by statements and execute each
                statements = [s.strip() for s in sql.split(';') if s.strip()]
                for i, statement in enumerate(statements, 1):
                    if statement and not statement.startswith('--'):
                        logger.info(f"Executing statement {i}/{len(statements)}...")
                        conn.execute(text(statement))
                conn.commit()

        # Verify creation
        with engine.connect() as conn:
            if settings.is_sqlite:
                result = conn.execute(text("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name LIKE 'mv_%'
                    ORDER BY name
                """))
            else:  # Snowflake
                result = conn.execute(text("""
                    SHOW MATERIALIZED VIEWS LIKE 'mv_%'
                """))

            views = [row[0] for row in result.fetchall()]

            logger.info("\n" + "=" * 80)
            logger.info("✅ MATERIALIZED VIEWS CREATED SUCCESSFULLY")
            logger.info("=" * 80)
            logger.info(f"\nCreated {len(views)} materialized views:")
            for view in views:
                logger.info(f"  - {view}")

            logger.info("\n" + "=" * 80)
            logger.info("Next steps:")
            logger.info("1. Start the API server:")
            logger.info("   uvicorn app.main:app --reload")
            logger.info("2. Visit the dashboard:")
            logger.info("   http://localhost:5173")
            logger.info("=" * 80 + "\n")

        return True

    except Exception as e:
        logger.error(f"❌ Error creating materialized views: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = create_views()
    sys.exit(0 if success else 1)
