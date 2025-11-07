"""
CREATE EXECUTIVE SUMMARY VIEWS
Comprehensive factor performance analysis with:
- Multi-factor combinations (Severity × Injury × Impact × Venue)
- VersionID support for filtering
- County comparison capability
- Top 10 high variance factors
- Drill-down ready structure
"""
from sqlalchemy import create_engine, text
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_executive_summary_views():
    """Create executive summary and comparison views"""

    db_path = Path('app/db/claims_analytics.db')
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return False

    engine = create_engine(f'sqlite:///{db_path}')

    try:
        with engine.connect() as conn:
            logger.info("=" * 80)
            logger.info("CREATING EXECUTIVE SUMMARY VIEWS")
            logger.info("=" * 80)

            result = conn.execute(text("SELECT COUNT(*) as count FROM claims")).fetchone()
            claim_count = result[0]
            logger.info(f"Processing {claim_count:,} claims...")

            # Drop existing executive summary views
            logger.info("\nDropping existing executive summary views...")
            views_to_drop = [
                'mv_executive_summary',
                'mv_factor_combinations_detailed',
                'mv_county_comparison',
                'mv_top_variance_factors'
            ]
            for view in views_to_drop:
                conn.execute(text(f"DROP TABLE IF EXISTS {view}"))
            conn.commit()
            logger.info("Done")

            # 1. EXECUTIVE SUMMARY - Multi-Factor Analysis
            logger.info("\n[1/4] Creating mv_executive_summary...")
            logger.info("  This shows top variance factors by ALL dimensions...")
            conn.execute(text("""
                CREATE TABLE mv_executive_summary AS
                SELECT
                    -- Factor Identification
                    'Severity: ' ||
                    CASE
                        WHEN CALCULATED_SEVERITY_SCORE <= 500 THEN 'Low'
                        WHEN CALCULATED_SEVERITY_SCORE <= 1500 THEN 'Medium'
                        ELSE 'High'
                    END || ' | Injury: ' ||
                    COALESCE(PRIMARY_INJURY_BY_SEVERITY, 'Unknown') || ' | Venue: ' ||
                    COALESCE(VENUERATING, 'Unknown') || ' | IOL: ' ||
                    CAST(IOL AS TEXT) as factor_combination,

                    -- Individual Factor Components
                    CASE
                        WHEN CALCULATED_SEVERITY_SCORE <= 500 THEN 'Low'
                        WHEN CALCULATED_SEVERITY_SCORE <= 1500 THEN 'Medium'
                        ELSE 'High'
                    END as severity_level,

                    PRIMARY_INJURY_BY_SEVERITY as injury_type,
                    PRIMARY_BODYPART_BY_SEVERITY as body_part,
                    VENUERATING as venue_rating,
                    COUNTYNAME as county,
                    VENUESTATE as state,
                    IOL as impact_on_life,
                    VERSIONID as version_id,
                    CAST(strftime('%Y', CLAIMCLOSEDDATE) AS INTEGER) as year,

                    -- Metrics
                    COUNT(*) as claim_count,
                    AVG(DOLLARAMOUNTHIGH) as avg_actual,
                    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
                    AVG(variance_pct) as avg_deviation_pct,
                    ABS(AVG(variance_pct)) as abs_avg_deviation_pct,
                    MIN(variance_pct) as min_deviation,
                    MAX(variance_pct) as max_deviation,

                    -- Risk Categorization
                    CASE
                        WHEN ABS(AVG(variance_pct)) > 30 THEN 'Critical'
                        WHEN ABS(AVG(variance_pct)) > 20 THEN 'High Risk'
                        WHEN ABS(AVG(variance_pct)) > 10 THEN 'Medium Risk'
                        ELSE 'Low Risk'
                    END as risk_level,

                    -- Financial Impact
                    SUM(ABS(DOLLARAMOUNTHIGH - CAUSATION_HIGH_RECOMMENDATION)) as total_dollar_error,
                    AVG(ABS(DOLLARAMOUNTHIGH - CAUSATION_HIGH_RECOMMENDATION)) as avg_dollar_error

                FROM claims
                WHERE CALCULATED_SEVERITY_SCORE IS NOT NULL
                  AND PRIMARY_INJURY_BY_SEVERITY IS NOT NULL
                  AND variance_pct IS NOT NULL
                GROUP BY
                    severity_level,
                    injury_type,
                    body_part,
                    venue_rating,
                    county,
                    state,
                    impact_on_life,
                    version_id,
                    year
                HAVING claim_count >= 3
                ORDER BY abs_avg_deviation_pct DESC
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_executive_summary")).fetchone()[0]
            logger.info(f"  Done - Created mv_executive_summary ({rows:,} factor combinations)")

            # 2. TOP VARIANCE FACTORS (Top 10 by category)
            logger.info("\n[2/4] Creating mv_top_variance_factors...")
            logger.info("  This shows top 10 high-variance factors by each dimension...")
            conn.execute(text("""
                CREATE TABLE mv_top_variance_factors AS
                SELECT * FROM (
                    -- Top 10 by Severity Level
                    SELECT
                        'Severity' as dimension,
                        severity_level as factor_value,
                        SUM(claim_count) as total_claims,
                        AVG(abs_avg_deviation_pct) as avg_deviation,
                        SUM(total_dollar_error) as total_error,
                        MAX(risk_level) as risk_level,
                        'All' as county,
                        'All' as state,
                        NULL as version_id
                    FROM mv_executive_summary
                    GROUP BY severity_level
                    ORDER BY avg_deviation DESC
                    LIMIT 10
                )

                UNION ALL

                SELECT * FROM (
                    -- Top 10 by Injury Type
                    SELECT
                        'Injury Type' as dimension,
                        injury_type as factor_value,
                        SUM(claim_count) as total_claims,
                        AVG(abs_avg_deviation_pct) as avg_deviation,
                        SUM(total_dollar_error) as total_error,
                        MAX(risk_level) as risk_level,
                        'All' as county,
                        'All' as state,
                        NULL as version_id
                    FROM mv_executive_summary
                    WHERE injury_type IS NOT NULL
                    GROUP BY injury_type
                    ORDER BY avg_deviation DESC
                    LIMIT 10
                )

                UNION ALL

                SELECT * FROM (
                    -- Top 10 by Venue Rating
                    SELECT
                        'Venue Rating' as dimension,
                        venue_rating as factor_value,
                        SUM(claim_count) as total_claims,
                        AVG(abs_avg_deviation_pct) as avg_deviation,
                        SUM(total_dollar_error) as total_error,
                        MAX(risk_level) as risk_level,
                        'All' as county,
                        'All' as state,
                        NULL as version_id
                    FROM mv_executive_summary
                    WHERE venue_rating IS NOT NULL
                    GROUP BY venue_rating
                    ORDER BY avg_deviation DESC
                    LIMIT 10
                )

                UNION ALL

                SELECT * FROM (
                    -- Top 10 by Impact on Life
                    SELECT
                        'Impact on Life' as dimension,
                        CAST(impact_on_life AS TEXT) as factor_value,
                        SUM(claim_count) as total_claims,
                        AVG(abs_avg_deviation_pct) as avg_deviation,
                        SUM(total_dollar_error) as total_error,
                        MAX(risk_level) as risk_level,
                        'All' as county,
                        'All' as state,
                        NULL as version_id
                    FROM mv_executive_summary
                    WHERE impact_on_life IS NOT NULL
                    GROUP BY impact_on_life
                    ORDER BY avg_deviation DESC
                    LIMIT 10
                )

                UNION ALL

                SELECT * FROM (
                    -- Top 10 by County
                    SELECT
                        'County' as dimension,
                        county || ', ' || state as factor_value,
                        SUM(claim_count) as total_claims,
                        AVG(abs_avg_deviation_pct) as avg_deviation,
                        SUM(total_dollar_error) as total_error,
                        MAX(risk_level) as risk_level,
                        county,
                        state,
                        NULL as version_id
                    FROM mv_executive_summary
                    WHERE county IS NOT NULL
                    GROUP BY county, state
                    ORDER BY avg_deviation DESC
                    LIMIT 10
                )
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_top_variance_factors")).fetchone()[0]
            logger.info(f"  Done - Created mv_top_variance_factors ({rows} top factors)")

            # 3. COUNTY COMPARISON VIEW
            logger.info("\n[3/4] Creating mv_county_comparison...")
            logger.info("  This enables comparing similar factors across counties...")
            conn.execute(text("""
                CREATE TABLE mv_county_comparison AS
                SELECT
                    -- Matching Factors (for comparison)
                    severity_level,
                    injury_type,
                    venue_rating,
                    impact_on_life,
                    version_id,

                    -- County Identification
                    county,
                    state,
                    county || ', ' || state as county_full,

                    -- Metrics for Comparison
                    claim_count,
                    abs_avg_deviation_pct as deviation_pct,
                    avg_actual,
                    avg_predicted,
                    avg_dollar_error,
                    total_dollar_error,
                    risk_level,

                    -- Ranking within same factor group
                    ROW_NUMBER() OVER (
                        PARTITION BY severity_level, injury_type, venue_rating, impact_on_life
                        ORDER BY abs_avg_deviation_pct DESC
                    ) as rank_in_group,

                    -- Count how many counties have same factors
                    COUNT(*) OVER (
                        PARTITION BY severity_level, injury_type, venue_rating, impact_on_life
                    ) as counties_with_same_factors

                FROM mv_executive_summary
                WHERE county IS NOT NULL
                  AND claim_count >= 3
                ORDER BY
                    severity_level,
                    injury_type,
                    venue_rating,
                    impact_on_life,
                    deviation_pct DESC
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_county_comparison")).fetchone()[0]
            logger.info(f"  Done - Created mv_county_comparison ({rows:,} county factor combos)")

            # 4. FACTOR COMBINATIONS DETAILED (Enhanced version with VersionID)
            logger.info("\n[4/4] Creating mv_factor_combinations_detailed...")
            logger.info("  This is the detailed version with all filters...")
            conn.execute(text("""
                CREATE TABLE mv_factor_combinations_detailed AS
                SELECT
                    factor_combination,
                    severity_level,
                    injury_type,
                    body_part,
                    venue_rating,
                    county,
                    state,
                    impact_on_life,
                    version_id,
                    year,
                    claim_count,
                    abs_avg_deviation_pct,
                    avg_actual,
                    avg_predicted,
                    avg_dollar_error,
                    total_dollar_error,
                    risk_level,

                    -- Add percentile ranking
                    PERCENT_RANK() OVER (ORDER BY abs_avg_deviation_pct) as deviation_percentile,

                    -- Category for UI display
                    CASE
                        WHEN injury_type IS NOT NULL THEN 'Injury Type'
                        WHEN county IS NOT NULL THEN 'County'
                        WHEN venue_rating IS NOT NULL THEN 'Venue'
                        ELSE 'Other'
                    END as category

                FROM mv_executive_summary
                ORDER BY abs_avg_deviation_pct DESC
                LIMIT 10000
            """))
            rows = conn.execute(text("SELECT COUNT(*) FROM mv_factor_combinations_detailed")).fetchone()[0]
            logger.info(f"  Done - Created mv_factor_combinations_detailed ({rows:,} rows)")

            conn.commit()

            # Show summary statistics
            logger.info("\n" + "=" * 80)
            logger.info("EXECUTIVE SUMMARY VIEWS CREATED SUCCESSFULLY!")
            logger.info("=" * 80)

            # Get top 10 critical factors
            top_10 = conn.execute(text("""
                SELECT factor_combination, abs_avg_deviation_pct, claim_count, risk_level
                FROM mv_executive_summary
                ORDER BY abs_avg_deviation_pct DESC
                LIMIT 10
            """)).fetchall()

            logger.info("\nTop 10 Critical Factor Combinations:")
            logger.info("-" * 80)
            for idx, row in enumerate(top_10, 1):
                logger.info(f"{idx}. {row[0][:60]}...")
                logger.info(f"   Deviation: {row[1]:.2f}% | Claims: {row[2]} | Risk: {row[3]}")

            logger.info("\n" + "=" * 80)
            logger.info("VIEWS SUMMARY:")
            logger.info("=" * 80)
            logger.info("  mv_executive_summary: Multi-factor analysis")
            logger.info("  mv_top_variance_factors: Top 10 by each dimension")
            logger.info("  mv_county_comparison: Compare similar factors across counties")
            logger.info("  mv_factor_combinations_detailed: Filterable by VersionID/Year")
            logger.info("=" * 80)

            return True

    except Exception as e:
        logger.error(f"Error creating executive summary views: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = create_executive_summary_views()
    if success:
        print("\nSUCCESS! Executive Summary views created")
        print("Next: Restart backend and test the new endpoints")
    else:
        print("\nFAILED! Check error messages above")
