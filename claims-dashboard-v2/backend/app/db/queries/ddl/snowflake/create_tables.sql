-- Snowflake Table Creation Script
-- Claims Analytics Dashboard - v2.0
-- Optimized for large-scale analytics with proper Snowflake types

-- ==============================================
-- TABLE: claims
-- Main claims table storing all claim data
-- ==============================================
CREATE OR REPLACE TABLE claims (
    -- Primary Key
    id NUMBER AUTOINCREMENT PRIMARY KEY,

    -- Core Identifiers
    CLAIMID NUMBER NOT NULL,
    EXPSR_NBR VARCHAR(50),
    VERSIONID NUMBER,
    RN NUMBER,

    -- Dates (using proper DATE type in Snowflake)
    CLAIMCLOSEDDATE DATE,
    INCIDENTDATE DATE,
    DURATIONTOREPORT FLOAT,

    -- Financial Fields
    CAUSATION_HIGH_RECOMMENDATION FLOAT,  -- Predicted settlement
    SETTLEMENTAMOUNT NUMBER,
    DOLLARAMOUNTHIGH FLOAT,  -- Actual settlement amount
    GENERALS FLOAT,

    -- Injury Information - Legacy Single-Tier Structure
    ALL_BODYPARTS VARCHAR,
    ALL_INJURIES VARCHAR,
    ALL_INJURYGROUP_CODES VARCHAR,
    ALL_INJURYGROUP_TEXTS VARCHAR,
    PRIMARY_INJURY VARCHAR(200),
    PRIMARY_BODYPART VARCHAR(200),
    PRIMARY_INJURYGROUP_CODE VARCHAR(50),
    INJURY_COUNT NUMBER,
    BODYPART_COUNT NUMBER,
    INJURYGROUP_COUNT NUMBER,

    -- Multi-Tier Injury System - By SEVERITY Ranking
    PRIMARY_INJURY_BY_SEVERITY VARCHAR(200),
    PRIMARY_BODYPART_BY_SEVERITY VARCHAR(200),
    PRIMARY_INJURYGROUP_CODE_BY_SEVERITY VARCHAR(50),
    PRIMARY_INJURY_SEVERITY_SCORE FLOAT,
    PRIMARY_INJURY_CAUSATION_SCORE_BY_SEVERITY FLOAT,

    SECONDARY_INJURY_BY_SEVERITY VARCHAR(200),
    SECONDARY_BODYPART_BY_SEVERITY VARCHAR(200),
    SECONDARY_INJURYGROUP_CODE_BY_SEVERITY VARCHAR(50),
    SECONDARY_INJURY_SEVERITY_SCORE FLOAT,
    SECONDARY_INJURY_CAUSATION_SCORE_BY_SEVERITY FLOAT,

    TERTIARY_INJURY_BY_SEVERITY VARCHAR(200),
    TERTIARY_BODYPART_BY_SEVERITY VARCHAR(200),
    TERTIARY_INJURY_SEVERITY_SCORE FLOAT,
    TERTIARY_INJURY_CAUSATION_SCORE_BY_SEVERITY FLOAT,

    -- Multi-Tier Injury System - By CAUSATION Ranking
    PRIMARY_INJURY_BY_CAUSATION VARCHAR(200),
    PRIMARY_BODYPART_BY_CAUSATION VARCHAR(200),
    PRIMARY_INJURYGROUP_CODE_BY_CAUSATION VARCHAR(50),
    PRIMARY_INJURY_CAUSATION_SCORE FLOAT,
    PRIMARY_INJURY_SEVERITY_SCORE_BY_CAUSATION FLOAT,

    SECONDARY_INJURY_BY_CAUSATION VARCHAR(200),
    SECONDARY_BODYPART_BY_CAUSATION VARCHAR(200),
    SECONDARY_INJURYGROUP_CODE_BY_CAUSATION VARCHAR(50),
    SECONDARY_INJURY_CAUSATION_SCORE FLOAT,
    SECONDARY_INJURY_SEVERITY_SCORE_BY_CAUSATION FLOAT,

    TERTIARY_INJURY_BY_CAUSATION VARCHAR(200),
    TERTIARY_BODYPART_BY_CAUSATION VARCHAR(200),
    TERTIARY_INJURY_CAUSATION_SCORE FLOAT,
    TERTIARY_INJURY_SEVERITY_SCORE_BY_CAUSATION FLOAT,

    -- Person Information
    HASATTORNEY BOOLEAN,  -- Using native BOOLEAN type
    AGE NUMBER,
    GENDER VARCHAR(10),
    OCCUPATION_AVAILABLE NUMBER,
    OCCUPATION VARCHAR(200),
    ADJUSTERNAME VARCHAR(100),

    -- Location and Venue
    IOL NUMBER,  -- Impact on Life
    COUNTYNAME VARCHAR(100),
    VENUESTATE VARCHAR(50),
    VENUERATINGTEXT VARCHAR(50),
    VENUERATINGPOINT FLOAT,
    RATINGWEIGHT FLOAT,
    VENUERATING VARCHAR(50),
    VULNERABLECLAIMANT VARCHAR(50),
    BODY_REGION VARCHAR(100),

    -- Settlement Timing
    SETTLEMENT_DAYS NUMBER,
    SETTLEMENT_MONTHS NUMBER,
    SETTLEMENT_YEARS FLOAT,
    SETTLEMENT_SPEED_CATEGORY VARCHAR(50),

    -- Calculated Fields
    SEVERITY_SCORE FLOAT,
    CAUTION_LEVEL VARCHAR(50),
    variance_pct FLOAT,  -- (actual - predicted) / predicted * 100
    CALCULATED_SEVERITY_SCORE FLOAT,
    CALCULATED_CAUSATION_SCORE FLOAT,

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
)
COMMENT = 'Main claims table - 5M+ records with multi-tier injury ranking';

