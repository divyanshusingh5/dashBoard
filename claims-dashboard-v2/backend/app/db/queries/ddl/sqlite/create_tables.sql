-- SQLite Table Creation Script
-- Claims Analytics Dashboard - v2.0
-- Optimized for 5M+ records with proper indexing

-- ==============================================
-- TABLE: claims
-- Main claims table storing all claim data
-- ==============================================
CREATE TABLE IF NOT EXISTS claims (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Core Identifiers
    CLAIMID INTEGER NOT NULL,
    EXPSR_NBR VARCHAR(50),
    VERSIONID INTEGER,
    RN INTEGER,

    -- Dates (stored as strings, parsed when needed)
    CLAIMCLOSEDDATE VARCHAR(50),
    INCIDENTDATE VARCHAR(50),
    DURATIONTOREPORT REAL,

    -- Financial Fields
    CAUSATION_HIGH_RECOMMENDATION REAL,  -- Predicted settlement
    SETTLEMENTAMOUNT INTEGER,
    DOLLARAMOUNTHIGH REAL,  -- Actual settlement amount
    GENERALS REAL,

    -- Injury Information - Legacy Single-Tier Structure
    ALL_BODYPARTS TEXT,
    ALL_INJURIES TEXT,
    ALL_INJURYGROUP_CODES TEXT,
    ALL_INJURYGROUP_TEXTS TEXT,
    PRIMARY_INJURY VARCHAR(200),
    PRIMARY_BODYPART VARCHAR(200),
    PRIMARY_INJURYGROUP_CODE VARCHAR(50),
    INJURY_COUNT INTEGER,
    BODYPART_COUNT INTEGER,
    INJURYGROUP_COUNT INTEGER,

    -- Multi-Tier Injury System - By SEVERITY Ranking
    PRIMARY_INJURY_BY_SEVERITY VARCHAR(200),
    PRIMARY_BODYPART_BY_SEVERITY VARCHAR(200),
    PRIMARY_INJURYGROUP_CODE_BY_SEVERITY VARCHAR(50),
    PRIMARY_INJURY_SEVERITY_SCORE REAL,
    PRIMARY_INJURY_CAUSATION_SCORE_BY_SEVERITY REAL,

    SECONDARY_INJURY_BY_SEVERITY VARCHAR(200),
    SECONDARY_BODYPART_BY_SEVERITY VARCHAR(200),
    SECONDARY_INJURYGROUP_CODE_BY_SEVERITY VARCHAR(50),
    SECONDARY_INJURY_SEVERITY_SCORE REAL,
    SECONDARY_INJURY_CAUSATION_SCORE_BY_SEVERITY REAL,

    TERTIARY_INJURY_BY_SEVERITY VARCHAR(200),
    TERTIARY_BODYPART_BY_SEVERITY VARCHAR(200),
    TERTIARY_INJURY_SEVERITY_SCORE REAL,
    TERTIARY_INJURY_CAUSATION_SCORE_BY_SEVERITY REAL,

    -- Multi-Tier Injury System - By CAUSATION Ranking
    PRIMARY_INJURY_BY_CAUSATION VARCHAR(200),
    PRIMARY_BODYPART_BY_CAUSATION VARCHAR(200),
    PRIMARY_INJURYGROUP_CODE_BY_CAUSATION VARCHAR(50),
    PRIMARY_INJURY_CAUSATION_SCORE REAL,
    PRIMARY_INJURY_SEVERITY_SCORE_BY_CAUSATION REAL,

    SECONDARY_INJURY_BY_CAUSATION VARCHAR(200),
    SECONDARY_BODYPART_BY_CAUSATION VARCHAR(200),
    SECONDARY_INJURYGROUP_CODE_BY_CAUSATION VARCHAR(50),
    SECONDARY_INJURY_CAUSATION_SCORE REAL,
    SECONDARY_INJURY_SEVERITY_SCORE_BY_CAUSATION REAL,

    TERTIARY_INJURY_BY_CAUSATION VARCHAR(200),
    TERTIARY_BODYPART_BY_CAUSATION VARCHAR(200),
    TERTIARY_INJURY_CAUSATION_SCORE REAL,
    TERTIARY_INJURY_SEVERITY_SCORE_BY_CAUSATION REAL,

    -- Person Information
    HASATTORNEY VARCHAR(10),
    AGE INTEGER,
    GENDER VARCHAR(10),
    OCCUPATION_AVAILABLE INTEGER,
    OCCUPATION VARCHAR(200),
    ADJUSTERNAME VARCHAR(100),

    -- Location and Venue
    IOL INTEGER,  -- Impact on Life
    COUNTYNAME VARCHAR(100),
    VENUESTATE VARCHAR(50),
    VENUERATINGTEXT VARCHAR(50),
    VENUERATINGPOINT REAL,
    RATINGWEIGHT REAL,
    VENUERATING VARCHAR(50),
    VULNERABLECLAIMANT VARCHAR(50),
    BODY_REGION VARCHAR(100),

    -- Settlement Timing
    SETTLEMENT_DAYS INTEGER,
    SETTLEMENT_MONTHS INTEGER,
    SETTLEMENT_YEARS REAL,
    SETTLEMENT_SPEED_CATEGORY VARCHAR(50),

    -- Calculated Fields
    SEVERITY_SCORE REAL,
    CAUTION_LEVEL VARCHAR(50),
    variance_pct REAL,  -- (actual - predicted) / predicted * 100
    CALCULATED_SEVERITY_SCORE REAL,
    CALCULATED_CAUSATION_SCORE REAL,

    -- Clinical Factors (40+ feature columns)
    Advanced_Pain_Treatment VARCHAR(200),
    Causation_Compliance VARCHAR(200),
    Clinical_Findings VARCHAR(200),
    Cognitive_Symptoms VARCHAR(200),
    Complete_Disability_Duration VARCHAR(200),
    Concussion_Diagnosis VARCHAR(200),
    Consciousness_Impact VARCHAR(200),
    Consistent_Mechanism VARCHAR(200),
    Dental_Procedure VARCHAR(200),
    Dental_Treatment VARCHAR(200),
    Dental_Visibility VARCHAR(200),
    Emergency_Treatment VARCHAR(200),
    Fixation_Method VARCHAR(200),
    Head_Trauma VARCHAR(200),
    Immobilization_Used VARCHAR(200),
    Injury_Count_Feature VARCHAR(200),
    Injury_Extent VARCHAR(200),
    Injury_Laterality VARCHAR(200),
    Injury_Location VARCHAR(200),
    Injury_Type VARCHAR(200),
    Mobility_Assistance VARCHAR(200),
    Movement_Restriction VARCHAR(200),
    Nerve_Involvement VARCHAR(200),
    Pain_Management VARCHAR(200),
    Partial_Disability_Duration VARCHAR(200),
    Physical_Symptoms VARCHAR(200),
    Physical_Therapy VARCHAR(200),
    Prior_Treatment VARCHAR(200),
    Recovery_Duration VARCHAR(200),
    Repair_Type VARCHAR(200),
    Respiratory_Issues VARCHAR(200),
    Soft_Tissue_Damage VARCHAR(200),
    Special_Treatment VARCHAR(200),
    Surgical_Intervention VARCHAR(200),
    Symptom_Timeline VARCHAR(200),
    Treatment_Compliance VARCHAR(200),
    Treatment_Course VARCHAR(200),
    Treatment_Delays VARCHAR(200),
    Treatment_Level VARCHAR(200),
    Treatment_Period_Considered VARCHAR(200),
    Vehicle_Impact VARCHAR(200)
);

