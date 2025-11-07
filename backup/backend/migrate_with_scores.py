"""
Final Migration Script: dat.csv + weights.csv scores → SQLite
Calculates composite scores from weights.csv and merges with dat.csv
"""

import pandas as pd
import sqlite3
from pathlib import Path
import logging
from calculate_composite_scores import (
    calculate_severity_score,
    calculate_causation_score,
    categorize_severity,
    categorize_causation,
    calculate_caution_level
)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    logger.info("="*70)
    logger.info("COMPOSITE SCORES MIGRATION: dat.csv + weights.csv → SQLite")
    logger.info("="*70)

    # Step 1: Load dat.csv
    logger.info("\n[1/7] Loading dat.csv (claim data)...")
    dat_df = pd.read_csv('data/dat.csv', low_memory=False)
    dat_df.columns = [col.strip("'") for col in dat_df.columns]  # Remove quotes

    # Drop duplicate clinical Injury_Count column (keep INJURY_COUNT)
    if 'Injury_Count' in dat_df.columns:
        dat_df.drop(columns=['Injury_Count'], inplace=True)
        logger.info("  Dropped duplicate 'Injury_Count' clinical column from dat.csv")

    logger.info(f"  Loaded {len(dat_df)} claims")
    logger.info(f"  Columns: {len(dat_df.columns)}")

    # Step 2: Load weights.csv
    logger.info("\n[2/7] Loading weights.csv (clinical factor weights)...")
    weights_df = pd.read_csv('data/weights.csv', low_memory=False)
    weights_df.columns = [col.strip("'") for col in weights_df.columns]  # Remove quotes

    # Drop duplicate clinical factor column (Injury_Count exists in both files)
    if 'Injury_Count' in weights_df.columns:
        weights_df.drop(columns=['Injury_Count'], inplace=True)
        logger.info("  Dropped duplicate 'Injury_Count' column from weights.csv")

    logger.info(f"  Loaded {len(weights_df)} weight records")

    # Step 3: Calculate variance for dat.csv
    logger.info("\n[3/7] Calculating variance_pct...")
    dat_df['variance_pct'] = (
        (dat_df['DOLLARAMOUNTHIGH'] - dat_df['CAUSATION_HIGH_RECOMMENDATION'])
        / dat_df['CAUSATION_HIGH_RECOMMENDATION'] * 100
    )
    dat_df['variance_pct'] = dat_df['variance_pct'].fillna(0).round(2)

    # Step 4: Calculate composite scores from weights.csv
    logger.info("\n[4/7] Calculating composite scores from weights.csv...")
    logger.info("  a) SEVERITY_SCORE (19 severity-related factors)...")
    weights_df['SEVERITY_SCORE'] = weights_df.apply(calculate_severity_score, axis=1)
    logger.info(f"     Mean: {weights_df['SEVERITY_SCORE'].mean():.2f}, "
                f"Std: {weights_df['SEVERITY_SCORE'].std():.2f}")

    logger.info("  b) CAUSATION_SCORE (21 causation/compliance factors)...")
    weights_df['CAUSATION_SCORE'] = weights_df.apply(calculate_causation_score, axis=1)
    logger.info(f"     Mean: {weights_df['CAUSATION_SCORE'].mean():.2f}, "
                f"Std: {weights_df['CAUSATION_SCORE'].std():.2f}")

    logger.info("  c) Categorizing scores...")
    weights_df['SEVERITY_CATEGORY'] = weights_df['SEVERITY_SCORE'].apply(categorize_severity)
    weights_df['CAUSATION_CATEGORY'] = weights_df['CAUSATION_SCORE'].apply(categorize_causation)
    weights_df['CAUTION_LEVEL'] = weights_df.apply(
        lambda row: calculate_caution_level(row['SEVERITY_SCORE'], row['CAUSATION_SCORE']),
        axis=1
    )

    # Step 5: Merge scores into dat_df
    logger.info("\n[5/7] Merging composite scores into dat.csv...")
    score_cols = ['CLAIMID', 'SEVERITY_SCORE', 'CAUSATION_SCORE',
                  'SEVERITY_CATEGORY', 'CAUSATION_CATEGORY', 'CAUTION_LEVEL']

    # Merge on CLAIMID
    merged_df = dat_df.merge(
        weights_df[score_cols],
        on='CLAIMID',
        how='left',
        suffixes=('', '_from_weights')
    )

    # Check for unmatched claims
    unmatched = merged_df['SEVERITY_SCORE'].isna().sum()
    if unmatched > 0:
        logger.warning(f"  WARNING: {unmatched} claims have no matching weights")
        # Fill NaN with defaults
        merged_df['SEVERITY_SCORE'].fillna(0, inplace=True)
        merged_df['CAUSATION_SCORE'].fillna(0, inplace=True)
        merged_df['SEVERITY_CATEGORY'].fillna('Low', inplace=True)
        merged_df['CAUSATION_CATEGORY'].fillna('Low', inplace=True)
        merged_df['CAUTION_LEVEL'].fillna('Medium', inplace=True)

    logger.info(f"  Successfully merged {len(merged_df)} claims")

    # Step 6: Save to SQLite
    logger.info("\n[6/7] Saving to SQLite database...")
    db_path = Path('app/db/claims_analytics.db')
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    merged_df.to_sql('claims', conn, if_exists='replace', index=False, chunksize=100)
    conn.close()

    logger.info(f"  Saved to: {db_path}")

    # Step 7: Verify
    logger.info("\n[7/7] Verifying database...")
    conn = sqlite3.connect(str(db_path))

    # Count claims
    result = pd.read_sql_query("SELECT COUNT(*) as count FROM claims", conn)
    logger.info(f"  Total claims: {result['count'].iloc[0]}")

    # Check new columns exist
    columns_query = "PRAGMA table_info(claims)"
    columns_df = pd.read_sql_query(columns_query, conn)
    new_columns = ['SEVERITY_SCORE', 'CAUSATION_SCORE', 'SEVERITY_CATEGORY',
                   'CAUSATION_CATEGORY', 'CAUTION_LEVEL', 'variance_pct']

    logger.info("  Checking new columns:")
    for col in new_columns:
        if col in columns_df['name'].values:
            logger.info(f"    [OK] {col}")
        else:
            logger.error(f"    [MISSING] {col}")

    # Check score distributions
    dist_query = """
        SELECT
            SEVERITY_CATEGORY,
            COUNT(*) as count
        FROM claims
        WHERE SEVERITY_CATEGORY IS NOT NULL
        GROUP BY SEVERITY_CATEGORY
        ORDER BY SEVERITY_CATEGORY
    """
    severity_dist = pd.read_sql_query(dist_query, conn)

    logger.info("\n  SEVERITY_CATEGORY Distribution:")
    for _, row in severity_dist.iterrows():
        logger.info(f"    {row['SEVERITY_CATEGORY']}: {row['count']}")

    causation_query = """
        SELECT
            CAUSATION_CATEGORY,
            COUNT(*) as count
        FROM claims
        WHERE CAUSATION_CATEGORY IS NOT NULL
        GROUP BY CAUSATION_CATEGORY
        ORDER BY CAUSATION_CATEGORY
    """
    causation_dist = pd.read_sql_query(causation_query, conn)

    logger.info("\n  CAUSATION_CATEGORY Distribution:")
    for _, row in causation_dist.iterrows():
        logger.info(f"    {row['CAUSATION_CATEGORY']}: {row['count']}")

    # Sample data
    logger.info("\n" + "="*70)
    logger.info("SAMPLE CLAIMS WITH COMPOSITE SCORES")
    logger.info("="*70)
    sample_query = """
        SELECT
            CLAIMID,
            DOLLARAMOUNTHIGH as Actual,
            CAUSATION_HIGH_RECOMMENDATION as Predicted,
            variance_pct as Variance,
            SEVERITY_SCORE as SevScore,
            SEVERITY_CATEGORY as SevCat,
            CAUSATION_SCORE as CausScore,
            CAUSATION_CATEGORY as CausCat,
            CAUTION_LEVEL as Caution
        FROM claims
        LIMIT 10
    """
    sample = pd.read_sql_query(sample_query, conn)
    print(sample.to_string(index=False))

    conn.close()

    logger.info("\n" + "="*70)
    logger.info("MIGRATION COMPLETE!")
    logger.info("="*70)
    logger.info(f"\nDatabase: {db_path}")
    logger.info(f"Total claims: {len(merged_df)}")
    logger.info("\nNew scoring system active:")
    logger.info("  - SEVERITY_SCORE: Physical injury severity (19 factors)")
    logger.info("  - CAUSATION_SCORE: Treatment compliance & causation (21 factors)")
    logger.info("  - CAUTION_LEVEL: Combined risk assessment")
    logger.info("\nNext steps:")
    logger.info("  1. Restart backend: python run.py")
    logger.info("  2. Backend will now return composite scores in API responses")
    logger.info("  3. Update frontend to display new score columns")


if __name__ == "__main__":
    main()
