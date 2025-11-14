"""
Complete PostgreSQL Migration Script for Claims Analytics
Migrates dat.csv and SSNB.csv to PostgreSQL database
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, Text, Index, Boolean, BigInteger, text
)
from sqlalchemy.orm import declarative_base, sessionmaker
import logging
from datetime import datetime
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Schema Definition
Base = declarative_base()

class Claim(Base):
    """Main claims table - stores all claim data from dat.csv"""
    __tablename__ = 'claims'

    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Core identifiers
    CLAIMID = Column(Integer, nullable=False, index=True)
    EXPSR_NBR = Column(String(50))
    VERSIONID = Column(Integer, index=True)

    # Dates
    CLAIMCLOSEDDATE = Column(String(50), index=True)
    INCIDENTDATE = Column(String(50))
    DURATIONTOREPORT = Column(Float)

    # Financial
    CAUSATION_HIGH_RECOMMENDATION = Column(Float)
    SETTLEMENTAMOUNT = Column(Integer)
    DOLLARAMOUNTHIGH = Column(Float, index=True)
    GENERALS = Column(Float)

    # Legacy injury info
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
    BODY_REGION = Column(String(100))

    # Multi-tier injury by SEVERITY
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

    # Multi-tier injury by CAUSATION
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

    # Location and venue
    IOL = Column(Integer, index=True)
    COUNTYNAME = Column(String(100), index=True)
    VENUESTATE = Column(String(50), index=True)
    VENUERATINGTEXT = Column(String(50))
    VENUERATINGPOINT = Column(Float)
    RATINGWEIGHT = Column(Float)
    VENUERATING = Column(String(50), index=True)
    VULNERABLECLAIMANT = Column(String(50))

    # Settlement timing
    SETTLEMENT_DAYS = Column(Integer)
    SETTLEMENT_MONTHS = Column(Integer)
    SETTLEMENT_YEARS = Column(Float)
    SETTLEMENT_SPEED_CATEGORY = Column(String(50))

    # Calculated fields
    SEVERITY_SCORE = Column(Float, index=True)
    CAUTION_LEVEL = Column(String(50), index=True)
    variance_pct = Column(Float, index=True)

    # Composite scores
    CALCULATED_SEVERITY_SCORE = Column(Float, index=True)
    CALCULATED_CAUSATION_SCORE = Column(Float, index=True)
    RN = Column(Integer)

    # Clinical factors (40+ fields)
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

    # Indexes for performance
    __table_args__ = (
        Index('idx_county_venue', 'COUNTYNAME', 'VENUERATING'),
        Index('idx_injury_severity_caution', 'PRIMARY_INJURYGROUP_CODE', 'CAUTION_LEVEL', 'IOL'),
        Index('idx_date_venue', 'CLAIMCLOSEDDATE', 'VENUERATING'),
        Index('idx_adjuster_date', 'ADJUSTERNAME', 'CLAIMCLOSEDDATE'),
        Index('idx_primary_severity_by_severity', 'PRIMARY_INJURYGROUP_CODE_BY_SEVERITY', 'PRIMARY_INJURY_SEVERITY_SCORE'),
        Index('idx_calculated_scores', 'CALCULATED_SEVERITY_SCORE', 'CALCULATED_CAUSATION_SCORE'),
    )


class SSNB(Base):
    """SSNB table - Single injury, Soft tissue, Neck/Back claims"""
    __tablename__ = 'ssnb'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    CLAIMID = Column(Integer, nullable=False, index=True)
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

    # Fixed injury type
    PRIMARY_INJURY = Column(String(200))
    PRIMARY_BODYPART = Column(String(200))
    PRIMARY_INJURY_GROUP = Column(String(200))

    # Scores
    PRIMARY_SEVERITY_SCORE = Column(Float)
    PRIMARY_CAUSATION_SCORE = Column(Float)

    # Clinical factors - FLOAT VALUES
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


# Migration Class
class PostgreSQLMigration:
    """Complete PostgreSQL migration with schema creation"""

    def __init__(self,
                 dat_csv_path: str = "dat.csv",
                 ssnb_csv_path: str = "SSNB.csv",
                 batch_size: int = 5000,
                 db_url: str = None):

        self.dat_csv_path = Path(dat_csv_path)
        self.ssnb_csv_path = Path(ssnb_csv_path)
        self.batch_size = batch_size

        # PostgreSQL connection - UPDATE THESE CREDENTIALS
        self.db_url = db_url or "postgresql://postgres:user@localhost:5432/claims_analytics"

        self.engine = None
        self.session = None

    def initialize_database(self):
        """Initialize PostgreSQL database and create all tables"""
        logger.info("Connecting to PostgreSQL database...")
        logger.info(f"Database: claims_analytics")

        try:
            self.engine = create_engine(
                self.db_url,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                echo=False
            )

            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"✓ Connected to PostgreSQL: {version[:50]}...")

            # Create all tables
            logger.info("Creating database schema...")
            Base.metadata.create_all(self.engine)

            # Create session
            Session = sessionmaker(bind=self.engine)
            self.session = Session()

            logger.info("✓ Database schema created successfully")

        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            logger.error("Make sure PostgreSQL is running and credentials are correct")
            raise

    def clean_column_name(self, col: str) -> str:
        """Remove quotes from column names"""
        return col.strip("'\"")

    def calculate_variance_pct(self, row):
        """Calculate variance percentage for model performance"""
        try:
            actual = row.get('DOLLARAMOUNTHIGH', row.get('DOLLARAMOUNT HIGH'))
            predicted = row.get('CAUSATION_HIGH_RECOMMENDATION')

            if pd.isna(actual) or pd.isna(predicted) or predicted == 0:
                return None

            variance = ((actual - predicted) / predicted) * 100
            return round(variance, 2)
        except:
            return None

    def calculate_severity_score(self, row):
        """Calculate severity score based on injury characteristics"""
        try:
            score = 0

            if pd.notna(row.get('PRIMARY_INJURY_SEVERITY_SCORE')):
                score += row.get('PRIMARY_INJURY_SEVERITY_SCORE', 0) * 0.5

            if pd.notna(row.get('SECONDARY_INJURY_SEVERITY_SCORE')):
                score += row.get('SECONDARY_INJURY_SEVERITY_SCORE', 0) * 0.3

            if pd.notna(row.get('TERTIARY_INJURY_SEVERITY_SCORE')):
                score += row.get('TERTIARY_INJURY_SEVERITY_SCORE', 0) * 0.2

            injury_count = row.get('INJURY_COUNT', 1)
            score *= (1 + (injury_count - 1) * 0.15)

            return round(score, 2)
        except:
            return None

    def calculate_caution_level(self, severity_score):
        """Categorize severity into caution levels"""
        if pd.isna(severity_score):
            return 'Unknown'

        if severity_score < 1000:
            return 'Low'
        elif severity_score < 5000:
            return 'Medium'
        elif severity_score < 15000:
            return 'High'
        else:
            return 'Critical'

    def safe_value(self, value, dtype='str'):
        """Safely convert values, handling NaN, inf, etc."""
        if pd.isna(value) or value in [np.inf, -np.inf]:
            return None

        if dtype == 'str':
            return str(value) if value is not None else None
        elif dtype == 'int':
            try:
                return int(value) if value is not None else None
            except:
                return None
        elif dtype == 'float':
            try:
                return float(value) if value is not None else None
            except:
                return None

        return value

    def migrate_dat_csv(self):
        """Migrate main dat.csv with PostgreSQL optimizations"""
        if not self.dat_csv_path.exists():
            logger.error(f"❌ dat.csv not found at {self.dat_csv_path}")
            return False

        logger.info(f"📊 Loading dat.csv from {self.dat_csv_path}...")

        # Clear existing data
        try:
            logger.info("Clearing existing claims data...")
            self.session.query(Claim).delete()
            self.session.commit()
            logger.info("✓ Claims table cleared")
        except Exception as e:
            logger.warning(f"Could not clear claims table: {str(e)}")
            self.session.rollback()

        # Read and process in chunks
        chunks = pd.read_csv(self.dat_csv_path, chunksize=self.batch_size)
        total_imported = 0
        total_errors = 0

        for chunk_num, df_chunk in enumerate(chunks, 1):
            logger.info(f"Processing chunk {chunk_num} ({len(df_chunk)} records)...")

            # Clean column names
            df_chunk.columns = [self.clean_column_name(col) for col in df_chunk.columns]

            # Calculate derived fields
            logger.info("  Calculating derived fields...")
            df_chunk['variance_pct'] = df_chunk.apply(self.calculate_variance_pct, axis=1)

            if 'SEVERITY_SCORE' not in df_chunk.columns:
                df_chunk['SEVERITY_SCORE'] = df_chunk.apply(self.calculate_severity_score, axis=1)

            df_chunk['CAUTION_LEVEL'] = df_chunk['SEVERITY_SCORE'].apply(self.calculate_caution_level)

            # Prepare data for bulk insert
            claims_batch = []

            for idx, row in df_chunk.iterrows():
                try:
                    claim_data = {
                        # Core identifiers
                        'CLAIMID': self.safe_value(row.get('CLAIMID'), 'int'),
                        'EXPSR_NBR': self.safe_value(row.get('EXPSR_NBR'), 'str'),
                        'VERSIONID': self.safe_value(row.get('VERSIONID'), 'int'),

                        # Dates
                        'CLAIMCLOSEDDATE': self.safe_value(row.get('CLAIMCLOSEDDATE'), 'str'),
                        'INCIDENTDATE': self.safe_value(row.get('INCIDENTDATE'), 'str'),
                        'DURATIONTOREPORT': self.safe_value(row.get('DURATIONTOREPORT'), 'float'),

                        # Financial
                        'CAUSATION_HIGH_RECOMMENDATION': self.safe_value(row.get('CAUSATION_HIGH_RECOMMENDATION'), 'float'),
                        'SETTLEMENTAMOUNT': self.safe_value(row.get('SETTLEMENTAMOUNT'), 'int'),
                        'DOLLARAMOUNTHIGH': self.safe_value(row.get('DOLLARAMOUNTHIGH'), 'float'),
                        'GENERALS': self.safe_value(row.get('GENERALS'), 'float'),

                        # Legacy injury info
                        'ALL_BODYPARTS': self.safe_value(row.get('ALL_BODYPARTS'), 'str'),
                        'ALL_INJURIES': self.safe_value(row.get('ALL_INJURIES'), 'str'),
                        'ALL_INJURYGROUP_CODES': self.safe_value(row.get('ALL_INJURYGROUP_CODES'), 'str'),
                        'ALL_INJURYGROUP_TEXTS': self.safe_value(row.get('ALL_INJURYGROUP_TEXTS'), 'str'),
                        'PRIMARY_INJURY': self.safe_value(row.get('PRIMARY_INJURY'), 'str'),
                        'PRIMARY_BODYPART': self.safe_value(row.get('PRIMARY_BODYPART'), 'str'),
                        'PRIMARY_INJURYGROUP_CODE': self.safe_value(row.get('PRIMARY_INJURYGROUP_CODE'), 'str'),
                        'INJURY_COUNT': self.safe_value(row.get('INJURY_COUNT'), 'int'),
                        'BODYPART_COUNT': self.safe_value(row.get('BODYPART_COUNT'), 'int'),
                        'INJURYGROUP_COUNT': self.safe_value(row.get('INJURYGROUP_COUNT'), 'int'),
                        'BODY_REGION': self.safe_value(row.get('BODY_REGION'), 'str'),

                        # Multi-tier injury by SEVERITY
                        'PRIMARY_INJURY_BY_SEVERITY': self.safe_value(row.get('PRIMARY_INJURY_BY_SEVERITY'), 'str'),
                        'PRIMARY_BODYPART_BY_SEVERITY': self.safe_value(row.get('PRIMARY_BODYPART_BY_SEVERITY'), 'str'),
                        'PRIMARY_INJURYGROUP_CODE_BY_SEVERITY': self.safe_value(row.get('PRIMARY_INJURYGROUP_CODE_BY_SEVERITY'), 'str'),
                        'PRIMARY_INJURY_SEVERITY_SCORE': self.safe_value(row.get('PRIMARY_INJURY_SEVERITY_SCORE'), 'float'),
                        'PRIMARY_INJURY_CAUSATION_SCORE_BY_SEVERITY': self.safe_value(row.get('PRIMARY_INJURY_CAUSATION_SCORE_BY_SEVERITY'), 'float'),

                        'SECONDARY_INJURY_BY_SEVERITY': self.safe_value(row.get('SECONDARY_INJURY_BY_SEVERITY'), 'str'),
                        'SECONDARY_BODYPART_BY_SEVERITY': self.safe_value(row.get('SECONDARY_BODYPART_BY_SEVERITY'), 'str'),
                        'SECONDARY_INJURYGROUP_CODE_BY_SEVERITY': self.safe_value(row.get('SECONDARY_INJURYGROUP_CODE_BY_SEVERITY'), 'str'),
                        'SECONDARY_INJURY_SEVERITY_SCORE': self.safe_value(row.get('SECONDARY_INJURY_SEVERITY_SCORE'), 'float'),
                        'SECONDARY_INJURY_CAUSATION_SCORE_BY_SEVERITY': self.safe_value(row.get('SECONDARY_INJURY_CAUSATION_SCORE_BY_SEVERITY'), 'float'),

                        'TERTIARY_INJURY_BY_SEVERITY': self.safe_value(row.get('TERTIARY_INJURY_BY_SEVERITY'), 'str'),
                        'TERTIARY_BODYPART_BY_SEVERITY': self.safe_value(row.get('TERTIARY_BODYPART_BY_SEVERITY'), 'str'),
                        'TERTIARY_INJURY_SEVERITY_SCORE': self.safe_value(row.get('TERTIARY_INJURY_SEVERITY_SCORE'), 'float'),
                        'TERTIARY_INJURY_CAUSATION_SCORE_BY_SEVERITY': self.safe_value(row.get('TERTIARY_INJURY_CAUSATION_SCORE_BY_SEVERITY'), 'float'),

                        # Multi-tier injury by CAUSATION
                        'PRIMARY_INJURY_BY_CAUSATION': self.safe_value(row.get('PRIMARY_INJURY_BY_CAUSATION'), 'str'),
                        'PRIMARY_BODYPART_BY_CAUSATION': self.safe_value(row.get('PRIMARY_BODYPART_BY_CAUSATION'), 'str'),
                        'PRIMARY_INJURYGROUP_CODE_BY_CAUSATION': self.safe_value(row.get('PRIMARY_INJURYGROUP_CODE_BY_CAUSATION'), 'str'),
                        'PRIMARY_INJURY_CAUSATION_SCORE': self.safe_value(row.get('PRIMARY_INJURY_CAUSATION_SCORE'), 'float'),
                        'PRIMARY_INJURY_SEVERITY_SCORE_BY_CAUSATION': self.safe_value(row.get('PRIMARY_INJURY_SEVERITY_SCORE_BY_CAUSATION'), 'float'),

                        'SECONDARY_INJURY_BY_CAUSATION': self.safe_value(row.get('SECONDARY_INJURY_BY_CAUSATION'), 'str'),
                        'SECONDARY_BODYPART_BY_CAUSATION': self.safe_value(row.get('SECONDARY_BODYPART_BY_CAUSATION'), 'str'),
                        'SECONDARY_INJURYGROUP_CODE_BY_CAUSATION': self.safe_value(row.get('SECONDARY_INJURYGROUP_CODE_BY_CAUSATION'), 'str'),
                        'SECONDARY_INJURY_CAUSATION_SCORE': self.safe_value(row.get('SECONDARY_INJURY_CAUSATION_SCORE'), 'float'),
                        'SECONDARY_INJURY_SEVERITY_SCORE_BY_CAUSATION': self.safe_value(row.get('SECONDARY_INJURY_SEVERITY_SCORE_BY_CAUSATION'), 'float'),

                        'TERTIARY_INJURY_BY_CAUSATION': self.safe_value(row.get('TERTIARY_INJURY_BY_CAUSATION'), 'str'),
                        'TERTIARY_BODYPART_BY_CAUSATION': self.safe_value(row.get('TERTIARY_BODYPART_BY_CAUSATION'), 'str'),
                        'TERTIARY_INJURY_CAUSATION_SCORE': self.safe_value(row.get('TERTIARY_INJURY_CAUSATION_SCORE'), 'float'),
                        'TERTIARY_INJURY_SEVERITY_SCORE_BY_CAUSATION': self.safe_value(row.get('TERTIARY_INJURY_SEVERITY_SCORE_BY_CAUSATION'), 'float'),

                        # Person info
                        'HASATTORNEY': self.safe_value(row.get('HASATTORNEY'), 'str'),
                        'AGE': self.safe_value(row.get('AGE'), 'int'),
                        'GENDER': self.safe_value(row.get('GENDER'), 'str'),
                        'OCCUPATION_AVAILABLE': self.safe_value(row.get('OCCUPATION_AVAILABLE'), 'int'),
                        'OCCUPATION': self.safe_value(row.get('OCCUPATION'), 'str'),
                        'ADJUSTERNAME': self.safe_value(row.get('ADJUSTERNAME'), 'str'),

                        # Location and venue
                        'IOL': self.safe_value(row.get('IOL'), 'int'),
                        'COUNTYNAME': self.safe_value(row.get('COUNTYNAME'), 'str'),
                        'VENUESTATE': self.safe_value(row.get('VENUESTATE'), 'str'),
                        'VENUERATINGTEXT': self.safe_value(row.get('VENUERATINGTEXT'), 'str'),
                        'VENUERATINGPOINT': self.safe_value(row.get('VENUERATINGPOINT'), 'float'),
                        'RATINGWEIGHT': self.safe_value(row.get('RATINGWEIGHT'), 'float'),
                        'VENUERATING': self.safe_value(row.get('VENUERATING'), 'str'),
                        'VULNERABLECLAIMANT': self.safe_value(row.get('VULNERABLECLAIMANT'), 'str'),

                        # Settlement timing
                        'SETTLEMENT_DAYS': self.safe_value(row.get('SETTLEMENT_DAYS'), 'int'),
                        'SETTLEMENT_MONTHS': self.safe_value(row.get('SETTLEMENT_MONTHS'), 'int'),
                        'SETTLEMENT_YEARS': self.safe_value(row.get('SETTLEMENT_YEARS'), 'float'),
                        'SETTLEMENT_SPEED_CATEGORY': self.safe_value(row.get('SETTLEMENT_SPEED_CATEGORY'), 'str'),

                        # Calculated fields
                        'SEVERITY_SCORE': self.safe_value(row.get('SEVERITY_SCORE'), 'float'),
                        'CAUTION_LEVEL': self.safe_value(row.get('CAUTION_LEVEL'), 'str'),
                        'variance_pct': self.safe_value(row.get('variance_pct'), 'float'),

                        # Composite scores
                        'CALCULATED_SEVERITY_SCORE': self.safe_value(row.get('CALCULATED_SEVERITY_SCORE'), 'float'),
                        'CALCULATED_CAUSATION_SCORE': self.safe_value(row.get('CALCULATED_CAUSATION_SCORE'), 'float'),
                        'RN': self.safe_value(row.get('RN'), 'int'),

                        # Clinical factors
                        'Advanced_Pain_Treatment': self.safe_value(row.get('Advanced_Pain_Treatment'), 'str'),
                        'Causation_Compliance': self.safe_value(row.get('Causation_Compliance'), 'str'),
                        'Clinical_Findings': self.safe_value(row.get('Clinical_Findings'), 'str'),
                        'Cognitive_Symptoms': self.safe_value(row.get('Cognitive_Symptoms'), 'str'),
                        'Complete_Disability_Duration': self.safe_value(row.get('Complete_Disability_Duration'), 'str'),
                        'Concussion_Diagnosis': self.safe_value(row.get('Concussion_Diagnosis'), 'str'),
                        'Consciousness_Impact': self.safe_value(row.get('Consciousness_Impact'), 'str'),
                        'Consistent_Mechanism': self.safe_value(row.get('Consistent_Mechanism'), 'str'),
                        'Dental_Procedure': self.safe_value(row.get('Dental_Procedure'), 'str'),
                        'Dental_Treatment': self.safe_value(row.get('Dental_Treatment'), 'str'),
                        'Dental_Visibility': self.safe_value(row.get('Dental_Visibility'), 'str'),
                        'Emergency_Treatment': self.safe_value(row.get('Emergency_Treatment'), 'str'),
                        'Fixation_Method': self.safe_value(row.get('Fixation_Method'), 'str'),
                        'Head_Trauma': self.safe_value(row.get('Head_Trauma'), 'str'),
                        'Immobilization_Used': self.safe_value(row.get('Immobilization_Used'), 'str'),
                        'Injury_Count_Feature': self.safe_value(row.get('Injury_Count'), 'str'),
                        'Injury_Extent': self.safe_value(row.get('Injury_Extent'), 'str'),
                        'Injury_Laterality': self.safe_value(row.get('Injury_Laterality'), 'str'),
                        'Injury_Location': self.safe_value(row.get('Injury_Location'), 'str'),
                        'Injury_Type': self.safe_value(row.get('Injury_Type'), 'str'),
                        'Mobility_Assistance': self.safe_value(row.get('Mobility_Assistance'), 'str'),
                        'Movement_Restriction': self.safe_value(row.get('Movement_Restriction'), 'str'),
                        'Nerve_Involvement': self.safe_value(row.get('Nerve_Involvement'), 'str'),
                        'Pain_Management': self.safe_value(row.get('Pain_Management'), 'str'),
                        'Partial_Disability_Duration': self.safe_value(row.get('Partial_Disability_Duration'), 'str'),
                        'Physical_Symptoms': self.safe_value(row.get('Physical_Symptoms'), 'str'),
                        'Physical_Therapy': self.safe_value(row.get('Physical_Therapy'), 'str'),
                        'Prior_Treatment': self.safe_value(row.get('Prior_Treatment'), 'str'),
                        'Recovery_Duration': self.safe_value(row.get('Recovery_Duration'), 'str'),
                        'Repair_Type': self.safe_value(row.get('Repair_Type'), 'str'),
                        'Respiratory_Issues': self.safe_value(row.get('Respiratory_Issues'), 'str'),
                        'Soft_Tissue_Damage': self.safe_value(row.get('Soft_Tissue_Damage'), 'str'),
                        'Special_Treatment': self.safe_value(row.get('Special_Treatment'), 'str'),
                        'Surgical_Intervention': self.safe_value(row.get('Surgical_Intervention'), 'str'),
                        'Symptom_Timeline': self.safe_value(row.get('Symptom_Timeline'), 'str'),
                        'Treatment_Compliance': self.safe_value(row.get('Treatment_Compliance'), 'str'),
                        'Treatment_Course': self.safe_value(row.get('Treatment_Course'), 'str'),
                        'Treatment_Delays': self.safe_value(row.get('Treatment_Delays'), 'str'),
                        'Treatment_Level': self.safe_value(row.get('Treatment_Level'), 'str'),
                        'Treatment_Period_Considered': self.safe_value(row.get('Treatment_Period_Considered'), 'str'),
                        'Vehicle_Impact': self.safe_value(row.get('Vehicle_Impact'), 'str'),
                    }

                    claims_batch.append(claim_data)

                except Exception as e:
                    logger.error(f"Error preparing row {idx}: {str(e)}")
                    total_errors += 1

            # Bulk insert the batch
            try:
                if claims_batch:
                    self.session.bulk_insert_mappings(Claim, claims_batch)
                    self.session.commit()

                    total_imported += len(claims_batch)
                    logger.info(f"✓ Chunk {chunk_num} inserted successfully ({len(claims_batch)} records)")

            except Exception as e:
                logger.error(f"❌ Error inserting chunk {chunk_num}: {str(e)}")
                self.session.rollback()

        logger.info(f"\n✓ dat.csv migration complete!")
        logger.info(f"  Imported: {total_imported:,} records")
        logger.info(f"  Errors: {total_errors}")

        return True

    def migrate_ssnb_csv(self):
        """Migrate SSNB.csv to PostgreSQL"""
        if not self.ssnb_csv_path.exists():
            logger.warning(f"⚠ SSNB.csv not found at {self.ssnb_csv_path}, skipping...")
            return True

        logger.info(f"\n📊 Loading SSNB.csv from {self.ssnb_csv_path}...")

        # Clear existing SSNB data
        try:
            logger.info("Clearing existing SSNB data...")
            self.session.query(SSNB).delete()
            self.session.commit()
            logger.info("✓ SSNB table cleared")
        except Exception as e:
            logger.warning(f"Could not clear SSNB table: {str(e)}")
            self.session.rollback()

        df = pd.read_csv(self.ssnb_csv_path)
        df.columns = [self.clean_column_name(col) for col in df.columns]

        logger.info(f"Found {len(df)} SSNB records")

        # Prepare batch data
        ssnb_batch = []
        total_errors = 0

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Preparing SSNB data"):
            try:
                ssnb_data = {
                    'CLAIMID': self.safe_value(row.get('CLAIMID'), 'int'),
                    'VERSIONID': self.safe_value(row.get('VERSIONID'), 'int'),
                    'EXPSR_NBR': self.safe_value(row.get('EXPSR_NBR'), 'str'),
                    'CAUSATION_HIGH_RECOMMENDATION': self.safe_value(row.get('CAUSATION_HIGH_RECOMMENDATION'), 'float'),
                    'DOLLARAMOUNTHIGH': self.safe_value(row.get('DOLLARAMOUNTHIGH'), 'float'),
                    'VENUERATING': self.safe_value(row.get('VENUERATING'), 'str'),
                    'RATINGWEIGHT': self.safe_value(row.get('RATINGWEIGHT'), 'float'),
                    'VENUERATINGTEXT': self.safe_value(row.get('VENUERATINGTEXT'), 'str'),
                    'VENUERATINGPOINT': self.safe_value(row.get('VENUERATINGPOINT'), 'float'),
                    'INCIDENTDATE': self.safe_value(row.get('INCIDENTDATE'), 'str'),
                    'CLAIMCLOSEDDATE': self.safe_value(row.get('CLAIMCLOSEDDATE'), 'str'),
                    'AGE': self.safe_value(row.get('AGE'), 'int'),
                    'GENDER': self.safe_value(row.get('GENDER'), 'int'),
                    'HASATTORNEY': self.safe_value(row.get('HASATTORNEY'), 'int'),
                    'IOL': self.safe_value(row.get('IOL'), 'int'),
                    'ADJUSTERNAME': self.safe_value(row.get('ADJUSTERNAME'), 'str'),
                    'OCCUPATION': self.safe_value(row.get('OCCUPATION'), 'str'),
                    'COUNTYNAME': self.safe_value(row.get('COUNTYNAME'), 'str'),
                    'VENUESTATE': self.safe_value(row.get('VENUESTATE'), 'str'),
                    'VULNERABLECLAIMANT': bool(row.get('VULNERABLECLAIMANT')) if pd.notna(row.get('VULNERABLECLAIMANT')) else None,
                    'PRIMARY_INJURY': self.safe_value(row.get('PRIMARY_INJURY'), 'str'),
                    'PRIMARY_BODYPART': self.safe_value(row.get('PRIMARY_BODYPART'), 'str'),
                    'PRIMARY_INJURY_GROUP': self.safe_value(row.get('PRIMARY_INJURY_GROUP'), 'str'),
                    'PRIMARY_SEVERITY_SCORE': self.safe_value(row.get('PRIMARY_SEVERITY_SCORE'), 'float'),
                    'PRIMARY_CAUSATION_SCORE': self.safe_value(row.get('PRIMARY_CAUSATION_SCORE'), 'float'),
                    # Clinical factors as floats
                    'Causation_Compliance': self.safe_value(row.get('Causation_Compliance'), 'float'),
                    'Clinical_Findings': self.safe_value(row.get('Clinical_Findings'), 'float'),
                    'Consistent_Mechanism': self.safe_value(row.get('Consistent_Mechanism'), 'float'),
                    'Injury_Location': self.safe_value(row.get('Injury_Location'), 'float'),
                    'Movement_Restriction': self.safe_value(row.get('Movement_Restriction'), 'float'),
                    'Pain_Management': self.safe_value(row.get('Pain_Management'), 'float'),
                    'Prior_Treatment': self.safe_value(row.get('Prior_Treatment'), 'float'),
                    'Symptom_Timeline': self.safe_value(row.get('Symptom_Timeline'), 'float'),
                    'Treatment_Course': self.safe_value(row.get('Treatment_Course'), 'float'),
                    'Treatment_Delays': self.safe_value(row.get('Treatment_Delays'), 'float'),
                    'Treatment_Period_Considered': self.safe_value(row.get('Treatment_Period_Considered'), 'float'),
                    'Vehicle_Impact': self.safe_value(row.get('Vehicle_Impact'), 'float'),
                }

                ssnb_batch.append(ssnb_data)

            except Exception as e:
                logger.error(f"Error preparing SSNB row {idx}: {str(e)}")
                total_errors += 1

        # Bulk insert
        try:
            if ssnb_batch:
                self.session.bulk_insert_mappings(SSNB, ssnb_batch)
                self.session.commit()
                logger.info(f"✓ SSNB migration complete! Imported: {len(ssnb_batch):,} records")
        except Exception as e:
            logger.error(f"❌ Error inserting SSNB data: {str(e)}")
            self.session.rollback()
            return False

        return True

    def verify_migration(self):
        """Verify migration results"""
        logger.info("\n🔍 Verifying migration...")

        try:
            claim_count = self.session.query(Claim).count()
            ssnb_count = self.session.query(SSNB).count()

            logger.info(f"  Claims: {claim_count:,} records")
            logger.info(f"  SSNB: {ssnb_count:,} records")

            # Sample check
            sample_claim = self.session.query(Claim).first()
            if sample_claim:
                logger.info(f"\n  Sample claim ID: {sample_claim.CLAIMID}")
                logger.info(f"    Primary injury (severity): {sample_claim.PRIMARY_INJURY_BY_SEVERITY}")
                logger.info(f"    Primary injury (causation): {sample_claim.PRIMARY_INJURY_BY_CAUSATION}")
                logger.info(f"    Calculated severity score: {sample_claim.CALCULATED_SEVERITY_SCORE}")
                logger.info(f"    Variance %: {sample_claim.variance_pct}")

        except Exception as e:
            logger.error(f"Verification error: {str(e)}")

        return True

    def run(self):
        """Run complete PostgreSQL migration"""
        logger.info("="*80)
        logger.info("🚀 Starting PostgreSQL Migration to claims_analytics")
        logger.info("="*80)

        start_time = datetime.now()

        try:
            # Initialize
            self.initialize_database()

            # Migrate CSV files
            if not self.migrate_dat_csv():
                return False

            if not self.migrate_ssnb_csv():
                return False

            # Verify
            self.verify_migration()

            # Success
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info("\n" + "="*80)
            logger.info(f"✅ PostgreSQL migration completed in {elapsed:.2f} seconds")
            logger.info("="*80)

            return True

        except Exception as e:
            logger.error(f"❌ Migration failed: {str(e)}")
            return False

        finally:
            if self.session:
                self.session.close()


if __name__ == "__main__":
    # Load DATABASE_URL from environment
    DB_URL = os.getenv('DATABASE_URL')

    if not DB_URL:
        logger.error("DATABASE_URL not found in environment variables")
        logger.error("Please set DATABASE_URL in .env file")
        sys.exit(1)

    # CSV file paths (loaded from environment or use defaults)
    CSV_PATHS = {
        'dat_csv': os.getenv('CSV_FILE_PATH', 'dat.csv'),
        'ssnb_csv': 'SSNB.csv',
    }

    migration = PostgreSQLMigration(
        dat_csv_path=CSV_PATHS['dat_csv'],
        ssnb_csv_path=CSV_PATHS['ssnb_csv'],
        db_url=DB_URL
    )

    success = migration.run()

    if success:
        print("\n✅ PostgreSQL migration completed successfully!")
        print("   Database: claims_analytics")
        print("   Tables: claims, ssnb")
    else:
        print("\n❌ Migration failed - check logs above")
