-- Snowflake Native Materialized Views
-- Claims Analytics Dashboard - v2.0
-- Uses native MATERIALIZED VIEW with optional AUTO_REFRESH

-- ==============================================
-- VIEW 1: mv_year_severity
-- Year and severity category aggregations
-- ==============================================
CREATE OR REPLACE MATERIALIZED VIEW mv_year_severity
-- AUTO_REFRESH = TRUE  -- Uncomment for auto-refresh
-- REFRESH_INTERVAL = '1 HOUR'  -- Set refresh interval
AS
SELECT
    YEAR(CLAIMCLOSEDDATE) as year,
    CASE
        WHEN CALCULATED_SEVERITY_SCORE <= 500 THEN 'Low'
        WHEN CALCULATED_SEVERITY_SCORE <= 1500 THEN 'Medium'
        ELSE 'High'
    END as severity_category,
    COUNT(*) as claim_count,
    SUM(DOLLARAMOUNTHIGH) as total_actual_settlement,
    SUM(CAUSATION_HIGH_RECOMMENDATION) as total_predicted_settlement,
    AVG(DOLLARAMOUNTHIGH) as avg_actual_settlement,
    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted_settlement,
    AVG(variance_pct) as avg_variance_pct,
    AVG(SETTLEMENT_DAYS) as avg_settlement_days,
    SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) as overprediction_count,
    SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) as underprediction_count,
    SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) as high_variance_count
FROM claims
WHERE CLAIMCLOSEDDATE IS NOT NULL
  AND CALCULATED_SEVERITY_SCORE IS NOT NULL
GROUP BY YEAR(CLAIMCLOSEDDATE), severity_category;

-- ==============================================
-- VIEW 2: mv_county_year
-- County, state, year aggregations
-- ==============================================
CREATE OR REPLACE MATERIALIZED VIEW mv_county_year AS
SELECT
    COUNTYNAME as county,
    VENUESTATE as state,
    YEAR(CLAIMCLOSEDDATE) as year,
    VENUERATING as venue_rating,
    COUNT(*) as claim_count,
    SUM(DOLLARAMOUNTHIGH) as total_settlement,
    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
    AVG(variance_pct) as avg_variance_pct,
    SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) as high_variance_count,
    (SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100) as high_variance_pct,
    SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) as overprediction_count,
    SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) as underprediction_count
FROM claims
WHERE COUNTYNAME IS NOT NULL
  AND CLAIMCLOSEDDATE IS NOT NULL
GROUP BY COUNTYNAME, VENUESTATE, YEAR(CLAIMCLOSEDDATE), VENUERATING
HAVING COUNT(*) >= 5;

-- ==============================================
-- VIEW 3: mv_injury_group
-- Injury group, type, body part aggregations
-- ==============================================
CREATE OR REPLACE MATERIALIZED VIEW mv_injury_group AS
SELECT
    PRIMARY_INJURYGROUP_CODE_BY_SEVERITY as injury_group,
    PRIMARY_INJURY_BY_SEVERITY as injury_type,
    PRIMARY_BODYPART_BY_SEVERITY as body_part,
    BODY_REGION as body_region,
    CASE
        WHEN CALCULATED_SEVERITY_SCORE <= 500 THEN 'Low'
        WHEN CALCULATED_SEVERITY_SCORE <= 1500 THEN 'Medium'
        ELSE 'High'
    END as severity_category,
    COUNT(*) as claim_count,
    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
    AVG(variance_pct) as avg_variance_pct,
    AVG(SETTLEMENT_DAYS) as avg_settlement_days,
    SUM(DOLLARAMOUNTHIGH) as total_settlement,
    SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) as high_variance_count,
    SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) as overprediction_count,
    SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) as underprediction_count
FROM claims
WHERE PRIMARY_INJURYGROUP_CODE_BY_SEVERITY IS NOT NULL
  AND CALCULATED_SEVERITY_SCORE IS NOT NULL
GROUP BY
    PRIMARY_INJURYGROUP_CODE_BY_SEVERITY,
    PRIMARY_INJURY_BY_SEVERITY,
    PRIMARY_BODYPART_BY_SEVERITY,
    BODY_REGION,
    severity_category
HAVING COUNT(*) >= 5;

-- ==============================================
-- VIEW 4: mv_adjuster_performance
-- Adjuster performance metrics
-- ==============================================
CREATE OR REPLACE MATERIALIZED VIEW mv_adjuster_performance AS
SELECT
    ADJUSTERNAME as adjuster_name,
    COUNT(*) as claim_count,
    AVG(DOLLARAMOUNTHIGH) as avg_actual_settlement,
    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted_settlement,
    AVG(variance_pct) as avg_variance_pct,
    SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END) as high_variance_count,
    (SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100) as high_variance_pct,
    SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END) as overprediction_count,
    SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END) as underprediction_count,
    AVG(SETTLEMENT_DAYS) as avg_settlement_days