-- ==============================================
-- TABLE: ssnb
-- Single injury, Soft tissue, Neck/Back claims
-- Used for weight recalibration
-- ==============================================
CREATE OR REPLACE TABLE ssnb (
    -- Primary Key
    id NUMBER AUTOINCREMENT PRIMARY KEY,

    -- Core Identifiers
    CLAIMID NUMBER NOT NULL,
    VERSIONID NUMBER,
    EXPSR_NBR VARCHAR(50),

    -- Financial
    CAUSATION_HIGH_RECOMMENDATION FLOAT,
    DOLLARAMOUNTHIGH FLOAT,

    -- Venue
    VENUERATING VARCHAR(50),
    RATINGWEIGHT FLOAT,
    VENUERATINGTEXT VARCHAR(100),
    VENUERATINGPOINT FLOAT,

    -- Dates
    INCIDENTDATE DATE,
    CLAIMCLOSEDDATE DATE,

    -- Demographics
    AGE NUMBER,
    GENDER NUMBER,
    HASATTORNEY BOOLEAN,
    IOL NUMBER,
    ADJUSTERNAME VARCHAR(100),
    OCCUPATION VARCHAR(200),

    -- Location
    COUNTYNAME VARCHAR(100),
    VENUESTATE VARCHAR(50),
    VULNERABLECLAIMANT BOOLEAN,

    -- Fixed Injury Type for SSNB
    PRIMARY_INJURY VARCHAR(200),
    PRIMARY_BODYPART VARCHAR(200),
    PRIMARY_INJURY_GROUP VARCHAR(200),

    -- Scores
    PRIMARY_SEVERITY_SCORE FLOAT,
    PRIMARY_CAUSATION_SCORE FLOAT,

    -- Clinical Factors - FLOAT VALUES (not categorical!)
    Causation_Compliance FLOAT,
    Clinical_Findings FLOAT,
    Consistent_Mechanism FLOAT,
    Injury_Location FLOAT,
    Movement_Restriction FLOAT,
    Pain_Management FLOAT,
    Prior_Treatment FLOAT,
    Symptom_Timeline FLOAT,
    Treatment_Course FLOAT,
    Treatment_Delays FLOAT,
    Treatment_Period_Considered FLOAT,
    Vehicle_Impact FLOAT
)
COMMENT = 'SSNB subset - Single injury, Soft tissue, Neck/Back claims for recalibration';

-- ==============================================
-- TABLE: weights
-- Feature weights configuration
-- ==============================================
CREATE OR REPLACE TABLE weights (
    -- Primary Key
    id NUMBER AUTOINCREMENT PRIMARY KEY,

    -- Weight Configuration
    factor_name VARCHAR(200) NOT NULL UNIQUE,
    base_weight FLOAT NOT NULL,
    min_weight FLOAT NOT NULL,
    max_weight FLOAT NOT NULL,
    category VARCHAR(100),
    description VARCHAR
)
COMMENT = 'Model feature weights configuration';

-- ==============================================
-- TABLE: venue_statistics
-- Pre-computed venue rating statistics
-- ==============================================
CREATE OR REPLACE TABLE venue_statistics (
    -- Primary Key
    id NUMBER AUTOINCREMENT PRIMARY KEY,

    -- Grouping Dimensions
    VENUERATING VARCHAR(50) NOT NULL,
    VENUERATINGTEXT VARCHAR(100),
    RATINGWEIGHT FLOAT,
    SEVERITY_CATEGORY VARCHAR(20) NOT NULL,
    CAUSATION_CATEGORY VARCHAR(20) NOT NULL,
    IOL NUMBER NOT NULL,

    -- Actual Settlement Statistics
    mean_actual FLOAT,
    median_actual FLOAT,
    stddev_actual FLOAT,
    min_actual FLOAT,
    max_actual FLOAT,

    -- Predicted Statistics
    mean_predicted FLOAT,
    median_predicted FLOAT,
    mode_predicted FLOAT,
    stddev_predicted FLOAT,

    -- Error Metrics
    mean_absolute_error FLOAT,
    median_absolute_error FLOAT,
    mean_error_pct FLOAT,

    -- Statistical Measures
    coefficient_of_variation FLOAT,

    -- Confidence Metrics
    sample_size NUMBER NOT NULL,
    confidence_interval_lower FLOAT,
    confidence_interval_upper FLOAT,

    -- Data Quality
    last_updated TIMESTAMP_NTZ,
    data_period_start VARCHAR(50),
    data_period_end VARCHAR(50)
)
COMMENT = 'Pre-computed venue statistics for fast recommendations';

-- ==============================================
-- TABLE: aggregated_cache
-- Cache for pre-computed aggregations
-- ==============================================
CREATE OR REPLACE TABLE aggregated_cache (
    -- Primary Key
    id NUMBER AUTOINCREMENT PRIMARY KEY,

    -- Cache Configuration
    cache_key VARCHAR(200) NOT NULL UNIQUE,
    cache_type VARCHAR(100),
    data_json VARIANT,  -- Using VARIANT for JSON in Snowflake
    created_at TIMESTAMP_NTZ,
    updated_at TIMESTAMP_NTZ
)
COMMENT = 'Cache for pre-computed dashboard aggregations';

-- ==============================================
-- CLUSTERING KEYS for Performance
-- ==============================================
-- Cluster claims table by commonly filtered columns
ALTER TABLE claims CLUSTER BY (CLAIMCLOSEDDATE, COUNTYNAME, VENUERATING);
ALTER TABLE venue_statistics CLUSTER BY (VENUERATING, SEVERITY_CATEGORY);
