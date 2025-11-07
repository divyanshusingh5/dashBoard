"""
SMART MIGRATION SCRIPT
- Checks existing data before migrating
- Only migrates what's missing
- Handles duplicates properly
- Fast and efficient
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = 'app/db/claims_analytics.db'
DAT_CSV_PATH = 'dat.csv'
SSNB_CSV_PATH = 'SSNB.csv'


def check_table_exists(conn, table_name):
    """Check if table exists in database"""
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='{table_name}'
    """)
    return cursor.fetchone() is not None


def get_table_count(conn, table_name):
    """Get row count for a table"""
    try:
        cursor = conn.cursor()
        result = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        return result[0] if result else 0
    except sqlite3.OperationalError:
        return 0


def create_ssnb_table(conn):
    """Create SSNB table - will use SQLAlchemy schema"""
    logger.info("Creating ssnb table using SQLAlchemy...")

    try:
        from app.db.schema import Base, get_engine, SSNB
        engine = get_engine()
        Base.metadata.create_all(engine, tables=[SSNB.__table__])
        logger.info("ssnb table created successfully")
    except Exception as e:
        logger.error(f"Error creating ssnb table: {e}")
        raise


def migrate_claims_data(conn):
    """Migrate claims data from dat.csv"""
    logger.info("\n" + "="*80)
    logger.info("CHECKING CLAIMS DATA")
    logger.info("="*80)

    claims_count = get_table_count(conn, 'claims')

    if claims_count > 0:
        logger.info(f"✓ Claims table already has {claims_count:,} records")
        logger.info("✓ Skipping dat.csv migration (already done)")
        return True

    logger.info("Claims table is empty, migrating from dat.csv...")

    if not Path(DAT_CSV_PATH).exists():
        logger.error(f"Error: {DAT_CSV_PATH} not found!")
        return False

    try:
        # Load CSV
        logger.info(f"Reading {DAT_CSV_PATH}...")
        df = pd.read_csv(DAT_CSV_PATH)
        logger.info(f"Loaded {len(df):,} records from CSV")

        # Migrate to database
        logger.info("Migrating to SQLite database...")
        df.to_sql('claims', conn, if_exists='replace', index=False, chunksize=5000)

        new_count = get_table_count(conn, 'claims')
        logger.info(f"✓ Successfully migrated {new_count:,} claims records")
        return True

    except Exception as e:
        logger.error(f"Error migrating claims data: {str(e)}")
        return False


