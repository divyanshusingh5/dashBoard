"""
Migration Script for ACTUAL dat.csv Structure
Handles 851,118 rows with 80 columns from real production data
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import logging
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

Base = declarative_base()


class Claim(Base):
    """
    Claims table matching ACTUAL dat.csv structure (80 columns)
    """
    __tablename__ = 'claims'

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Core Identifiers
    CLAIMID = Column(Integer, unique=True, nullable=False, index=True)
    EXPSR_NBR = Column(String(50))

    # Dates
    CLAIMCLOSEDDATE = Column(String(50), index=True)
    INCIDENTDATE = Column(String(50))

    # Financial
    CAUSATION_HIGH_RECOMMENDATION = Column(Float)  # Predicted amount
    SETTLEMENTAMOUNT = Column(Integer)
    DOLLARAMOUNTHIGH = Column(Float, index=True)  # Actual settled amount
    GENERALS = Column(Float)
    variance_pct = Column(Float, index=True)  # CALCULATED

    # Version and Timing
    VERSIONID = Column(Integer, index=True)
    DURATIONTOREPORT = Column(Integer)

    # People
    ADJUSTERNAME = Column(String(100), index=True)
    HASATTORNEY = Column(Integer)
    AGE = Column(Integer)
    GENDER = Column(Integer)
    OCCUPATION_AVAILABLE = Column(Integer)
    OCCUPATION = Column(Float)

    # Injury Details
    ALL_BODYPARTS = Column(Text)
    ALL_INJURIES = Column(Text)
    ALL_INJURYGROUP_CODES = Column(Text)
    ALL_INJURYGROUP_TEXTS = Column(Text)
    PRIMARY_INJURY = Column(String(200))
    PRIMARY_BODYPART = Column(String(200))
    PRIMARY_INJURYGROUP_CODE = Column(String(50), index=True)
    INJURY_COUNT = Column(Integer)
    BODYPART_COUNT = Column(Integer)
    INJURYGROUP_COUNT = Column(Integer)
    BODY_REGION = Column(String(100))

    # Settlement Timeline
    SETTLEMENT_DAYS = Column(Integer)
    SETTLEMENT_MONTHS = Column(Integer)
    SETTLEMENT_YEARS = Column(Float)
    SETTLEMENT_SPEED_CATEGORY = Column(String(50))

    # Location and Venue
    IOL = Column(Integer, index=True)  # Impact on Life
    COUNTYNAME = Column(String(100), index=True)
    VENUESTATE = Column(String(50), index=True)
    VENUERATINGTEXT = Column(String(50))
    VENUERATINGPOINT = Column(Float)
    RATINGWEIGHT = Column(Float)
    VENUERATING = Column(String(50), index=True)

    # Risk Indicators
    VULNERABLECLAIMANT = Column(String(50))

    # Clinical Features (40 columns - all from your actual data)
    Advanced_Pain_Treatment = Column(String(100))
    Causation_Compliance = Column(String(100))
    Clinical_Findings = Column(String(100))
    Cognitive_Symptoms = Column(String(100))
    Complete_Disability_Duration = Column(String(100))
    Concussion_Diagnosis = Column(String(100))
    Consciousness_Impact = Column(String(100))
    Consistent_Mechanism = Column(String(100))
    Dental_Procedure = Column(String(100))
    Dental_Treatment = Column(String(100))
    Dental_Visibility = Column(String(100))
    Emergency_Treatment = Column(String(100))
    Fixation_Method = Column(String(100))
    Head_Trauma = Column(String(100))
    Immobilization_Used = Column(String(100))
    Injury_Count_Feature = Column(String(100))
    Injury_Extent = Column(String(100))
    Injury_Laterality = Column(String(100))
    Injury_Location = Column(String(100))
    Injury_Type = Column(String(100))
    Mobility_Assistance = Column(String(100))
    Movement_Restriction = Column(String(100))
    Nerve_Involvement = Column(String(100))
    Pain_Management = Column(String(100))
    Partial_Disability_Duration = Column(String(100))
    Physical_Symptoms = Column(String(100))
    Physical_Therapy = Column(String(100))
    Prior_Treatment = Column(String(100))
    Recovery_Duration = Column(String(100))
    Repair_Type = Column(String(100))
    Respiratory_Issues = Column(String(100))
    Soft_Tissue_Damage = Column(String(100))
    Special_Treatment = Column(String(100))
    Surgical_Intervention = Column(String(100))
    Symptom_Timeline = Column(String(100))
    Treatment_Compliance = Column(Float)
    Treatment_Course = Column(String(100))
    Treatment_Delays = Column(String(100))
    Treatment_Level = Column(String(100))
    Treatment_Period_Considered = Column(String(100))
    Vehicle_Impact = Column(String(100))

    # Calculated fields for compatibility
    SEVERITY_SCORE = Column(Float, index=True)  # CALCULATED from DOLLARAMOUNTHIGH
    CAUTION_LEVEL = Column(String(50), index=True)  # CALCULATED

    # Composite indexes for 5M+ scale performance
    __table_args__ = (
        # Critical for venue shift analysis
        Index('idx_county_venue', 'COUNTYNAME', 'VENUERATING'),
        Index('idx_injury_severity', 'PRIMARY_INJURYGROUP_CODE', 'SEVERITY_SCORE'),
        Index('idx_date_venue', 'CLAIMCLOSEDDATE', 'VENUERATING'),
        Index('idx_date_county', 'CLAIMCLOSEDDATE', 'COUNTYNAME'),

        # For adjuster performance
        Index('idx_adjuster_date', 'ADJUSTERNAME', 'CLAIMCLOSEDDATE'),
        Index('idx_adjuster_variance', 'ADJUSTERNAME', 'variance_pct'),

        # For overview and filtering
        Index('idx_date_variance', 'CLAIMCLOSEDDATE', 'variance_pct'),
        Index('idx_venue_state', 'VENUESTATE', 'VENUERATING'),

        # For isolated factor analysis
        Index('idx_county_venue_injury', 'COUNTYNAME', 'VENUERATING', 'PRIMARY_INJURYGROUP_CODE'),
    )


class Weight(Base):
    """Weights table for feature weights"""
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


def calculate_variance_pct(row):
    """
    Calculate variance percentage
    variance_pct = ((Actual - Predicted) / Predicted) * 100

    Actual = DOLLARAMOUNTHIGH (what was actually paid)
    Predicted = CAUSATION_HIGH_RECOMMENDATION (model prediction)
    """
    try:
        actual = float(row.get('DOLLARAMOUNTHIGH', 0))
        predicted = float(row.get('CAUSATION_HIGH_RECOMMENDATION', 1))  # Avoid division by zero

        if predicted == 0 or pd.isna(predicted):
            return 0.0

        variance = ((actual - predicted) / predicted) * 100
        return round(variance, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


def calculate_severity_score(row):
    """
    Calculate severity score from DOLLARAMOUNTHIGH
    Higher dollar amounts = higher severity
    """
    try:
        amount = float(row.get('DOLLARAMOUNTHIGH', 0))

        if amount < 5000:
            return 1.0
        elif amount < 10000:
            return 2.0
        elif amount < 25000:
            return 4.0
        elif amount < 50000:
            return 6.0
        elif amount < 100000:
            return 8.0
        else:
            return 10.0
    except (ValueError, TypeError):
        return 0.0


def calculate_caution_level(row):
    """
    Calculate caution level from DOLLARAMOUNTHIGH
    """
    try:
        amount = float(row.get('DOLLARAMOUNTHIGH', 0))

        if amount < 10000:
            return 'Low'
        elif amount < 50000:
            return 'Medium'
        else:
            return 'High'
    except (ValueError, TypeError):
        return 'Low'


def migrate_claims(session, dat_csv_path: str, batch_size: int = 5000):
    """
    Migrate ACTUAL dat.csv to SQLite
    Handles all 80 columns from production data
    """
    logger.info(f"Loading claims from: {dat_csv_path}")

    try:
        # Get total rows
        total_rows = sum(1 for _ in open(dat_csv_path, encoding='utf-8')) - 1
        logger.info(f"Total rows to migrate: {total_rows:,}")

        # Clear existing claims
        logger.info("Clearing existing claims...")
        session.execute(text("DELETE FROM claims"))
        session.commit()

        # Read CSV in chunks
        chunk_iterator = pd.read_csv(
            dat_csv_path,
            chunksize=batch_size,
            low_memory=False
        )

        total_migrated = 0

        with tqdm(total=total_rows, desc="Migrating claims") as pbar:
            for chunk_num, chunk in enumerate(chunk_iterator, 1):
                claims_batch = []

                for _, row in chunk.iterrows():
                    # Calculate derived fields
                    variance_pct = calculate_variance_pct(row)
                    severity_score = calculate_severity_score(row)
                    caution_level = calculate_caution_level(row)

                    claim = Claim(
                        # Core identifiers
                        CLAIMID=int(row.get('CLAIMID', 0)),
                        EXPSR_NBR=str(row.get('EXPSR_NBR', '')),

                        # Dates
                        CLAIMCLOSEDDATE=str(row.get('CLAIMCLOSEDDATE', '')),
                        INCIDENTDATE=str(row.get('INCIDENTDATE', '')),

                        # Financial
                        CAUSATION_HIGH_RECOMMENDATION=float(row.get('CAUSATION_HIGH_RECOMMENDATION', 0)) if pd.notna(row.get('CAUSATION_HIGH_RECOMMENDATION')) else None,
                        SETTLEMENTAMOUNT=int(row.get('SETTLEMENTAMOUNT', 0)) if pd.notna(row.get('SETTLEMENTAMOUNT')) else 0,
                        DOLLARAMOUNTHIGH=float(row.get('DOLLARAMOUNTHIGH', 0)) if pd.notna(row.get('DOLLARAMOUNTHIGH')) else None,
                        GENERALS=float(row.get('GENERALS', 0)) if pd.notna(row.get('GENERALS')) else None,
                        variance_pct=variance_pct,

                        # Version and timing
                        VERSIONID=int(row.get('VERSIONID', 0)),
                        DURATIONTOREPORT=int(row.get('DURATIONTOREPORT', 0)) if pd.notna(row.get('DURATIONTOREPORT')) else 0,

                        # People
                        ADJUSTERNAME=str(row.get('ADJUSTERNAME', '')),
                        HASATTORNEY=int(row.get('HASATTORNEY', 0)) if pd.notna(row.get('HASATTORNEY')) else 0,
                        AGE=int(row.get('AGE', 0)) if pd.notna(row.get('AGE')) else None,
                        GENDER=int(row.get('GENDER', 0)) if pd.notna(row.get('GENDER')) else None,
                        OCCUPATION_AVAILABLE=int(row.get('OCCUPATION_AVAILABLE', 0)) if pd.notna(row.get('OCCUPATION_AVAILABLE')) else 0,
                        OCCUPATION=float(row.get('OCCUPATION')) if pd.notna(row.get('OCCUPATION')) else None,

                        # Injury details
                        ALL_BODYPARTS=str(row.get('ALL_BODYPARTS', '')),
                        ALL_INJURIES=str(row.get('ALL_INJURIES', '')),
                        ALL_INJURYGROUP_CODES=str(row.get('ALL_INJURYGROUP_CODES', '')),
                        ALL_INJURYGROUP_TEXTS=str(row.get('ALL_INJURYGROUP_TEXTS', '')),
                        PRIMARY_INJURY=str(row.get('PRIMARY_INJURY', '')),
                        PRIMARY_BODYPART=str(row.get('PRIMARY_BODYPART', '')),
                        PRIMARY_INJURYGROUP_CODE=str(row.get('PRIMARY_INJURYGROUP_CODE', '')),
                        INJURY_COUNT=int(row.get('INJURY_COUNT', 0)) if pd.notna(row.get('INJURY_COUNT')) else None,
                        BODYPART_COUNT=int(row.get('BODYPART_COUNT', 0)) if pd.notna(row.get('BODYPART_COUNT')) else None,
                        INJURYGROUP_COUNT=int(row.get('INJURYGROUP_COUNT', 0)) if pd.notna(row.get('INJURYGROUP_COUNT')) else None,
                        BODY_REGION=str(row.get('BODY_REGION', '')),

                        # Settlement timeline
                        SETTLEMENT_DAYS=int(row.get('SETTLEMENT_DAYS', 0)) if pd.notna(row.get('SETTLEMENT_DAYS')) else None,
                        SETTLEMENT_MONTHS=int(row.get('SETTLEMENT_MONTHS', 0)) if pd.notna(row.get('SETTLEMENT_MONTHS')) else None,
                        SETTLEMENT_YEARS=float(row.get('SETTLEMENT_YEARS', 0)) if pd.notna(row.get('SETTLEMENT_YEARS')) else None,
                        SETTLEMENT_SPEED_CATEGORY=str(row.get('SETTLEMENT_SPEED_CATEGORY', '')),

                        # Location and venue
                        IOL=int(row.get('IOL', 0)) if pd.notna(row.get('IOL')) else None,
                        COUNTYNAME=str(row.get('COUNTYNAME', '')),
                        VENUESTATE=str(row.get('VENUESTATE', '')),
                        VENUERATINGTEXT=str(row.get('VENUERATINGTEXT', '')),
                        VENUERATINGPOINT=float(row.get('VENUERATINGPOINT', 0)) if pd.notna(row.get('VENUERATINGPOINT')) else None,
                        RATINGWEIGHT=float(row.get('RATINGWEIGHT', 0)) if pd.notna(row.get('RATINGWEIGHT')) else None,
                        VENUERATING=str(row.get('VENUERATING', '')),

                        # Risk indicators
                        VULNERABLECLAIMANT=str(row.get('VULNERABLECLAIMANT', '')) if pd.notna(row.get('VULNERABLECLAIMANT')) else None,

                        # Clinical features (40 columns)
                        Advanced_Pain_Treatment=str(row.get('Advanced_Pain_Treatment', '')) if pd.notna(row.get('Advanced_Pain_Treatment')) else None,
                        Causation_Compliance=str(row.get('Causation_Compliance', '')) if pd.notna(row.get('Causation_Compliance')) else None,
                        Clinical_Findings=str(row.get('Clinical_Findings', '')) if pd.notna(row.get('Clinical_Findings')) else None,
                        Cognitive_Symptoms=str(row.get('Cognitive_Symptoms', '')) if pd.notna(row.get('Cognitive_Symptoms')) else None,
                        Complete_Disability_Duration=str(row.get('Complete_Disability_Duration', '')) if pd.notna(row.get('Complete_Disability_Duration')) else None,
                        Concussion_Diagnosis=str(row.get('Concussion_Diagnosis', '')) if pd.notna(row.get('Concussion_Diagnosis')) else None,
                        Consciousness_Impact=str(row.get('Consciousness_Impact', '')) if pd.notna(row.get('Consciousness_Impact')) else None,
                        Consistent_Mechanism=str(row.get('Consistent_Mechanism', '')) if pd.notna(row.get('Consistent_Mechanism')) else None,
                        Dental_Procedure=str(row.get('Dental_Procedure', '')) if pd.notna(row.get('Dental_Procedure')) else None,
                        Dental_Treatment=str(row.get('Dental_Treatment', '')) if pd.notna(row.get('Dental_Treatment')) else None,
                        Dental_Visibility=str(row.get('Dental_Visibility', '')) if pd.notna(row.get('Dental_Visibility')) else None,
                        Emergency_Treatment=str(row.get('Emergency_Treatment', '')) if pd.notna(row.get('Emergency_Treatment')) else None,
                        Fixation_Method=str(row.get('Fixation_Method', '')) if pd.notna(row.get('Fixation_Method')) else None,
                        Head_Trauma=str(row.get('Head_Trauma', '')) if pd.notna(row.get('Head_Trauma')) else None,
                        Immobilization_Used=str(row.get('Immobilization_Used', '')) if pd.notna(row.get('Immobilization_Used')) else None,
                        Injury_Count_Feature=str(row.get('Injury_Count', '')) if pd.notna(row.get('Injury_Count')) else None,
                        Injury_Extent=str(row.get('Injury_Extent', '')) if pd.notna(row.get('Injury_Extent')) else None,
                        Injury_Laterality=str(row.get('Injury_Laterality', '')) if pd.notna(row.get('Injury_Laterality')) else None,
                        Injury_Location=str(row.get('Injury_Location', '')) if pd.notna(row.get('Injury_Location')) else None,
                        Injury_Type=str(row.get('Injury_Type', '')) if pd.notna(row.get('Injury_Type')) else None,
                        Mobility_Assistance=str(row.get('Mobility_Assistance', '')) if pd.notna(row.get('Mobility_Assistance')) else None,
                        Movement_Restriction=str(row.get('Movement_Restriction', '')) if pd.notna(row.get('Movement_Restriction')) else None,
                        Nerve_Involvement=str(row.get('Nerve_Involvement', '')) if pd.notna(row.get('Nerve_Involvement')) else None,
                        Pain_Management=str(row.get('Pain_Management', '')) if pd.notna(row.get('Pain_Management')) else None,
                        Partial_Disability_Duration=str(row.get('Partial_Disability_Duration', '')) if pd.notna(row.get('Partial_Disability_Duration')) else None,
                        Physical_Symptoms=str(row.get('Physical_Symptoms', '')) if pd.notna(row.get('Physical_Symptoms')) else None,
                        Physical_Therapy=str(row.get('Physical_Therapy', '')) if pd.notna(row.get('Physical_Therapy')) else None,
                        Prior_Treatment=str(row.get('Prior_Treatment', '')) if pd.notna(row.get('Prior_Treatment')) else None,
                        Recovery_Duration=str(row.get('Recovery_Duration', '')) if pd.notna(row.get('Recovery_Duration')) else None,
                        Repair_Type=str(row.get('Repair_Type', '')) if pd.notna(row.get('Repair_Type')) else None,
                        Respiratory_Issues=str(row.get('Respiratory_Issues', '')) if pd.notna(row.get('Respiratory_Issues')) else None,
                        Soft_Tissue_Damage=str(row.get('Soft_Tissue_Damage', '')) if pd.notna(row.get('Soft_Tissue_Damage')) else None,
                        Special_Treatment=str(row.get('Special_Treatment', '')) if pd.notna(row.get('Special_Treatment')) else None,
                        Surgical_Intervention=str(row.get('Surgical_Intervention', '')) if pd.notna(row.get('Surgical_Intervention')) else None,
                        Symptom_Timeline=str(row.get('Symptom_Timeline', '')) if pd.notna(row.get('Symptom_Timeline')) else None,
                        Treatment_Compliance=float(row.get('Treatment_Compliance')) if pd.notna(row.get('Treatment_Compliance')) else None,
                        Treatment_Course=str(row.get('Treatment_Course', '')) if pd.notna(row.get('Treatment_Course')) else None,
                        Treatment_Delays=str(row.get('Treatment_Delays', '')) if pd.notna(row.get('Treatment_Delays')) else None,
                        Treatment_Level=str(row.get('Treatment_Level', '')) if pd.notna(row.get('Treatment_Level')) else None,
                        Treatment_Period_Considered=str(row.get('Treatment_Period_Considered', '')) if pd.notna(row.get('Treatment_Period_Considered')) else None,
                        Vehicle_Impact=str(row.get('Vehicle_Impact', '')) if pd.notna(row.get('Vehicle_Impact')) else None,

                        # Calculated fields
                        SEVERITY_SCORE=severity_score,
                        CAUTION_LEVEL=caution_level,
                    )
                    claims_batch.append(claim)

                # Bulk insert
                session.bulk_save_objects(claims_batch)
                session.commit()

                total_migrated += len(claims_batch)
                pbar.update(len(chunk))

                if chunk_num % 10 == 0:
                    logger.info(f"Migrated {total_migrated:,} / {total_rows:,} claims...")

        logger.info(f"✓ Successfully migrated {total_migrated:,} claims")
        return True

    except Exception as e:
        logger.error(f"Error migrating claims: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return False


def migrate_weights(session, weights_csv_path: str):
    """Migrate weights.csv to database"""
    logger.info(f"Loading weights from: {weights_csv_path}")

    try:
        df = pd.read_csv(weights_csv_path)
        logger.info(f"Loaded {len(df)} weight records")

        # Clear existing weights
        session.query(Weight).delete()
        session.commit()

        # Insert weights
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Migrating weights"):
            weight = Weight(
                factor_name=str(row['factor_name']),
                base_weight=float(row['base_weight']),
                min_weight=float(row['min_weight']),
                max_weight=float(row['max_weight']),
                category=str(row['category']),
                description=str(row.get('description', ''))
            )
            session.add(weight)

        session.commit()
        logger.info(f"✓ Successfully migrated {len(df)} weights")
        return True

    except Exception as e:
        logger.error(f"Error migrating weights: {e}")
        session.rollback()
        return False


def main():
    """Main migration function"""
    logger.info("=" * 60)
    logger.info("ACTUAL DAT.CSV MIGRATION (851,118 rows, 80 columns)")
    logger.info("=" * 60)

    # Paths
    data_dir = Path(__file__).parent / "data"
    dat_csv = data_dir / "dat.csv"
    weights_csv = data_dir / "weights.csv"

    # Check files
    if not dat_csv.exists():
        logger.error(f"dat.csv not found at: {dat_csv}")
        return

    if not weights_csv.exists():
        logger.error(f"weights.csv not found at: {weights_csv}")
        logger.warning("Continuing without weights...")

    # Create database
    db_path = Path(__file__).parent / "app" / "db" / "claims_analytics.db"
    db_url = f"sqlite:///{db_path}"

    logger.info("Creating database with ACTUAL schema...")
    engine = create_engine(
        db_url,
        echo=False,
        pool_size=20,
        max_overflow=40,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.drop_all(engine)  # Drop old schema
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        # Migrate weights
        if weights_csv.exists():
            if not migrate_weights(session, str(weights_csv)):
                logger.error("Failed to migrate weights")
                return

        # Migrate claims
        if not migrate_claims(session, str(dat_csv), batch_size=5000):
            logger.error("Failed to migrate claims")
            return

        logger.info("=" * 60)
        logger.info("✓ MIGRATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Database location: {db_path}")
        logger.info("You can now start the API server:")
        logger.info("  python -m uvicorn app.main:app --reload")

    finally:
        session.close()


if __name__ == "__main__":
    main()