FROM claims
WHERE ADJUSTERNAME IS NOT NULL
  AND ADJUSTERNAME != ''
  AND ADJUSTERNAME != 'System System'
GROUP BY ADJUSTERNAME
HAVING COUNT(*) >= 10;

-- ==============================================
-- VIEW 5: mv_venue_analysis
-- Venue rating analysis by county
-- ==============================================
CREATE OR REPLACE MATERIALIZED VIEW mv_venue_analysis AS
SELECT
    VENUERATING as venue_rating,
    VENUESTATE as state,
    COUNTYNAME as county,
    COUNT(*) as claim_count,
    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
    AVG(variance_pct) as avg_variance_pct,
    AVG(VENUERATINGPOINT) as avg_venue_rating_point,
    (SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100) as high_variance_pct
FROM claims
WHERE VENUERATING IS NOT NULL
  AND COUNTYNAME IS NOT NULL
GROUP BY VENUERATING, VENUESTATE, COUNTYNAME
HAVING COUNT(*) >= 10;

-- ==============================================
-- VIEW 6: mv_factor_combinations
-- Factor combination variance drivers
-- ==============================================
CREATE OR REPLACE MATERIALIZED VIEW mv_factor_combinations AS
SELECT
    CONCAT('County: ', COUNTYNAME, ': ', VENUESTATE, ', ', TO_CHAR(YEAR(CLAIMCLOSEDDATE))) as factor,
    'Driver' as category,
    COUNT(*) as claims,
    AVG(variance_pct) as avg_deviation,
    ABS(AVG(variance_pct)) as abs_avg_deviation,
    CASE
        WHEN ABS(AVG(variance_pct)) > 30 THEN 'Action Needed'
        WHEN ABS(AVG(variance_pct)) > 15 THEN 'Monitor'
        ELSE 'Good'
    END as status,
    YEAR(CLAIMCLOSEDDATE) as year,
    COUNTYNAME as county,
    VENUESTATE as state
FROM claims
WHERE COUNTYNAME IS NOT NULL
  AND CLAIMCLOSEDDATE IS NOT NULL
  AND variance_pct IS NOT NULL
GROUP BY COUNTYNAME, VENUESTATE, YEAR(CLAIMCLOSEDDATE)
HAVING COUNT(*) >= 1

UNION ALL

SELECT
    PRIMARY_INJURY_BY_SEVERITY as factor,
    'Injury Type' as category,
    COUNT(*) as claims,
    AVG(variance_pct) as avg_deviation,
    ABS(AVG(variance_pct)) as abs_avg_deviation,
    CASE
        WHEN ABS(AVG(variance_pct)) > 30 THEN 'Action Needed'
        WHEN ABS(AVG(variance_pct)) > 15 THEN 'Monitor'
        ELSE 'Good'
    END as status,
    NULL as year,
    NULL as county,
    PRIMARY_BODYPART_BY_SEVERITY as state
FROM claims
WHERE PRIMARY_INJURY_BY_SEVERITY IS NOT NULL
  AND variance_pct IS NOT NULL
GROUP BY PRIMARY_INJURY_BY_SEVERITY, PRIMARY_BODYPART_BY_SEVERITY
HAVING COUNT(*) >= 5

ORDER BY abs_avg_deviation DESC
LIMIT 1000;

-- ==============================================
-- VIEW 7: mv_kpi_summary
-- Overall KPI summary (single row)
-- ==============================================
CREATE OR REPLACE MATERIALIZED VIEW mv_kpi_summary AS
SELECT
    COUNT(*) as total_claims,
    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
    AVG(SETTLEMENT_DAYS) as avg_days,
    AVG(ABS(variance_pct)) as avg_abs_variance,
    (SUM(CASE WHEN ABS(variance_pct) > 20 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100) as high_variance_pct,
    (SUM(CASE WHEN variance_pct < 0 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100) as overprediction_rate,
    (SUM(CASE WHEN variance_pct > 0 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100) as underprediction_rate
FROM claims;

-- ==============================================
-- REFRESH COMMANDS
-- Run these to manually refresh materialized views
-- ==============================================

-- Refresh all views:
-- ALTER MATERIALIZED VIEW mv_year_severity REFRESH;
-- ALTER MATERIALIZED VIEW mv_county_year REFRESH;
-- ALTER MATERIALIZED VIEW mv_injury_group REFRESH;
-- ALTER MATERIALIZED VIEW mv_adjuster_performance REFRESH;
-- ALTER MATERIALIZED VIEW mv_venue_analysis REFRESH;
-- ALTER MATERIALIZED VIEW mv_factor_combinations REFRESH;
-- ALTER MATERIALIZED VIEW mv_kpi_summary REFRESH;
