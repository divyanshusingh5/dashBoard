-- Refresh All Materialized Views (SQLite)
-- Delete all data and re-populate from claims table

-- This script should be run periodically to refresh the materialized views
-- Execution time depends on claims table size (5M+ rows = 2-5 minutes)

BEGIN TRANSACTION;

-- Drop and recreate all views for complete refresh
-- This is more reliable than DELETE + INSERT for large datasets

DROP TABLE IF EXISTS mv_year_severity;
DROP TABLE IF EXISTS mv_county_year;
DROP TABLE IF EXISTS mv_injury_group;
DROP TABLE IF EXISTS mv_adjuster_performance;
DROP TABLE IF EXISTS mv_venue_analysis;
DROP TABLE IF EXISTS mv_factor_combinations;
DROP TABLE IF EXISTS mv_kpi_summary;

-- Note: The actual view creation SQL should be loaded from create_materialized_views.sql
-- This is a placeholder showing the pattern

-- After this, run: sqlite3 app/db/claims_analytics.db < app/db/queries/ddl/sqlite/create_materialized_views.sql

COMMIT;

-- Update query planner statistics
ANALYZE;
