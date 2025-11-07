"""
Enhanced CSV to SQLite Migration with Composite Scores
Calculates SEVERITY_SCORE and CAUSATION_SCORE from clinical factor weights
"""

import pandas as pd
import sqlite3
from pathlib import Path
import logging
from tqdm import tqdm
from calculate_composite_scores import (
    calculate_severity_score,
    calculate_causation_score,
    categorize_severity,
    categorize_causation,
    calculate_caution_level,
    SEVERITY_FACTORS,
    CAUSATION_FACTORS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_with_composite_scores():
    """
    Migrate dat.csv to SQLite with enhanced composite scores
    """
    logger.info("="*60)
    logger.info("ENHANCED MIGRATION WITH COMPOSITE SCORES")
    logger.info("="*60)

    # Load data
    logger.info("\n[1/6] Loading dat.csv...")
    df = pd.read_csv('data/dat.csv', low_memory=False)
    logger.info(f"Loaded {len(df)} claims")

    # Remove quotes from clinical factor column names
    logger.info("\n[2/6] Cleaning column names...")
    df.columns = [col.strip("'") for col in df.columns]

    # Calculate variance_pct
    logger.info("\n[3/6] Calculating variance percentage...")
    df['variance_pct'] = ((df['DOLLARAMOUNTHIGH'] - df['CAUSATION_HIGH_RECOMMENDATION'])
                          / df['CAUSATION_HIGH_RECOMMENDATION'] * 100)
    df['variance_pct'] = df['variance_pct'].fillna(0).round(2)

    # Calculate composite scores
    logger.info("\n[4/6] Calculating SEVERITY_SCORE (sum of 20 severity factors)...")
    df['SEVERITY_SCORE'] = df.apply(calculate_severity_score, axis=1)
    logger.info(f"  Mean: {df['SEVERITY_SCORE'].mean():.2f}, Std: {df['SEVERITY_SCORE'].std():.2f}")

    logger.info("\n[5/6] Calculating CAUSATION_SCORE (sum of 21 causation/compliance factors)...")
    df['CAUSATION_SCORE'] = df.apply(calculate_causation_score, axis=1)
    logger.info(f"  Mean: {df['CAUSATION_SCORE'].mean():.2f}, Std: {df['CAUSATION_SCORE'].std():.2f}")

    # Categorize scores
    logger.info("\n[6/6] Categorizing scores and calculating CAUTION_LEVEL...")
    df['SEVERITY_CATEGORY'] = df['SEVERITY_SCORE'].apply(categorize_severity)
    df['CAUSATION_CATEGORY'] = df['CAUSATION_SCORE'].apply(categorize_causation)
    df['CAUTION_LEVEL'] = df.apply(
        lambda row: calculate_caution_level(row['SEVERITY_SCORE'], row['CAUSATION_SCORE']),
        axis=1
    )

    # Print distributions
    print("\n" + "="*60)
    print("SCORE DISTRIBUTIONS")
    print("="*60)
    print("\nSEVERITY_CATEGORY:")
    print(df['SEVERITY_CATEGORY'].value_counts().sort_index())
    print("\nCAUSATION_CATEGORY:")
    print(df['CAUSATION_CATEGORY'].value_counts().sort_index())
    print("\nCAUTION_LEVEL:")
    print(df['CAUTION_LEVEL'].value_counts().sort_index())

    # Save to SQLite
    logger.info("\nSaving to SQLite database...")
    db_path = Path('app/db/claims_analytics.db')
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    df.to_sql('claims', conn, if_exists='replace', index=False, chunksize=100)
    conn.close()

    logger.info(f"[SUCCESS] Migrated {len(df)} claims to {db_path}")

    # Show sample
    print("\n" + "="*60)
    print("SAMPLE CLAIMS WITH NEW SCORES")
    print("="*60)
    sample_cols = ['CLAIMID', 'DOLLARAMOUNTHIGH', 'SEVERITY_SCORE', 'SEVERITY_CATEGORY',
                   'CAUSATION_SCORE', 'CAUSATION_CATEGORY', 'CAUTION_LEVEL', 'variance_pct']
    print(df[sample_cols].head(10).to_string(index=False))

    # Verify
    logger.info("\nVerifying database...")
    conn = sqlite3.connect(str(db_path))
    result = pd.read_sql_query("SELECT COUNT(*) as count FROM claims", conn)
    logger.info(f"Verification: {result['count'].iloc[0]} claims in database")

    # Check for new columns
    columns_query = "PRAGMA table_info(claims)"
    columns_df = pd.read_sql_query(columns_query, conn)
    new_columns = ['SEVERITY_SCORE', 'CAUSATION_SCORE', 'SEVERITY_CATEGORY',
                   'CAUSATION_CATEGORY', 'CAUTION_LEVEL']
    for col in new_columns:
        if col in columns_df['name'].values:
            logger.info(f"  [OK] Column '{col}' exists")
        else:
            logger.warning(f"  [MISSING] Column '{col}' not found!")

    conn.close()

    logger.info("\n" + "="*60)
    logger.info("MIGRATION COMPLETE!")
    logger.info("="*60)
    logger.info(f"\nDatabase: {db_path}")
    logger.info(f"Total claims: {len(df)}")
    logger.info(f"New columns added: {len(new_columns)}")
    logger.info("\nComposite Score Breakdown:")
    logger.info(f"  SEVERITY_SCORE: Sum of {len(SEVERITY_FACTORS)} factors")
    logger.info(f"  CAUSATION_SCORE: Sum of {len(CAUSATION_FACTORS)} factors")


if __name__ == "__main__":
    migrate_with_composite_scores()
