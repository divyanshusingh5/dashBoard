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
    claim_id = Column(String(100), unique=True, nullable=False, index=True)

    # Core fields
    VERSIONID = Column(Integer, index=True)
    claim_date = Column(String(50), index=True)  # Store as string, parse when needed
    DURATIONTOREPORT = Column(Float)
    DOLLARAMOUNTHIGH = Column(Float, index=True)

    # Injury information
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

    # Settlement information
    SETTLEMENT_DAYS = Column(Integer)
    SETTLEMENT_MONTHS = Column(Integer)
    SETTLEMENT_YEARS = Column(Integer)

    # Location and venue
    IMPACT = Column(Integer, index=True)
    COUNTYNAME = Column(String(100), index=True)
    VENUESTATE = Column(String(50), index=True)
    VENUE_RATING = Column(String(50), index=True)
    RATINGWEIGHT = Column(Float)
    INJURY_GROUP_CODE = Column(String(50), index=True)

    # Severity and caution
    CAUSATION__HIGH_RECOMMENDATION = Column(Float)
    SEVERITY_SCORE = Column(Float, index=True)
    CAUTION_LEVEL = Column(String(50), index=True)

    # Adjuster and predictions
    adjuster = Column(String(100), index=True)
    predicted_pain_suffering = Column(Float)
    variance_pct = Column(Float, index=True)

    # Causation factors
    causation_probability = Column(Float)
    causation_tx_delay = Column(Float)
    causation_tx_gaps = Column(Float)
    # causation_compliance = Column(Float)  # Removed: duplicate of Causation_Compliance below

    # Severity factors
    severity_allowed_tx_period = Column(Float)
    severity_initial_tx = Column(Float)
    severity_injections = Column(Float)
    severity_objective_findings = Column(Float)
    severity_pain_mgmt = Column(Float)
    severity_type_tx = Column(Float)
    severity_injury_site = Column(Float)
    severity_code = Column(Float)

    # Extended clinical factors (51 total feature columns)
    Advanced_Pain_Treatment = Column(String(50))
    Causation_Compliance = Column(String(50))
    Clinical_Findings = Column(String(50))
    Cognitive_Symptoms = Column(String(50))
    Complete_Disability_Duration = Column(String(50))
    Concussion_Diagnosis = Column(String(50))
    Consciousness_Impact = Column(String(50))
    Consistent_Mechanism = Column(String(50))
    Dental_Procedure = Column(String(50))
    Emergency_Treatment = Column(String(50))
    Fixation_Method = Column(String(50))
    Head_Trauma = Column(String(50))
    Immobilization_Used = Column(String(50))
    Injury_Count_Feature = Column(String(50))
    Injury_Extent = Column(String(50))
    Injury_Laterality = Column(String(50))
    Injury_Location = Column(String(50))
    Injury_Type = Column(String(50))
    Mobility_Assistance = Column(String(50))
    Movement_Restriction = Column(String(50))
    Nerve_Involvement = Column(String(50))
    Pain_Management = Column(String(50))
    Partial_Disability_Duration = Column(String(50))
    Physical_Symptoms = Column(String(50))
    Physical_Therapy = Column(String(50))
    Prior_Treatment = Column(String(50))
    Recovery_Duration = Column(String(50))
    Repair_Type = Column(String(50))
    Respiratory_Issues = Column(String(50))
    Soft_Tissue_Damage = Column(String(50))
    Special_Treatment = Column(String(50))
    Surgical_Intervention = Column(String(50))
    Symptom_Timeline = Column(String(50))
    Treatment_Compliance = Column(String(50))
    Treatment_Course = Column(String(50))
    Treatment_Delays = Column(String(50))
    Treatment_Level = Column(String(50))
    Treatment_Period_Considered = Column(String(50))
    Vehicle_Impact = Column(String(50))

    # Composite indexes for common queries - optimized for 5M+ claims
    __table_args__ = (
        # Critical for venue shift analysis
        Index('idx_county_venue', 'COUNTYNAME', 'VENUE_RATING'),
        Index('idx_injury_severity_caution', 'INJURY_GROUP_CODE', 'CAUTION_LEVEL', 'IMPACT'),
        Index('idx_date_venue', 'claim_date', 'VENUE_RATING'),
        Index('idx_date_county', 'claim_date', 'COUNTYNAME'),

        # For adjuster performance analysis
        Index('idx_adjuster_date', 'adjuster', 'claim_date'),
        Index('idx_adjuster_variance', 'adjuster', 'variance_pct'),

        # For overview and filtering
        Index('idx_date_variance', 'claim_date', 'variance_pct'),
        Index('idx_venue_state', 'VENUESTATE', 'VENUE_RATING'),

        # For isolated factor analysis with full controls
        Index('idx_county_venue_injury', 'COUNTYNAME', 'VENUE_RATING', 'INJURY_GROUP_CODE'),
        Index('idx_county_venue_injury_severity', 'COUNTYNAME', 'VENUE_RATING', 'INJURY_GROUP_CODE', 'CAUTION_LEVEL'),
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
