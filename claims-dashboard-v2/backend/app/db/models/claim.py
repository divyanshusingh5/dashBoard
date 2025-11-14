"""
Claim model - Main claims table.
Stores all claim data with multi-tier injury ranking system.
"""

from sqlalchemy import Column, Integer, String, Float, Text, Index

from .base import BaseModel


class Claim(BaseModel):
    """
    Main claims table - stores all claim data from dat.csv.
    Optimized for fast querying with 20+ composite indexes.

    Features:
    - Multi-tier injury ranking (by severity AND causation)
    - 40+ clinical factor columns
    - Calculated variance and scores
    - Settlement timing metrics
    """

    __tablename__ = 'claims'

    # ==========================================
    # Core Identifiers
    # ==========================================
    CLAIMID = Column(Integer, nullable=False, index=True)
    EXPSR_NBR = Column(String(50))
    VERSIONID = Column(Integer, index=True)
    RN = Column(Integer)

    # ==========================================
    # Dates (stored as strings for SQLite compatibility)
    # ==========================================
    CLAIMCLOSEDDATE = Column(String(50), index=True)
    INCIDENTDATE = Column(String(50))
    DURATIONTOREPORT = Column(Float)

    # ==========================================
    # Financial Fields
    # ==========================================
    CAUSATION_HIGH_RECOMMENDATION = Column(Float)  # Predicted settlement
    SETTLEMENTAMOUNT = Column(Integer)
    DOLLARAMOUNTHIGH = Column(Float, index=True)  # Actual settlement
    GENERALS = Column(Float)

    # ==========================================
    # Injury Information - Legacy Single-Tier
    # ==========================================
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

    # ==========================================
    # Multi-Tier Injury - By SEVERITY Ranking
    # ==========================================
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

    # ==========================================
    # Multi-Tier Injury - By CAUSATION Ranking
    # ==========================================
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

    # ==========================================
    # Person Information
    # ==========================================
    HASATTORNEY = Column(String(10))
    AGE = Column(Integer)
    GENDER = Column(String(10))
    OCCUPATION_AVAILABLE = Column(Integer)
    OCCUPATION = Column(String(200))
    ADJUSTERNAME = Column(String(100), index=True)

    # ==========================================
    # Location and Venue
    # ==========================================
    IOL = Column(Integer, index=True)  # Impact on Life
    COUNTYNAME = Column(String(100), index=True)
    VENUESTATE = Column(String(50), index=True)
    VENUERATINGTEXT = Column(String(50))
    VENUERATINGPOINT = Column(Float)
    RATINGWEIGHT = Column(Float)
    VENUERATING = Column(String(50), index=True)
    VULNERABLECLAIMANT = Column(String(50))
    BODY_REGION = Column(String(100))

    # ==========================================
    # Settlement Timing
    # ==========================================
    SETTLEMENT_DAYS = Column(Integer)
    SETTLEMENT_MONTHS = Column(Integer)
    SETTLEMENT_YEARS = Column(Float)
    SETTLEMENT_SPEED_CATEGORY = Column(String(50))

    # ==========================================
    # Calculated Fields
    # ==========================================
    SEVERITY_SCORE = Column(Float, index=True)
    CAUTION_LEVEL = Column(String(50), index=True)
    variance_pct = Column(Float, index=True)
    CALCULATED_SEVERITY_SCORE = Column(Float, index=True)
    CALCULATED_CAUSATION_SCORE = Column(Float, index=True)

    # ==========================================
    # Clinical Factors (40+ features)
    # ==========================================
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
    Injury_Count_Feature = Column(String(200))
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

    # ==========================================
    # Composite Indexes for Performance
    # ==========================================
    __table_args__ = (
        # Venue shift analysis
        Index('idx_county_venue', 'COUNTYNAME', 'VENUERATING'),
        Index('idx_county_venue_injury', 'COUNTYNAME', 'VENUERATING', 'PRIMARY_INJURYGROUP_CODE'),
        Index('idx_county_venue_injury_severity', 'COUNTYNAME', 'VENUERATING', 'PRIMARY_INJURYGROUP_CODE', 'CAUTION_LEVEL'),
        Index('idx_date_venue', 'CLAIMCLOSEDDATE', 'VENUERATING'),
        Index('idx_date_county', 'CLAIMCLOSEDDATE', 'COUNTYNAME'),
        Index('idx_venue_state', 'VENUESTATE', 'VENUERATING'),

        # Adjuster performance
        Index('idx_adjuster_date', 'ADJUSTERNAME', 'CLAIMCLOSEDDATE'),
        Index('idx_adjuster_variance', 'ADJUSTERNAME', 'variance_pct'),

        # Overview and filtering
        Index('idx_date_variance', 'CLAIMCLOSEDDATE', 'variance_pct'),
        Index('idx_injury_severity_caution', 'PRIMARY_INJURYGROUP_CODE', 'CAUTION_LEVEL', 'IOL'),

        # Multi-tier injury analysis
        Index('idx_primary_severity_by_severity', 'PRIMARY_INJURYGROUP_CODE_BY_SEVERITY', 'PRIMARY_INJURY_SEVERITY_SCORE'),
        Index('idx_primary_causation_by_causation', 'PRIMARY_INJURYGROUP_CODE_BY_CAUSATION', 'PRIMARY_INJURY_CAUSATION_SCORE'),
        Index('idx_calculated_scores', 'CALCULATED_SEVERITY_SCORE', 'CALCULATED_CAUSATION_SCORE'),

        # Model performance
        Index('idx_model_performance', 'PRIMARY_INJURYGROUP_CODE_BY_SEVERITY', 'variance_pct', 'CALCULATED_SEVERITY_SCORE'),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Claim(id={self.id}, CLAIMID={self.CLAIMID}, amount=${self.DOLLARAMOUNTHIGH})>"