-- ==============================================
-- TABLE: ssnb
-- Single injury, Soft tissue, Neck/Back claims
-- Used for weight recalibration
-- ==============================================
CREATE TABLE IF NOT EXISTS ssnb (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Core Identifiers
    CLAIMID INTEGER NOT NULL,
    VERSIONID INTEGER,
    EXPSR_NBR VARCHAR(50),

    -- Financial
    CAUSATION_HIGH_RECOMMENDATION REAL,
    DOLLARAMOUNTHIGH REAL,

    -- Venue
    VENUERATING VARCHAR(50),
    RATINGWEIGHT REAL,
    VENUERATINGTEXT VARCHAR(100),
    VENUERATINGPOINT REAL,

    -- Dates
    INCIDENTDATE VARCHAR(50),
    CLAIMCLOSEDDATE VARCHAR(50),

    -- Demographics
    AGE INTEGER,
    GENDER INTEGER,
    HASATTORNEY INTEGER,
    IOL INTEGER,
    ADJUSTERNAME VARCHAR(100),
    OCCUPATION VARCHAR(200),

    -- Location
    COUNTYNAME VARCHAR(100),
    VENUESTATE VARCHAR(50),
    VULNERABLECLAIMANT INTEGER,  -- 0/1 boolean

    -- Fixed Injury Type for SSNB
    PRIMARY_INJURY VARCHAR(200),  -- Always 'Sprain/Strain'
    PRIMARY_BODYPART VARCHAR(200),  -- Always 'Neck/Back'
    PRIMARY_INJURY_GROUP VARCHAR(200),  -- Always 'Sprain/Strain, Neck/Back'

    -- Scores
    PRIMARY_SEVERITY_SCORE REAL,
    PRIMARY_CAUSATION_SCORE REAL,

    -- Clinical Factors - FLOAT VALUES (not categorical!)
    Causation_Compliance REAL,
    Clinical_Findings REAL,
    Consistent_Mechanism REAL,
    Injury_Location REAL,
    Movement_Restriction REAL,
    Pain_Management REAL,
    Prior_Treatment REAL,
    Symptom_Timeline REAL,
    Treatment_Course REAL,
    Treatment_Delays REAL,
    Treatment_Period_Considered REAL,
    Vehicle_Impact REAL
);