def migrate_ssnb_data(conn):
    """Migrate SSNB data with duplicate handling"""
    logger.info("\n" + "="*80)
    logger.info("CHECKING SSNB DATA")
    logger.info("="*80)

    # Check if table exists
    if not check_table_exists(conn, 'ssnb'):
        logger.info("ssnb table doesn't exist, creating it...")
        create_ssnb_table(conn)
    else:
        logger.info("ssnb table already exists")

    ssnb_count = get_table_count(conn, 'ssnb')

    if ssnb_count > 0:
        logger.info(f"✓ SSNB table already has {ssnb_count:,} records")
        print("\nDo you want to:")
        print("  1. Skip SSNB migration (keep existing data)")
        print("  2. Replace all SSNB data (clear and re-migrate)")
        user_input = input("Choice (1/2): ").strip()

        if user_input == '1':
            logger.info("✓ Skipping SSNB migration (keeping existing data)")
            return True
        elif user_input == '2':
            logger.info("Clearing existing SSNB data...")
            conn.execute("DELETE FROM ssnb")
            conn.commit()
            logger.info("✓ Cleared existing SSNB data")
        else:
            logger.info("Invalid choice, skipping SSNB migration")
            return True

    if not Path(SSNB_CSV_PATH).exists():
        logger.error(f"Error: {SSNB_CSV_PATH} not found!")
        return False

    try:
        # Load CSV
        logger.info(f"Reading {SSNB_CSV_PATH}...")
        df = pd.read_csv(SSNB_CSV_PATH)
        logger.info(f"Loaded {len(df):,} records from SSNB.csv")

        # Check for duplicates in CSV
        duplicates = df['CLAIMID'].duplicated().sum()
        if duplicates > 0:
            logger.warning(f"⚠ Found {duplicates} duplicate CLAIMID entries in CSV")
            logger.info("Keeping only the last occurrence of each duplicate CLAIMID...")
            df = df.drop_duplicates(subset='CLAIMID', keep='last')
            logger.info(f"After deduplication: {len(df):,} records")

        # Migrate to database using pandas (much faster!)
        logger.info("Migrating to database...")
        df.to_sql('ssnb', conn, if_exists='append', index=False, chunksize=1000)

        final_count = get_table_count(conn, 'ssnb')
        logger.info(f"\n✓ SSNB migration complete:")
        logger.info(f"  - Total records in table: {final_count:,}")

        return True

    except Exception as e:
        logger.error(f"Error migrating SSNB data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_migration(conn):
    """Verify migration results"""
    logger.info("\n" + "="*80)
    logger.info("MIGRATION VERIFICATION")
    logger.info("="*80)

    claims_count = get_table_count(conn, 'claims')
    ssnb_count = get_table_count(conn, 'ssnb')

    logger.info(f"Claims table: {claims_count:,} records")
    logger.info(f"SSNB table: {ssnb_count:,} records")

    # Check for matching CLAIMIDs
    cursor = conn.cursor()
    matched = cursor.execute("""
        SELECT COUNT(*)
        FROM claims c
        INNER JOIN ssnb s ON c.CLAIMID = s.CLAIMID
    """).fetchone()[0]

    if claims_count > 0:
        logger.info(f"Matched claims (have SSNB data): {matched:,} ({matched/claims_count*100:.1f}%)")
    else:
        logger.info(f"Matched claims: {matched:,}")

    # Sample data
    if ssnb_count > 0:
        logger.info("\nSample SSNB data:")
        sample = cursor.execute("""
            SELECT
                s.CLAIMID,
                s.DOLLARAMOUNTHIGH,
                s.CAUSATION_HIGH_RECOMMENDATION,
                s.PRIMARY_INJURY,
                s.PRIMARY_BODYPART,
                s.PRIMARY_SEVERITY_SCORE,
                s.PRIMARY_CAUSATION_SCORE
            FROM ssnb s
            LIMIT 3
        """).fetchall()

        for row in sample:
            logger.info(f"  CLAIMID: {row[0]}")
            logger.info(f"    Actual Settlement: ${row[1]:,.2f}")
            logger.info(f"    Predicted: ${row[2]:,.2f}")
            logger.info(f"    Injury: {row[3]} - {row[4]}")
            logger.info(f"    Severity: {row[5]:,.2f}, Causation: {row[6]:,.2f}")

    logger.info("\n" + "="*80)
    logger.info("MIGRATION SUMMARY")
    logger.info("="*80)
    logger.info(f"✓ Claims data: {claims_count:,} records")
    logger.info(f"✓ SSNB data: {ssnb_count:,} records")
    if claims_count > 0 and matched > 0:
        logger.info(f"✓ Match rate: {matched/claims_count*100:.1f}%")
    logger.info("✓ Ready for use!")
    logger.info("="*80)


def main():
    """Main migration function"""
    logger.info("\n" + "="*80)
    logger.info("SMART MIGRATION SCRIPT")
    logger.info("="*80)
    logger.info(f"Database: {DB_PATH}")
    logger.info(f"Claims CSV: {DAT_CSV_PATH}")
    logger.info(f"SSNB CSV: {SSNB_CSV_PATH}")
    logger.info("="*80)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)

    try:
        # Step 1: Migrate claims data (if needed)
        if not migrate_claims_data(conn):
            logger.error("Failed to migrate claims data")
            return

        # Step 2: Migrate SSNB data (if needed)
        if not migrate_ssnb_data(conn):
            logger.error("Failed to migrate SSNB data")
            return

        # Step 3: Verify
        verify_migration(conn)

    except Exception as e:
        logger.error(f"Migration error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == '__main__':
    main()
