"""
SSNB model - Single injury, Soft tissue, Neck/Back claims.
Used for weight recalibration with float-based clinical factors.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Index

from .base import BaseModel


class SSNB(BaseModel):
    """
    SSNB table - Single injury, Soft tissue, Neck/Back claims subset.

    Key Features:
    - Float-based clinical factors (not categorical)
    - Fixed injury type (Sprain/Strain, Neck/Back)
    - Used for model weight recalibration
    - Smaller dataset for optimization algorithms
    """

    __tablename__ = 'ssnb'

    # ==========================================
    # Core Identifiers
    # ==========================================
    CLAIMID = Column(Integer, nullable=False, index=True)
    VERSIONID = Column(Integer)
    EXPSR_NBR = Column(String(50))

    # ==========================================
    # Financial
    # ==========================================
    CAUSATION_HIGH_RECOMMENDATION = Column(Float)
    DOLLARAMOUNTHIGH = Column(Float)

    # ==========================================
    # Venue
    # ==========================================
    VENUERATING = Column(String(50))
    RATINGWEIGHT = Column(Float)
    VENUERATINGTEXT = Column(String(100))
    VENUERATINGPOINT = Column(Float)

    # ==========================================
    # Dates
    # ==========================================
    INCIDENTDATE = Column(String(50))
    CLAIMCLOSEDDATE = Column(String(50))

    # ==========================================
    # Demographics
    # ==========================================
    AGE = Column(Integer)
    GENDER = Column(Integer)
    HASATTORNEY = Column(Integer)  # 0/1 for SQLite, BOOLEAN for Snowflake
    IOL = Column(Integer)
    ADJUSTERNAME = Column(String(100))
    OCCUPATION = Column(String(200))

    # ==========================================
    # Location
    # ==========================================
    COUNTYNAME = Column(String(100))
    VENUESTATE = Column(String(50))
    VULNERABLECLAIMANT = Column(Integer)  # 0/1 for SQLite

    # ==========================================
    # Fixed Injury Type for SSNB
    # ==========================================
    PRIMARY_INJURY = Column(String(200))  # Always 'Sprain/Strain'
    PRIMARY_BODYPART = Column(String(200))  # Always 'Neck/Back'
    PRIMARY_INJURY_GROUP = Column(String(200))  # Always 'Sprain/Strain, Neck/Back'

    # ==========================================
    # Scores
    # ==========================================
    PRIMARY_SEVERITY_SCORE = Column(Float)
    PRIMARY_CAUSATION_SCORE = Column(Float)

    # ==========================================
    # Clinical Factors - FLOAT VALUES (not categorical!)
    # These are numerical scores, not categories
    # ==========================================
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

    # ==========================================
    # Indexes for Performance
    # ==========================================
    __table_args__ = (
        Index('idx_ssnb_severity', 'PRIMARY_SEVERITY_SCORE'),
        Index('idx_ssnb_causation', 'PRIMARY_CAUSATION_SCORE'),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<SSNB(id={self.id}, CLAIMID={self.CLAIMID}, severity={self.PRIMARY_SEVERITY_SCORE})>"