-- ==============================================
-- TABLE: weights
-- Feature weights configuration
-- ==============================================
CREATE TABLE IF NOT EXISTS weights (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Weight Configuration
    factor_name VARCHAR(200) NOT NULL UNIQUE,
    base_weight REAL NOT NULL,
    min_weight REAL NOT NULL,
    max_weight REAL NOT NULL,
    category VARCHAR(100),
    description TEXT
);

-- ==============================================
-- TABLE: venue_statistics
-- Pre-computed venue rating statistics
-- ==============================================
CREATE TABLE IF NOT EXISTS venue_statistics (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Grouping Dimensions
    VENUERATING VARCHAR(50) NOT NULL,
    VENUERATINGTEXT VARCHAR(100),
    RATINGWEIGHT REAL,
    SEVERITY_CATEGORY VARCHAR(20) NOT NULL,  -- Low/Medium/High
    CAUSATION_CATEGORY VARCHAR(20) NOT NULL,  -- Low/Medium/High
    IOL INTEGER NOT NULL,

    -- Actual Settlement Statistics
    mean_actual REAL,
    median_actual REAL,
    stddev_actual REAL,
    min_actual REAL,
    max_actual REAL,

    -- Predicted Statistics
    mean_predicted REAL,
    median_predicted REAL,
    mode_predicted REAL,
    stddev_predicted REAL,

    -- Error Metrics
    mean_absolute_error REAL,
    median_absolute_error REAL,
    mean_error_pct REAL,

    -- Statistical Measures
    coefficient_of_variation REAL,  -- stddev/mean - predictability measure

    -- Confidence Metrics
    sample_size INTEGER NOT NULL,
    confidence_interval_lower REAL,
    confidence_interval_upper REAL,

    -- Data Quality
    last_updated DATETIME,
    data_period_start VARCHAR(50),
    data_period_end VARCHAR(50)
);

-- ==============================================
-- TABLE: aggregated_cache
-- Cache for pre-computed aggregations
-- ==============================================
CREATE TABLE IF NOT EXISTS aggregated_cache (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Cache Configuration
    cache_key VARCHAR(200) NOT NULL UNIQUE,
    cache_type VARCHAR(100),  -- 'county_year', 'venue', etc.
    data_json TEXT,  -- Stored as JSON
    created_at DATETIME,
    updated_at DATETIME
);
