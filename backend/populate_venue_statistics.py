"""
Populate venue_statistics table from database claims
This creates pre-computed statistics for fast venue rating recommendations
"""

import sqlite3
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def categorize_score(score, score_type='severity'):
    """Categorize severity/causation scores into Low/Medium/High"""
    if score is None:
        return None

    if score_type == 'severity':
        if score <= 500:
            return 'Low'
        elif score <= 1500:
            return 'Medium'
        else:
            return 'High'
    else:  # causation
        if score <= 100:
            return 'Low'
        elif score <= 300:
            return 'Medium'
        else:
            return 'High'

def populate_venue_statistics():
    """Populate venue_statistics table with aggregated data"""

    conn = sqlite3.connect('app/db/claims_analytics.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    logger.info("=" * 80)
    logger.info("POPULATING VENUE STATISTICS TABLE")
    logger.info("=" * 80)

    # First, clear existing data
    logger.info("Clearing existing venue_statistics data...")
    cursor.execute("DELETE FROM venue_statistics")
    conn.commit()
    logger.info("✓ Cleared")

    # Get data period
    cursor.execute("SELECT MIN(CLAIMCLOSEDDATE), MAX(CLAIMCLOSEDDATE) FROM claims WHERE CLAIMCLOSEDDATE IS NOT NULL")
    period = cursor.fetchone()
    data_period_start = period[0] if period else None
    data_period_end = period[1] if period else None

    logger.info(f"Data period: {data_period_start} to {data_period_end}")

    # Generate statistics using SQL aggregation
    logger.info("\nCalculating venue statistics...")

    query = """
    WITH categorized_claims AS (
        SELECT
            VENUERATING,
            VENUERATINGTEXT,
            RATINGWEIGHT,
            CASE
                WHEN CALCULATED_SEVERITY_SCORE <= 500 THEN 'Low'
                WHEN CALCULATED_SEVERITY_SCORE <= 1500 THEN 'Medium'
                ELSE 'High'
            END as severity_cat,
            CASE
                WHEN CALCULATED_CAUSATION_SCORE <= 100 THEN 'Low'
                WHEN CALCULATED_CAUSATION_SCORE <= 300 THEN 'Medium'
                ELSE 'High'
            END as causation_cat,
            IOL,
            DOLLARAMOUNTHIGH as actual,
            CAUSATION_HIGH_RECOMMENDATION as predicted,
            ABS(DOLLARAMOUNTHIGH - CAUSATION_HIGH_RECOMMENDATION) as abs_error,
            ABS(variance_pct) as error_pct
        FROM claims
        WHERE VENUERATING IS NOT NULL
          AND CALCULATED_SEVERITY_SCORE IS NOT NULL
          AND CALCULATED_CAUSATION_SCORE IS NOT NULL
          AND IOL IS NOT NULL
          AND DOLLARAMOUNTHIGH IS NOT NULL
          AND CAUSATION_HIGH_RECOMMENDATION IS NOT NULL
    )
    SELECT
        VENUERATING,
        MAX(VENUERATINGTEXT) as VENUERATINGTEXT,
        AVG(RATINGWEIGHT) as RATINGWEIGHT,
        severity_cat,
        causation_cat,
        IOL,

        -- Actual settlement statistics
        AVG(actual) as mean_actual,
        COUNT(*) as sample_size,
        -- Note: SQLite doesn't have PERCENTILE_CONT, we'll calculate median differently
        MIN(actual) as min_actual,
        MAX(actual) as max_actual,

        -- Predicted statistics
        AVG(predicted) as mean_predicted,

        -- Error metrics
        AVG(abs_error) as mean_absolute_error,
        AVG(error_pct) as mean_error_pct

    FROM categorized_claims
    GROUP BY VENUERATING, severity_cat, causation_cat, IOL
    HAVING COUNT(*) >= 10
    ORDER BY VENUERATING, severity_cat, causation_cat, IOL
    """

    cursor.execute(query)
    results = cursor.fetchall()

    logger.info(f"Found {len(results)} venue/severity/causation/IOL combinations")

    # Calculate additional statistics for each combination
    insert_count = 0
    for row in results:
        venue = row[0]
        venue_text = row[1]
        rating_weight = row[2]
        sev_cat = row[3]
        caus_cat = row[4]
        iol = row[5]
        mean_actual = row[6]
        sample_size = row[7]
        min_actual = row[8]
        max_actual = row[9]
        mean_predicted = row[10]
        mean_abs_error = row[11]
        mean_error_pct = row[12]

        # Get median actual (simpler approach without CTE)
        median_actual_query = """
        SELECT DOLLARAMOUNTHIGH
        FROM claims
        WHERE VENUERATING = ?
          AND CASE
                WHEN CALCULATED_SEVERITY_SCORE <= 500 THEN 'Low'
                WHEN CALCULATED_SEVERITY_SCORE <= 1500 THEN 'Medium'
                ELSE 'High'
              END = ?
          AND CASE
                WHEN CALCULATED_CAUSATION_SCORE <= 100 THEN 'Low'
                WHEN CALCULATED_CAUSATION_SCORE <= 300 THEN 'Medium'
                ELSE 'High'
              END = ?
          AND IOL = ?
          AND DOLLARAMOUNTHIGH IS NOT NULL
        ORDER BY DOLLARAMOUNTHIGH
        LIMIT 1 OFFSET ?
        """
        median_offset = sample_size // 2
        cursor.execute(median_actual_query, (venue, sev_cat, caus_cat, iol, median_offset))
        median_result = cursor.fetchone()
        median_actual = median_result[0] if median_result else mean_actual

        # Get median error
        median_error_query = """
        SELECT ABS(DOLLARAMOUNTHIGH - CAUSATION_HIGH_RECOMMENDATION) as abs_error
        FROM claims
        WHERE VENUERATING = ?
          AND CASE
                WHEN CALCULATED_SEVERITY_SCORE <= 500 THEN 'Low'
                WHEN CALCULATED_SEVERITY_SCORE <= 1500 THEN 'Medium'
                ELSE 'High'
              END = ?
          AND CASE
                WHEN CALCULATED_CAUSATION_SCORE <= 100 THEN 'Low'
                WHEN CALCULATED_CAUSATION_SCORE <= 300 THEN 'Medium'
                ELSE 'High'
              END = ?
          AND IOL = ?
          AND DOLLARAMOUNTHIGH IS NOT NULL
        ORDER BY abs_error
        LIMIT 1 OFFSET ?
        """
        cursor.execute(median_error_query, (venue, sev_cat, caus_cat, iol, median_offset))
        median_error_result = cursor.fetchone()
        median_error = median_error_result[0] if median_error_result else mean_abs_error

        # Get variance for standard deviation
        variance_query = """
        SELECT AVG((DOLLARAMOUNTHIGH - ?) * (DOLLARAMOUNTHIGH - ?)) as variance_actual
        FROM claims
        WHERE VENUERATING = ?
          AND CASE
                WHEN CALCULATED_SEVERITY_SCORE <= 500 THEN 'Low'
                WHEN CALCULATED_SEVERITY_SCORE <= 1500 THEN 'Medium'
                ELSE 'High'
              END = ?
          AND CASE
                WHEN CALCULATED_CAUSATION_SCORE <= 100 THEN 'Low'
                WHEN CALCULATED_CAUSATION_SCORE <= 300 THEN 'Medium'
                ELSE 'High'
              END = ?
          AND IOL = ?
          AND DOLLARAMOUNTHIGH IS NOT NULL
        """
        cursor.execute(variance_query, (mean_actual, mean_actual, venue, sev_cat, caus_cat, iol))
        variance_result = cursor.fetchone()
        variance_actual = variance_result[0] if variance_result and variance_result[0] else 0
        stddev_actual = variance_actual ** 0.5 if variance_actual > 0 else 0

        # Coefficient of variation (predictability measure)
        cv = (stddev_actual / mean_actual) if mean_actual > 0 else 0

        # Confidence interval (95%)
        se = stddev_actual / (sample_size ** 0.5) if sample_size > 0 else 0
        ci_lower = mean_actual - (1.96 * se)
        ci_upper = mean_actual + (1.96 * se)

        # Insert into venue_statistics
        insert_query = """
        INSERT INTO venue_statistics (
            VENUERATING, VENUERATINGTEXT, RATINGWEIGHT,
            SEVERITY_CATEGORY, CAUSATION_CATEGORY, IOL,
            mean_actual, median_actual, stddev_actual, min_actual, max_actual,
            mean_predicted, median_predicted, stddev_predicted,
            mean_absolute_error, median_absolute_error, mean_error_pct,
            coefficient_of_variation,
            sample_size, confidence_interval_lower, confidence_interval_upper,
            last_updated, data_period_start, data_period_end
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(insert_query, (
            venue, venue_text, rating_weight,
            sev_cat, caus_cat, iol,
            mean_actual, median_actual, stddev_actual, min_actual, max_actual,
            mean_predicted, mean_predicted, 0,  # median_predicted, stddev_predicted
            mean_abs_error, median_error, mean_error_pct,
            cv,
            sample_size, ci_lower, ci_upper,
            datetime.now().isoformat(), data_period_start, data_period_end
        ))

        insert_count += 1
        if insert_count % 10 == 0:
            logger.info(f"  Inserted {insert_count}/{len(results)} combinations...")

    conn.commit()

    logger.info(f"\n✓ Successfully inserted {insert_count} venue statistics combinations")

    # Show summary
    logger.info("\n" + "=" * 80)
    logger.info("VENUE STATISTICS SUMMARY")
    logger.info("=" * 80)

    cursor.execute("""
        SELECT
            VENUERATING,
            COUNT(*) as combinations,
            SUM(sample_size) as total_claims,
            AVG(mean_absolute_error) as avg_error,
            MIN(sample_size) as min_sample,
            MAX(sample_size) as max_sample
        FROM venue_statistics
        GROUP BY VENUERATING
        ORDER BY VENUERATING
    """)

    logger.info(f"\n{'Venue Rating':<20} {'Combinations':<15} {'Total Claims':<15} {'Avg Error':<15} {'Sample Range':<20}")
    logger.info("-" * 90)
    for row in cursor.fetchall():
        logger.info(f"{row[0]:<20} {row[1]:<15} {row[2]:<15} ${row[3]:<14,.2f} {row[4]}-{row[5]}")

    logger.info("\n✓ Venue statistics table populated successfully!")
    logger.info(f"✓ Ready for fast venue rating recommendations (<1 second queries)")

    conn.close()

if __name__ == "__main__":
    try:
        populate_venue_statistics()
    except Exception as e:
        logger.error(f"Error populating venue statistics: {str(e)}")
        import traceback
        traceback.print_exc()
