-- Refresh All Materialized Views (Snowflake)
-- Uses native REFRESH command

-- Refresh individual views
ALTER MATERIALIZED VIEW mv_year_severity REFRESH;
ALTER MATERIALIZED VIEW mv_county_year REFRESH;
ALTER MATERIALIZED VIEW mv_injury_group REFRESH;
ALTER MATERIALIZED VIEW mv_adjuster_performance REFRESH;
ALTER MATERIALIZED VIEW mv_venue_analysis REFRESH;
ALTER MATERIALIZED VIEW mv_factor_combinations REFRESH;
ALTER MATERIALIZED VIEW mv_kpi_summary REFRESH;

-- Alternatively, suspend and resume to trigger refresh
-- ALTER MATERIALIZED VIEW mv_year_severity SUSPEND;
-- ALTER MATERIALIZED VIEW mv_year_severity RESUME;
