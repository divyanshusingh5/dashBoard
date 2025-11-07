"""
SQLite Database Schema for Claims Analytics
Optimized for 2M+ rows with proper indexing
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, Text, Index, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

Base = declarative_base()

class Claim(Base):
    """
    Main claims table - stores all claim data from dat.csv
    Optimized for fast querying on common filter fields
    """
    __tablename__ = 'claims'

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Core identifiers - ACTUAL DATA FORMAT
    CLAIMID = Column(Integer, unique=True, nullable=False, index=True)
    EXPSR_NBR = Column(String(50))

    # Core fields
    VERSIONID = Column(Integer, index=True)
    CLAIMCLOSEDDATE = Column(String(50), index=True)  # Store as string, parse when needed
    INCIDENTDATE = Column(String(50))
    DURATIONTOREPORT = Column(Float)

    # Financial - ACTUAL DATA FORMAT
    CAUSATION_HIGH_RECOMMENDATION = Column(Float)  # Predicted settlement
    SETTLEMENTAMOUNT = Column(Integer)
    DOLLARAMOUNTHIGH = Column(Float, index=True)  # Actual settlement amount
    GENERALS = Column(Float)

    # Injury information - Legacy single-tier structure (kept for backward compatibility)
    ALL_BODYPARTS = Column(Text)
    ALL_INJURIES = Column(Text)
    ALL_INJURYGROUP_CODES = Column(Text)
    ALL_INJURYGROUP_TEXTS = Column(Text)
    PRIMARY_INJURY = Column(String(200))
    PRIMARY_BODYPART = Column(String(200))
    PRIMARY_INJURYGROUP_CODE = Column(String(50))
    INJURY_COUNT = Column(Integer)
    BODYPART_COUNT = Column(Integer)
    INJURYGROUP_COUNT = Column(Integer)

    # NEW: Multi-tier injury system - By SEVERITY ranking
    PRIMARY_INJURY_BY_SEVERITY = Column(String(200))
    PRIMARY_BODYPART_BY_SEVERITY = Column(String(200))
    PRIMARY_INJURYGROUP_CODE_BY_SEVERITY = Column(String(50), index=True)
    PRIMARY_INJURY_SEVERITY_SCORE = Column(Float, index=True)
    PRIMARY_INJURY_CAUSATION_SCORE_BY_SEVERITY = Column(Float)

    SECONDARY_INJURY_BY_SEVERITY = Column(String(200))
    SECONDARY_BODYPART_BY_SEVERITY = Column(String(200))
    SECONDARY_INJURYGROUP_CODE_BY_SEVERITY = Column(String(50))
    SECONDARY_INJURY_SEVERITY_SCORE = Column(Float)
    SECONDARY_INJURY_CAUSATION_SCORE_BY_SEVERITY = Column(Float)

    TERTIARY_INJURY_BY_SEVERITY = Column(String(200))
    TERTIARY_BODYPART_BY_SEVERITY = Column(String(200))
    TERTIARY_INJURY_SEVERITY_SCORE = Column(Float)
    TERTIARY_INJURY_CAUSATION_SCORE_BY_SEVERITY = Column(Float)

    # NEW: Multi-tier injury system - By CAUSATION ranking
    PRIMARY_INJURY_BY_CAUSATION = Column(String(200))
    PRIMARY_BODYPART_BY_CAUSATION = Column(String(200))
    PRIMARY_INJURYGROUP_CODE_BY_CAUSATION = Column(String(50), index=True)
    PRIMARY_INJURY_CAUSATION_SCORE = Column(Float, index=True)
    PRIMARY_INJURY_SEVERITY_SCORE_BY_CAUSATION = Column(Float)

    SECONDARY_INJURY_BY_CAUSATION = Column(String(200))
    SECONDARY_BODYPART_BY_CAUSATION = Column(String(200))
    SECONDARY_INJURYGROUP_CODE_BY_CAUSATION = Column(String(50))
    SECONDARY_INJURY_CAUSATION_SCORE = Column(Float)
    SECONDARY_INJURY_SEVERITY_SCORE_BY_CAUSATION = Column(Float)

    TERTIARY_INJURY_BY_CAUSATION = Column(String(200))
    TERTIARY_BODYPART_BY_CAUSATION = Column(String(200))
    TERTIARY_INJURY_CAUSATION_SCORE = Column(Float)
    TERTIARY_INJURY_SEVERITY_SCORE_BY_CAUSATION = Column(Float)

    # Person information
    HASATTORNEY = Column(String(10))
    AGE = Column(Integer)
    GENDER = Column(String(10))
    OCCUPATION_AVAILABLE = Column(Integer)
    OCCUPATION = Column(String(200))
    ADJUSTERNAME = Column(String(100), index=True)

    # Location and venue - ACTUAL DATA FORMAT
    IOL = Column(Integer, index=True)  # Impact on life (was IMPACT)
    COUNTYNAME = Column(String(100), index=True)
    VENUESTATE = Column(String(50), index=True)
    VENUERATINGTEXT = Column(String(50))  # Text description of venue rating
    VENUERATINGPOINT = Column(Float)  # Numeric venue rating point
    RATINGWEIGHT = Column(Float)  # Venue weighting
    VENUERATING = Column(String(50), index=True)  # Defense/Neutral/Plaintiff Friendly
    VULNERABLECLAIMANT = Column(String(50))
    BODY_REGION = Column(String(100))

    # Settlement timing
    SETTLEMENT_DAYS = Column(Integer)
    SETTLEMENT_MONTHS = Column(Integer)
    SETTLEMENT_YEARS = Column(Float)
    SETTLEMENT_SPEED_CATEGORY = Column(String(50))

    # Calculated fields
    SEVERITY_SCORE = Column(Float, index=True)
    CAUTION_LEVEL = Column(String(50), index=True)
    variance_pct = Column(Float, index=True)  # Calculated: (DOLLARAMOUNTHIGH - CAUSATION_HIGH_RECOMMENDATION) / CAUSATION_HIGH_RECOMMENDATION * 100

    # NEW: Composite calculated scores from model
    CALCULATED_SEVERITY_SCORE = Column(Float, index=True)
    CALCULATED_CAUSATION_SCORE = Column(Float, index=True)

    # NEW: Row number field
    RN = Column(Integer)

    # Extended clinical factors (40+ feature columns)
    # Note: In CSV these have single quotes, in DB we use without quotes for column names
    Advanced_Pain_Treatment = Column(String(200))
    Causation_Compliance = Column(String(200))
    Clinical_Findings = Column(String(200))
    Cognitive_Symptoms = Column(String(200))
    Complete_Disability_Duration = Column(String(200))
    Concussion_Diagnosis = Column(String(200))
    Consciousness_Impact = Column(String(200))
    Consistent_Mechanism = Column(String(200))
    Dental_Procedure = Column(String(200))
    Dental_Treatment = Column(String(200))
    Dental_Visibility = Column(String(200))
    Emergency_Treatment = Column(String(200))
    Fixation_Method = Column(String(200))
    Head_Trauma = Column(String(200))
    Immobilization_Used = Column(String(200))
    Injury_Count_Feature = Column(String(200))  # This is 'Injury_Count' in CSV
    Injury_Extent = Column(String(200))
    Injury_Laterality = Column(String(200))
    Injury_Location = Column(String(200))
    Injury_Type = Column(String(200))
    Mobility_Assistance = Column(String(200))
    Movement_Restriction = Column(String(200))
    Nerve_Involvement = Column(String(200))
    Pain_Management = Column(String(200))
    Partial_Disability_Duration = Column(String(200))
    Physical_Symptoms = Column(String(200))
    Physical_Therapy = Column(String(200))
    Prior_Treatment = Column(String(200))
    Recovery_Duration = Column(String(200))
    Repair_Type = Column(String(200))
    Respiratory_Issues = Column(String(200))
    Soft_Tissue_Damage = Column(String(200))
    Special_Treatment = Column(String(200))
    Surgical_Intervention = Column(String(200))
    Symptom_Timeline = Column(String(200))
    Treatment_Compliance = Column(String(200))
    Treatment_Course = Column(String(200))
    Treatment_Delays = Column(String(200))
    Treatment_Level = Column(String(200))
    Treatment_Period_Considered = Column(String(200))
    Vehicle_Impact = Column(String(200))

    # Composite indexes for common queries - optimized for 5M+ claims (ACTUAL DATA FORMAT)
    __table_args__ = (
        # Critical for venue shift analysis
        Index('idx_county_venue', 'COUNTYNAME', 'VENUERATING'),
        Index('idx_injury_severity_caution', 'PRIMARY_INJURYGROUP_CODE', 'CAUTION_LEVEL', 'IOL'),
        Index('idx_date_venue', 'CLAIMCLOSEDDATE', 'VENUERATING'),
        Index('idx_date_county', 'CLAIMCLOSEDDATE', 'COUNTYNAME'),

        # For adjuster performance analysis
        Index('idx_adjuster_date', 'ADJUSTERNAME', 'CLAIMCLOSEDDATE'),
        Index('idx_adjuster_variance', 'ADJUSTERNAME', 'variance_pct'),

        # For overview and filtering
        Index('idx_date_variance', 'CLAIMCLOSEDDATE', 'variance_pct'),
        Index('idx_venue_state', 'VENUESTATE', 'VENUERATING'),

        # For isolated factor analysis with full controls
        Index('idx_county_venue_injury', 'COUNTYNAME', 'VENUERATING', 'PRIMARY_INJURYGROUP_CODE'),
        Index('idx_county_venue_injury_severity', 'COUNTYNAME', 'VENUERATING', 'PRIMARY_INJURYGROUP_CODE', 'CAUTION_LEVEL'),

        # NEW: Indexes for multi-tier injury analysis by severity
        Index('idx_primary_severity_by_severity', 'PRIMARY_INJURYGROUP_CODE_BY_SEVERITY', 'PRIMARY_INJURY_SEVERITY_SCORE'),
        Index('idx_calculated_scores', 'CALCULATED_SEVERITY_SCORE', 'CALCULATED_CAUSATION_SCORE'),

        # NEW: Indexes for multi-tier injury analysis by causation
        Index('idx_primary_causation_by_causation', 'PRIMARY_INJURYGROUP_CODE_BY_CAUSATION', 'PRIMARY_INJURY_CAUSATION_SCORE'),

        # NEW: Model performance analysis indexes
        Index('idx_model_performance', 'PRIMARY_INJURYGROUP_CODE_BY_SEVERITY', 'variance_pct', 'CALCULATED_SEVERITY_SCORE'),
    )


class SSNB(Base):
    """
    SSNB table - Single injury, Soft tissue, Neck/Back claims
    Used for weight recalibration with float-based clinical factor values
    """
    __tablename__ = 'ssnb'

    id = Column(Integer, primary_key=True, autoincrement=True)
    CLAIMID = Column(Integer, unique=True, nullable=False, index=True)
    VERSIONID = Column(Integer)
    EXPSR_NBR = Column(String(50))

    # Financial
    CAUSATION_HIGH_RECOMMENDATION = Column(Float)
    DOLLARAMOUNTHIGH = Column(Float)

    # Venue
    VENUERATING = Column(String(50))
    RATINGWEIGHT = Column(Float)
    VENUERATINGTEXT = Column(String(100))
    VENUERATINGPOINT = Column(Float)

    # Dates
    INCIDENTDATE = Column(String(50))
    CLAIMCLOSEDDATE = Column(String(50))

    # Demographics
    AGE = Column(Integer)
    GENDER = Column(Integer)
    HASATTORNEY = Column(Integer)
    IOL = Column(Integer)
    ADJUSTERNAME = Column(String(100))
    OCCUPATION = Column(String(200))

    # Location
    COUNTYNAME = Column(String(100))
    VENUESTATE = Column(String(50))
    VULNERABLECLAIMANT = Column(Boolean)

    # Fixed injury type for SSNB
    PRIMARY_INJURY = Column(String(200))  # Always 'Sprain/Strain'
    PRIMARY_BODYPART = Column(String(200))  # Always 'Neck/Back'
    PRIMARY_INJURY_GROUP = Column(String(200))  # Always 'Sprain/Strain, Neck/Back'

    # Scores
    PRIMARY_SEVERITY_SCORE = Column(Float)
    PRIMARY_CAUSATION_SCORE = Column(Float)

    # Clinical factors - FLOAT VALUES (not categorical!)
    Causation_Compliance = Column(Float)
    Clinical_Findings = Column(Float)
    Consistent_Mechanism = Column(Float)
    Injury_Location = Column(Float)
    Movement_Restriction = Column(Float)
    Pain_Management = Column(Float)
    Prior_Treatment = Column(Float)
    Symptom_Timeline = Column(Float)
    Treatment_Course = Column(Float)
    Treatment_Delays = Column(Float)
    Treatment_Period_Considered = Column(Float)
    Vehicle_Impact = Column(Float)

    __table_args__ = (
        Index('idx_ssnb_severity', 'PRIMARY_SEVERITY_SCORE'),
        Index('idx_ssnb_causation', 'PRIMARY_CAUSATION_SCORE'),
    )


class Weight(Base):
    """
    Weights table - stores feature weights from weights.csv
    """
    __tablename__ = 'weights'

    id = Column(Integer, primary_key=True, autoincrement=True)
    factor_name = Column(String(200), unique=True, nullable=False, index=True)
    base_weight = Column(Float, nullable=False)
    min_weight = Column(Float, nullable=False)
    max_weight = Column(Float, nullable=False)
    category = Column(String(100), index=True)
    description = Column(Text)

    __table_args__ = (
        Index('idx_category', 'category'),
    )


class AggregatedCache(Base):
    """
    Cache table for pre-computed aggregations
    Speeds up dashboard loading for 2M+ rows
    """
    __tablename__ = 'aggregated_cache'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(200), unique=True, nullable=False, index=True)
    cache_type = Column(String(100), index=True)  # 'county_year', 'venue', etc.
    data_json = Column(Text)  # Stored as JSON
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    __table_args__ = (
        Index('idx_cache_type', 'cache_type', 'updated_at'),
    )


# Database connection setup
def get_database_url(db_name: str = "claims_analytics.db") -> str:
    """Get SQLite database URL"""
    db_path = Path(__file__).parent / db_name
    return f"sqlite:///{db_path}"


def init_database(db_url: str = None):
    """
    Initialize database and create all tables
    """
    if db_url is None:
        db_url = get_database_url()

    engine = create_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}  # For SQLite with FastAPI
    )

    # Create all tables
    Base.metadata.create_all(engine)

    return engine


def get_session(engine):
    """
    Get SQLAlchemy session
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def get_engine():
    """
    Get database engine with connection pooling for 5M+ claims
    Optimized for production workload
    """
    db_url = get_database_url()
    return create_engine(
        db_url,
        echo=False,
        pool_size=20,              # Max persistent connections
        max_overflow=40,           # Max burst connections (total: 60)
        pool_timeout=30,           # Wait 30s for available connection
        pool_recycle=3600,         # Recycle connections after 1 hour
        pool_pre_ping=True,        # Check connection health before use
        connect_args={"check_same_thread": False}  # For SQLite with FastAPI
    )
