-- SQLite Index Creation Script
-- Claims Analytics Dashboard - v2.0
-- Optimized for 5M+ records with composite indexes for common query patterns

-- =====================================================
-- INDEXES FOR: claims table
-- =====================================================

-- Single Column Indexes
CREATE INDEX IF NOT EXISTS idx_claims_claimid ON claims(CLAIMID);
CREATE INDEX IF NOT EXISTS idx_claims_versionid ON claims(VERSIONID);
CREATE INDEX IF NOT EXISTS idx_claims_closedate ON claims(CLAIMCLOSEDDATE);
CREATE INDEX IF NOT EXISTS idx_claims_dollaramount ON claims(DOLLARAMOUNTHIGH);
CREATE INDEX IF NOT EXISTS idx_claims_adjustername ON claims(ADJUSTERNAME);
CREATE INDEX IF NOT EXISTS idx_claims_iol ON claims(IOL);
CREATE INDEX IF NOT EXISTS idx_claims_county ON claims(COUNTYNAME);
CREATE INDEX IF NOT EXISTS idx_claims_state ON claims(VENUESTATE);
CREATE INDEX IF NOT EXISTS idx_claims_venuerating ON claims(VENUERATING);
CREATE INDEX IF NOT EXISTS idx_claims_severity_score ON claims(SEVERITY_SCORE);
CREATE INDEX IF NOT EXISTS idx_claims_caution_level ON claims(CAUTION_LEVEL);
CREATE INDEX IF NOT EXISTS idx_claims_variance ON claims(variance_pct);
CREATE INDEX IF NOT EXISTS idx_claims_calc_severity ON claims(CALCULATED_SEVERITY_SCORE);
CREATE INDEX IF NOT EXISTS idx_claims_calc_causation ON claims(CALCULATED_CAUSATION_SCORE);
CREATE INDEX IF NOT EXISTS idx_claims_injury_by_severity ON claims(PRIMARY_INJURYGROUP_CODE_BY_SEVERITY);
CREATE INDEX IF NOT EXISTS idx_claims_injury_by_causation ON claims(PRIMARY_INJURYGROUP_CODE_BY_CAUSATION);
CREATE INDEX IF NOT EXISTS idx_claims_injury_severity_score ON claims(PRIMARY_INJURY_SEVERITY_SCORE);
CREATE INDEX IF NOT EXISTS idx_claims_injury_causation_score ON claims(PRIMARY_INJURY_CAUSATION_SCORE);

-- Composite Indexes for Venue Shift Analysis
CREATE INDEX IF NOT EXISTS idx_county_venue
    ON claims(COUNTYNAME, VENUERATING);

CREATE INDEX IF NOT EXISTS idx_county_venue_injury
    ON claims(COUNTYNAME, VENUERATING, PRIMARY_INJURYGROUP_CODE);

CREATE INDEX IF NOT EXISTS idx_county_venue_injury_severity
    ON claims(COUNTYNAME, VENUERATING, PRIMARY_INJURYGROUP_CODE, CAUTION_LEVEL);

CREATE INDEX IF NOT EXISTS idx_date_venue
    ON claims(CLAIMCLOSEDDATE, VENUERATING);

CREATE INDEX IF NOT EXISTS idx_date_county
    ON claims(CLAIMCLOSEDDATE, COUNTYNAME);

CREATE INDEX IF NOT EXISTS idx_venue_state
    ON claims(VENUESTATE, VENUERATING);

-- Composite Indexes for Adjuster Performance Analysis
CREATE INDEX IF NOT EXISTS idx_adjuster_date
    ON claims(ADJUSTERNAME, CLAIMCLOSEDDATE);

CREATE INDEX IF NOT EXISTS idx_adjuster_variance
    ON claims(ADJUSTERNAME, variance_pct);

-- Composite Indexes for Overview and Filtering
CREATE INDEX IF NOT EXISTS idx_date_variance
    ON claims(CLAIMCLOSEDDATE, variance_pct);

CREATE INDEX IF NOT EXISTS idx_injury_severity_caution
    ON claims(PRIMARY_INJURYGROUP_CODE, CAUTION_LEVEL, IOL);

-- Composite Indexes for Multi-Tier Injury Analysis
CREATE INDEX IF NOT EXISTS idx_primary_severity_by_severity
    ON claims(PRIMARY_INJURYGROUP_CODE_BY_SEVERITY, PRIMARY_INJURY_SEVERITY_SCORE);

CREATE INDEX IF NOT EXISTS idx_primary_causation_by_causation
    ON claims(PRIMARY_INJURYGROUP_CODE_BY_CAUSATION, PRIMARY_INJURY_CAUSATION_SCORE);

CREATE INDEX IF NOT EXISTS idx_calculated_scores
    ON claims(CALCULATED_SEVERITY_SCORE, CALCULATED_CAUSATION_SCORE);

-- Composite Index for Model Performance Analysis
CREATE INDEX IF NOT EXISTS idx_model_performance
    ON claims(PRIMARY_INJURYGROUP_CODE_BY_SEVERITY, variance_pct, CALCULATED_SEVERITY_SCORE);

-- =====================================================
-- INDEXES FOR: ssnb table
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_ssnb_claimid ON ssnb(CLAIMID);
CREATE INDEX IF NOT EXISTS idx_ssnb_severity ON ssnb(PRIMARY_SEVERITY_SCORE);
CREATE INDEX IF NOT EXISTS idx_ssnb_causation ON ssnb(PRIMARY_CAUSATION_SCORE);

-- =====================================================
-- INDEXES FOR: weights table
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_weights_factor_name ON weights(factor_name);
CREATE INDEX IF NOT EXISTS idx_weights_category ON weights(category);

-- =====================================================
-- INDEXES FOR: venue_statistics table
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_venue_stats_rating ON venue_statistics(VENUERATING);
CREATE INDEX IF NOT EXISTS idx_venue_stats_severity ON venue_statistics(SEVERITY_CATEGORY);
CREATE INDEX IF NOT EXISTS idx_venue_stats_causation ON venue_statistics(CAUSATION_CATEGORY);
CREATE INDEX IF NOT EXISTS idx_venue_stats_iol ON venue_statistics(IOL);
CREATE INDEX IF NOT EXISTS idx_venue_stats_error ON venue_statistics(mean_absolute_error);
CREATE INDEX IF NOT EXISTS idx_venue_stats_sample_size ON venue_statistics(sample_size);

-- Composite Indexes
CREATE INDEX IF NOT EXISTS idx_venue_lookup
    ON venue_statistics(VENUERATING, SEVERITY_CATEGORY, CAUSATION_CATEGORY, IOL);

CREATE INDEX IF NOT EXISTS idx_error_ranking
    ON venue_statistics(mean_absolute_error, sample_size);

CREATE INDEX IF NOT EXISTS idx_venue_category
    ON venue_statistics(VENUERATING, SEVERITY_CATEGORY);

-- =====================================================
-- INDEXES FOR: aggregated_cache table
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_cache_key ON aggregated_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_type ON aggregated_cache(cache_type);
CREATE INDEX IF NOT EXISTS idx_cache_type_updated
    ON aggregated_cache(cache_type, updated_at);

-- =====================================================
-- ANALYZE for Query Optimization
-- =====================================================
-- Run ANALYZE to update query planner statistics
ANALYZE;
