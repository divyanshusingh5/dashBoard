"""
Migrate CSV data to database
Supports both SQLite and Snowflake
"""

import pandas as pd
from pathlib import Path
import logging
from tqdm import tqdm
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_session, engine
from app.core import settings
from app.db.models import Claim, SSNB, Weight

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_claims(csv_path: str = "data/dat.csv", batch_size: int = 1000):
    """
    Migrate claims from CSV to database.

    Args:
        csv_path: Path to claims CSV file
        batch_size: Number of records to insert per batch
    """
    logger.info("=" * 80)
    logger.info("MIGRATING CLAIMS DATA")
    logger.info("=" * 80)

    csv_file = Path(csv_path)
    if not csv_file.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return False

    logger.info(f"Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)

    logger.info(f"Found {len(df):,} claims with {len(df.columns)} columns")
    logger.info(f"Database: {settings.DATABASE_TYPE}")

    session = get_session()
    try:
        # Check if data already exists
        existing_count = session.query(Claim).count()
        if existing_count > 0:
            logger.warning(f"Database already contains {existing_count:,} claims")
            response = input("Do you want to continue and add more? (y/n): ")
            if response.lower() != 'y':
                logger.info("Migration cancelled")
                return False

        # Batch insert with progress bar
        total_inserted = 0
        for i in tqdm(range(0, len(df), batch_size), desc="Inserting claims"):
            batch = df.iloc[i:i+batch_size]

            # Convert batch to Claim objects
            claims = []
            for _, row in batch.iterrows():
                try:
                    claim_data = row.to_dict()
                    # Convert NaN to None
                    claim_data = {k: (None if pd.isna(v) else v) for k, v in claim_data.items()}
                    claim = Claim.from_dict(claim_data)
                    claims.append(claim)
                except Exception as e:
                    logger.warning(f"Error processing row: {e}")
                    continue

            # Bulk insert
            session.bulk_save_objects(claims)
            session.commit()
            total_inserted += len(claims)

        logger.info(f"✅ Successfully migrated {total_inserted:,} claims")
        logger.info(f"Total claims in database: {session.query(Claim).count():,}")
        return True

    except Exception as e:
        logger.error(f"Error migrating claims: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def migrate_ssnb(csv_path: str = "data/SSNB.csv"):
    """
    Migrate SSNB data from CSV.

    Args:
        csv_path: Path to SSNB CSV file
    """
    logger.info("\n" + "=" * 80)
    logger.info("MIGRATING SSNB DATA")
    logger.info("=" * 80)

    csv_file = Path(csv_path)
    if not csv_file.exists():
        logger.warning(f"SSNB CSV file not found: {csv_path}")
        logger.info("Skipping SSNB migration")
        return True

    logger.info(f"Loading SSNB data from: {csv_path}")
    df = pd.read_csv(csv_path)

    logger.info(f"Found {len(df):,} SSNB records")

    session = get_session()
    try:
        # Convert to SSNB objects
        ssnb_records = []
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing SSNB"):
            try:
                record_data = row.to_dict()
                record_data = {k: (None if pd.isna(v) else v) for k, v in record_data.items()}
                ssnb = SSNB.from_dict(record_data)
                ssnb_records.append(ssnb)
            except Exception as e:
                logger.warning(f"Error processing SSNB row: {e}")
                continue

        # Bulk insert
        session.bulk_save_objects(ssnb_records)
        session.commit()

        logger.info(f"✅ Successfully migrated {len(ssnb_records):,} SSNB records")
        return True

    except Exception as e:
        logger.error(f"Error migrating SSNB: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def migrate_weights(csv_path: str = "data/weights.csv"):
    """
    Migrate weights from CSV.

    Args:
        csv_path: Path to weights CSV file
    """
    logger.info("\n" + "=" * 80)
    logger.info("MIGRATING WEIGHTS DATA")
    logger.info("=" * 80)

    csv_file = Path(csv_path)
    if not csv_file.exists():
        logger.warning(f"Weights CSV file not found: {csv_path}")
        logger.info("Skipping weights migration")
        return True

    logger.info(f"Loading weights from: {csv_path}")
    df = pd.read_csv(csv_path)

    logger.info(f"Found {len(df):,} weight records")

    session = get_session()
    try:
        # Convert to Weight objects
        weights = []
        for _, row in df.iterrows():
            try:
                weight_data = row.to_dict()
                weight_data = {k: (None if pd.isna(v) else v) for k, v in weight_data.items()}
                weight = Weight.from_dict(weight_data)
                weights.append(weight)
            except Exception as e:
                logger.warning(f"Error processing weight row: {e}")
                continue

        # Bulk insert
        session.bulk_save_objects(weights)
        session.commit()

        logger.info(f"✅ Successfully migrated {len(weights):,} weights")
        return True

    except Exception as e:
        logger.error(f"Error migrating weights: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def main():
    """Run all migrations."""
    logger.info("\n" + "="*80)
    logger.info("CSV TO DATABASE MIGRATION")
    logger.info(f"Database Type: {settings.DATABASE_TYPE}")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info("=" * 80 + "\n")

    # Migrate in order
    success = True

    # 1. Claims (main data)
    if not migrate_claims():
        logger.error("❌ Claims migration failed")
        success = False

    # 2. SSNB (optional)
    if not migrate_ssnb():
        logger.warning("⚠️  SSNB migration failed or skipped")

    # 3. Weights (optional)
    if not migrate_weights():
        logger.warning("⚠️  Weights migration failed or skipped")

    # Summary
    logger.info("\n" + "=" * 80)
    if success:
        logger.info("✅ MIGRATION COMPLETE")
        logger.info("\nNext steps:")
        logger.info("1. Create materialized views:")
        logger.info("   python scripts/create_materialized_views.py")
        logger.info("2. Start the API server:")
        logger.info("   uvicorn app.main:app --reload")
    else:
        logger.info("❌ MIGRATION FAILED")
        logger.info("Check the errors above and try again")
    logger.info("=" * 80 + "\n")

    return success


if __name__ == "__main__":
    import sys

    # Optional: Pass CSV paths as arguments
    if len(sys.argv) > 1:
        claims_path = sys.argv[1]
        ssnb_path = sys.argv[2] if len(sys.argv) > 2 else "data/SSNB.csv"
        weights_path = sys.argv[3] if len(sys.argv) > 3 else "data/weights.csv"

        migrate_claims(claims_path)
        migrate_ssnb(ssnb_path)
        migrate_weights(weights_path)
    else:
        main()
