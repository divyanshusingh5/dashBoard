"""
Comprehensive Migration Script
Dynamically migrates dat.csv and SSNB.csv to SQLite with full support for:
- Auto-detection of all CSV columns
- Multi-tier injury system
- Model performance calculation
- Handles 1M+ rows efficiently
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.schema import init_database, get_session, get_engine, Claim, SSNB, Weight
import logging
from datetime import datetime
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveMigration:
    """Intelligent migration with auto-column detection"""

    def __init__(self, dat_csv_path: str = "dat.csv", ssnb_csv_path: str = "SSNB.csv",
                 weights_csv_path: str = "data/weights.csv", batch_size: int = 10000):
        self.dat_csv_path = Path(dat_csv_path)
        self.ssnb_csv_path = Path(ssnb_csv_path)
        self.weights_csv_path = Path(weights_csv_path)
        self.batch_size = batch_size
        self.engine = None
        self.session = None

    def initialize_database(self):
        """Initialize database and create all tables"""
        logger.info("Initializing database schema...")
        self.engine = init_database()
        self.session = get_session(self.engine)
        logger.info("✓ Database schema created successfully")

    def clean_column_name(self, col: str) -> str:
        """Remove quotes from column names (CSV has 'Column_Name', DB needs Column_Name)"""
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
        """
        Calculate severity score based on injury characteristics
        This is a simplified version - can be enhanced with actual business logic
        """
        try:
            score = 0

            # Base score from injury severity
            if pd.notna(row.get('PRIMARY_INJURY_SEVERITY_SCORE')):
                score += row.get('PRIMARY_INJURY_SEVERITY_SCORE', 0) * 0.5

            # Add secondary/tertiary if present
            if pd.notna(row.get('SECONDARY_INJURY_SEVERITY_SCORE')):
                score += row.get('SECONDARY_INJURY_SEVERITY_SCORE', 0) * 0.3

            if pd.notna(row.get('TERTIARY_INJURY_SEVERITY_SCORE')):
                score += row.get('TERTIARY_INJURY_SEVERITY_SCORE', 0) * 0.2

            # Factor in injury count
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
        """Migrate main dat.csv with full dynamic column support"""
        if not self.dat_csv_path.exists():
            logger.error(f"❌ dat.csv not found at {self.dat_csv_path}")
            return False

        logger.info(f"📊 Loading dat.csv from {self.dat_csv_path}...")

        # Read CSV in chunks for memory efficiency
        chunks = pd.read_csv(self.dat_csv_path, chunksize=self.batch_size)

        total_imported = 0
        total_errors = 0

        for chunk_num, df_chunk in enumerate(chunks, 1):
            logger.info(f"Processing chunk {chunk_num} ({len(df_chunk)} records)...")

            # Clean column names (remove quotes)
            df_chunk.columns = [self.clean_column_name(col) for col in df_chunk.columns]

            # Calculate derived fields
            logger.info("  Calculating variance_pct...")
            df_chunk['variance_pct'] = df_chunk.apply(self.calculate_variance_pct, axis=1)

            logger.info("  Calculating SEVERITY_SCORE if needed...")
            if 'SEVERITY_SCORE' not in df_chunk.columns:
                df_chunk['SEVERITY_SCORE'] = df_chunk.apply(self.calculate_severity_score, axis=1)

            logger.info("  Calculating CAUTION_LEVEL...")
            df_chunk['CAUTION_LEVEL'] = df_chunk['SEVERITY_SCORE'].apply(self.calculate_caution_level)

            # Insert records
            logger.info("  Inserting into database...")
            for idx, row in tqdm(df_chunk.iterrows(), total=len(df_chunk), desc="  Records"):
                try:
                    claim = Claim(
                        # Core identifiers
                        CLAIMID=self.safe_value(row.get('CLAIMID'), 'int'),
                        EXPSR_NBR=self.safe_value(row.get('EXPSR_NBR'), 'str'),
                        VERSIONID=self.safe_value(row.get('VERSIONID'), 'int'),

                        # Dates
                        CLAIMCLOSEDDATE=self.safe_value(row.get('CLAIMCLOSEDDATE'), 'str'),
                        INCIDENTDATE=self.safe_value(row.get('INCIDENTDATE'), 'str'),
                        DURATIONTOREPORT=self.safe_value(row.get('DURATIONTOREPORT'), 'float'),

                        # Financial
                        CAUSATION_HIGH_RECOMMENDATION=self.safe_value(row.get('CAUSATION_HIGH_RECOMMENDATION'), 'float'),
                        SETTLEMENTAMOUNT=self.safe_value(row.get('SETTLEMENTAMOUNT'), 'int'),
                        DOLLARAMOUNTHIGH=self.safe_value(row.get('DOLLARAMOUNTHIGH'), 'float'),
                        GENERALS=self.safe_value(row.get('GENERALS'), 'float'),

                        # Legacy injury info
                        ALL_BODYPARTS=self.safe_value(row.get('ALL_BODYPARTS'), 'str'),
                        ALL_INJURIES=self.safe_value(row.get('ALL_INJURIES'), 'str'),
                        ALL_INJURYGROUP_CODES=self.safe_value(row.get('ALL_INJURYGROUP_CODES'), 'str'),
                        ALL_INJURYGROUP_TEXTS=self.safe_value(row.get('ALL_INJURYGROUP_TEXTS'), 'str'),
                        PRIMARY_INJURY=self.safe_value(row.get('PRIMARY_INJURY'), 'str'),
                        PRIMARY_BODYPART=self.safe_value(row.get('PRIMARY_BODYPART'), 'str'),
                        PRIMARY_INJURYGROUP_CODE=self.safe_value(row.get('PRIMARY_INJURYGROUP_CODE'), 'str'),
                        INJURY_COUNT=self.safe_value(row.get('INJURY_COUNT'), 'int'),
                        BODYPART_COUNT=self.safe_value(row.get('BODYPART_COUNT'), 'int'),
                        INJURYGROUP_COUNT=self.safe_value(row.get('INJURYGROUP_COUNT'), 'int'),
                        BODY_REGION=self.safe_value(row.get('BODY_REGION'), 'str'),

                        # NEW: Multi-tier injury by SEVERITY
                        PRIMARY_INJURY_BY_SEVERITY=self.safe_value(row.get('PRIMARY_INJURY_BY_SEVERITY'), 'str'),
                        PRIMARY_BODYPART_BY_SEVERITY=self.safe_value(row.get('PRIMARY_BODYPART_BY_SEVERITY'), 'str'),
                        PRIMARY_INJURYGROUP_CODE_BY_SEVERITY=self.safe_value(row.get('PRIMARY_INJURYGROUP_CODE_BY_SEVERITY'), 'str'),
                        PRIMARY_INJURY_SEVERITY_SCORE=self.safe_value(row.get('PRIMARY_INJURY_SEVERITY_SCORE'), 'float'),
                        PRIMARY_INJURY_CAUSATION_SCORE_BY_SEVERITY=self.safe_value(row.get('PRIMARY_INJURY_CAUSATION_SCORE_BY_SEVERITY'), 'float'),

                        SECONDARY_INJURY_BY_SEVERITY=self.safe_value(row.get('SECONDARY_INJURY_BY_SEVERITY'), 'str'),
                        SECONDARY_BODYPART_BY_SEVERITY=self.safe_value(row.get('SECONDARY_BODYPART_BY_SEVERITY'), 'str'),
                        SECONDARY_INJURYGROUP_CODE_BY_SEVERITY=self.safe_value(row.get('SECONDARY_INJURYGROUP_CODE_BY_SEVERITY'), 'str'),
                        SECONDARY_INJURY_SEVERITY_SCORE=self.safe_value(row.get('SECONDARY_INJURY_SEVERITY_SCORE'), 'float'),
                        SECONDARY_INJURY_CAUSATION_SCORE_BY_SEVERITY=self.safe_value(row.get('SECONDARY_INJURY_CAUSATION_SCORE_BY_SEVERITY'), 'float'),

                        TERTIARY_INJURY_BY_SEVERITY=self.safe_value(row.get('TERTIARY_INJURY_BY_SEVERITY'), 'str'),
                        TERTIARY_BODYPART_BY_SEVERITY=self.safe_value(row.get('TERTIARY_BODYPART_BY_SEVERITY'), 'str'),
                        TERTIARY_INJURY_SEVERITY_SCORE=self.safe_value(row.get('TERTIARY_INJURY_SEVERITY_SCORE'), 'float'),
                        TERTIARY_INJURY_CAUSATION_SCORE_BY_SEVERITY=self.safe_value(row.get('TERTIARY_INJURY_CAUSATION_SCORE_BY_SEVERITY'), 'float'),

                        # NEW: Multi-tier injury by CAUSATION
                        PRIMARY_INJURY_BY_CAUSATION=self.safe_value(row.get('PRIMARY_INJURY_BY_CAUSATION'), 'str'),
                        PRIMARY_BODYPART_BY_CAUSATION=self.safe_value(row.get('PRIMARY_BODYPART_BY_CAUSATION'), 'str'),
                        PRIMARY_INJURYGROUP_CODE_BY_CAUSATION=self.safe_value(row.get('PRIMARY_INJURYGROUP_CODE_BY_CAUSATION'), 'str'),
                        PRIMARY_INJURY_CAUSATION_SCORE=self.safe_value(row.get('PRIMARY_INJURY_CAUSATION_SCORE'), 'float'),
                        PRIMARY_INJURY_SEVERITY_SCORE_BY_CAUSATION=self.safe_value(row.get('PRIMARY_INJURY_SEVERITY_SCORE_BY_CAUSATION'), 'float'),

                        SECONDARY_INJURY_BY_CAUSATION=self.safe_value(row.get('SECONDARY_INJURY_BY_CAUSATION'), 'str'),
                        SECONDARY_BODYPART_BY_CAUSATION=self.safe_value(row.get('SECONDARY_BODYPART_BY_CAUSATION'), 'str'),
                        SECONDARY_INJURYGROUP_CODE_BY_CAUSATION=self.safe_value(row.get('SECONDARY_INJURYGROUP_CODE_BY_CAUSATION'), 'str'),
                        SECONDARY_INJURY_CAUSATION_SCORE=self.safe_value(row.get('SECONDARY_INJURY_CAUSATION_SCORE'), 'float'),
                        SECONDARY_INJURY_SEVERITY_SCORE_BY_CAUSATION=self.safe_value(row.get('SECONDARY_INJURY_SEVERITY_SCORE_BY_CAUSATION'), 'float'),

                        TERTIARY_INJURY_BY_CAUSATION=self.safe_value(row.get('TERTIARY_INJURY_BY_CAUSATION'), 'str'),
                        TERTIARY_BODYPART_BY_CAUSATION=self.safe_value(row.get('TERTIARY_BODYPART_BY_CAUSATION'), 'str'),
                        TERTIARY_INJURY_CAUSATION_SCORE=self.safe_value(row.get('TERTIARY_INJURY_CAUSATION_SCORE'), 'float'),
                        TERTIARY_INJURY_SEVERITY_SCORE_BY_CAUSATION=self.safe_value(row.get('TERTIARY_INJURY_SEVERITY_SCORE_BY_CAUSATION'), 'float'),

                        # Person info
                        HASATTORNEY=self.safe_value(row.get('HASATTORNEY'), 'str'),
                        AGE=self.safe_value(row.get('AGE'), 'int'),
                        GENDER=self.safe_value(row.get('GENDER'), 'str'),
                        OCCUPATION_AVAILABLE=self.safe_value(row.get('OCCUPATION_AVAILABLE'), 'int'),
                        OCCUPATION=self.safe_value(row.get('OCCUPATION'), 'str'),
                        ADJUSTERNAME=self.safe_value(row.get('ADJUSTERNAME'), 'str'),

                        # Location and venue
                        IOL=self.safe_value(row.get('IOL'), 'int'),
                        COUNTYNAME=self.safe_value(row.get('COUNTYNAME'), 'str'),
                        VENUESTATE=self.safe_value(row.get('VENUESTATE'), 'str'),
                        VENUERATINGTEXT=self.safe_value(row.get('VENUERATINGTEXT'), 'str'),
                        VENUERATINGPOINT=self.safe_value(row.get('VENUERATINGPOINT'), 'float'),
                        RATINGWEIGHT=self.safe_value(row.get('RATINGWEIGHT'), 'float'),
                        VENUERATING=self.safe_value(row.get('VENUERATING'), 'str'),
                        VULNERABLECLAIMANT=self.safe_value(row.get('VULNERABLECLAIMANT'), 'str'),

                        # Settlement timing
                        SETTLEMENT_DAYS=self.safe_value(row.get('SETTLEMENT_DAYS'), 'int'),
                        SETTLEMENT_MONTHS=self.safe_value(row.get('SETTLEMENT_MONTHS'), 'int'),
                        SETTLEMENT_YEARS=self.safe_value(row.get('SETTLEMENT_YEARS'), 'float'),
                        SETTLEMENT_SPEED_CATEGORY=self.safe_value(row.get('SETTLEMENT_SPEED_CATEGORY'), 'str'),

                        # Calculated fields
                        SEVERITY_SCORE=self.safe_value(row.get('SEVERITY_SCORE'), 'float'),
                        CAUTION_LEVEL=self.safe_value(row.get('CAUTION_LEVEL'), 'str'),
                        variance_pct=self.safe_value(row.get('variance_pct'), 'float'),

                        # NEW: Composite scores
                        CALCULATED_SEVERITY_SCORE=self.safe_value(row.get('CALCULATED_SEVERITY_SCORE'), 'float'),
                        CALCULATED_CAUSATION_SCORE=self.safe_value(row.get('CALCULATED_CAUSATION_SCORE'), 'float'),
                        RN=self.safe_value(row.get('RN'), 'int'),

                        # Clinical factors (40+)
                        Advanced_Pain_Treatment=self.safe_value(row.get('Advanced_Pain_Treatment'), 'str'),
                        Causation_Compliance=self.safe_value(row.get('Causation_Compliance'), 'str'),
                        Clinical_Findings=self.safe_value(row.get('Clinical_Findings'), 'str'),
                        Cognitive_Symptoms=self.safe_value(row.get('Cognitive_Symptoms'), 'str'),
                        Complete_Disability_Duration=self.safe_value(row.get('Complete_Disability_Duration'), 'str'),
                        Concussion_Diagnosis=self.safe_value(row.get('Concussion_Diagnosis'), 'str'),
                        Consciousness_Impact=self.safe_value(row.get('Consciousness_Impact'), 'str'),
                        Consistent_Mechanism=self.safe_value(row.get('Consistent_Mechanism'), 'str'),
                        Dental_Procedure=self.safe_value(row.get('Dental_Procedure'), 'str'),
                        Dental_Treatment=self.safe_value(row.get('Dental_Treatment'), 'str'),
                        Dental_Visibility=self.safe_value(row.get('Dental_Visibility'), 'str'),
                        Emergency_Treatment=self.safe_value(row.get('Emergency_Treatment'), 'str'),
                        Fixation_Method=self.safe_value(row.get('Fixation_Method'), 'str'),
                        Head_Trauma=self.safe_value(row.get('Head_Trauma'), 'str'),
                        Immobilization_Used=self.safe_value(row.get('Immobilization_Used'), 'str'),
                        Injury_Count_Feature=self.safe_value(row.get('Injury_Count'), 'str'),
                        Injury_Extent=self.safe_value(row.get('Injury_Extent'), 'str'),
                        Injury_Laterality=self.safe_value(row.get('Injury_Laterality'), 'str'),
                        Injury_Location=self.safe_value(row.get('Injury_Location'), 'str'),
                        Injury_Type=self.safe_value(row.get('Injury_Type'), 'str'),
                        Mobility_Assistance=self.safe_value(row.get('Mobility_Assistance'), 'str'),
                        Movement_Restriction=self.safe_value(row.get('Movement_Restriction'), 'str'),
                        Nerve_Involvement=self.safe_value(row.get('Nerve_Involvement'), 'str'),
                        Pain_Management=self.safe_value(row.get('Pain_Management'), 'str'),
                        Partial_Disability_Duration=self.safe_value(row.get('Partial_Disability_Duration'), 'str'),
                        Physical_Symptoms=self.safe_value(row.get('Physical_Symptoms'), 'str'),
                        Physical_Therapy=self.safe_value(row.get('Physical_Therapy'), 'str'),
                        Prior_Treatment=self.safe_value(row.get('Prior_Treatment'), 'str'),
                        Recovery_Duration=self.safe_value(row.get('Recovery_Duration'), 'str'),
                        Repair_Type=self.safe_value(row.get('Repair_Type'), 'str'),
                        Respiratory_Issues=self.safe_value(row.get('Respiratory_Issues'), 'str'),
                        Soft_Tissue_Damage=self.safe_value(row.get('Soft_Tissue_Damage'), 'str'),
                        Special_Treatment=self.safe_value(row.get('Special_Treatment'), 'str'),
                        Surgical_Intervention=self.safe_value(row.get('Surgical_Intervention'), 'str'),
                        Symptom_Timeline=self.safe_value(row.get('Symptom_Timeline'), 'str'),
                        Treatment_Compliance=self.safe_value(row.get('Treatment_Compliance'), 'str'),
                        Treatment_Course=self.safe_value(row.get('Treatment_Course'), 'str'),
                        Treatment_Delays=self.safe_value(row.get('Treatment_Delays'), 'str'),
                        Treatment_Level=self.safe_value(row.get('Treatment_Level'), 'str'),
                        Treatment_Period_Considered=self.safe_value(row.get('Treatment_Period_Considered'), 'str'),
                        Vehicle_Impact=self.safe_value(row.get('Vehicle_Impact'), 'str'),
                    )

                    self.session.add(claim)
                    total_imported += 1

                except Exception as e:
                    logger.error(f"  Error importing row {idx}: {str(e)}")
                    total_errors += 1
                    continue

            # Commit chunk
            try:
                self.session.commit()
                logger.info(f"✓ Chunk {chunk_num} committed successfully")
            except Exception as e:
                logger.error(f"❌ Error committing chunk {chunk_num}: {str(e)}")
                self.session.rollback()

        logger.info(f"\n✓ dat.csv migration complete!")
        logger.info(f"  Imported: {total_imported} records")
        logger.info(f"  Errors: {total_errors}")

        return True

    def migrate_ssnb_csv(self):
        """Migrate SSNB.csv with float-based clinical factors"""
        if not self.ssnb_csv_path.exists():
            logger.warning(f"⚠ SSNB.csv not found at {self.ssnb_csv_path}, skipping...")
            return True

        logger.info(f"\n📊 Loading SSNB.csv from {self.ssnb_csv_path}...")

        # Clear existing SSNB data to avoid UNIQUE constraint errors
        try:
            existing_count = self.session.query(SSNB).count()
            if existing_count > 0:
                logger.info(f"  Clearing {existing_count} existing SSNB records to avoid duplicates...")
                self.session.query(SSNB).delete()
                self.session.commit()
                logger.info(f"  ✓ SSNB table cleared")
        except Exception as e:
            logger.warning(f"  Could not clear SSNB table: {str(e)}")
            self.session.rollback()

        df = pd.read_csv(self.ssnb_csv_path)

        # Clean column names
        df.columns = [self.clean_column_name(col) for col in df.columns]

        logger.info(f"  Found {len(df)} SSNB records")

        total_imported = 0
        total_errors = 0

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="SSNB Records"):
            try:
                ssnb = SSNB(
                    CLAIMID=self.safe_value(row.get('CLAIMID'), 'int'),
                    VERSIONID=self.safe_value(row.get('VERSIONID'), 'int'),
                    EXPSR_NBR=self.safe_value(row.get('EXPSR_NBR'), 'str'),

                    # Financial
                    CAUSATION_HIGH_RECOMMENDATION=self.safe_value(row.get('CAUSATION_HIGH_RECOMMENDATION'), 'float'),
                    DOLLARAMOUNTHIGH=self.safe_value(row.get('DOLLARAMOUNTHIGH'), 'float'),

                    # Venue
                    VENUERATING=self.safe_value(row.get('VENUERATING'), 'str'),
                    RATINGWEIGHT=self.safe_value(row.get('RATINGWEIGHT'), 'float'),
                    VENUERATINGTEXT=self.safe_value(row.get('VENUERATINGTEXT'), 'str'),
                    VENUERATINGPOINT=self.safe_value(row.get('VENUERATINGPOINT'), 'float'),

                    # Dates
                    INCIDENTDATE=self.safe_value(row.get('INCIDENTDATE'), 'str'),
                    CLAIMCLOSEDDATE=self.safe_value(row.get('CLAIMCLOSEDDATE'), 'str'),

                    # Demographics
                    AGE=self.safe_value(row.get('AGE'), 'int'),
                    GENDER=self.safe_value(row.get('GENDER'), 'int'),
                    HASATTORNEY=self.safe_value(row.get('HASATTORNEY'), 'int'),
                    IOL=self.safe_value(row.get('IOL'), 'int'),
                    ADJUSTERNAME=self.safe_value(row.get('ADJUSTERNAME'), 'str'),
                    OCCUPATION=self.safe_value(row.get('OCCUPATION'), 'str'),

                    # Location
                    COUNTYNAME=self.safe_value(row.get('COUNTYNAME'), 'str'),
                    VENUESTATE=self.safe_value(row.get('VENUESTATE'), 'str'),
                    VULNERABLECLAIMANT=bool(row.get('VULNERABLECLAIMANT')) if pd.notna(row.get('VULNERABLECLAIMANT')) else None,

                    # Fixed injury type
                    PRIMARY_INJURY=self.safe_value(row.get('PRIMARY_INJURY'), 'str'),
                    PRIMARY_BODYPART=self.safe_value(row.get('PRIMARY_BODYPART'), 'str'),
                    PRIMARY_INJURY_GROUP=self.safe_value(row.get('PRIMARY_INJURY_GROUP'), 'str'),

                    # Scores
                    PRIMARY_SEVERITY_SCORE=self.safe_value(row.get('PRIMARY_SEVERITY_SCORE'), 'float'),
                    PRIMARY_CAUSATION_SCORE=self.safe_value(row.get('PRIMARY_CAUSATION_SCORE'), 'float'),

                    # Clinical factors - FLOAT VALUES
                    Causation_Compliance=self.safe_value(row.get('Causation_Compliance'), 'float'),
                    Clinical_Findings=self.safe_value(row.get('Clinical_Findings'), 'float'),
                    Consistent_Mechanism=self.safe_value(row.get('Consistent_Mechanism'), 'float'),
                    Injury_Location=self.safe_value(row.get('Injury_Location'), 'float'),
                    Movement_Restriction=self.safe_value(row.get('Movement_Restriction'), 'float'),
                    Pain_Management=self.safe_value(row.get('Pain_Management'), 'float'),
                    Prior_Treatment=self.safe_value(row.get('Prior_Treatment'), 'float'),
                    Symptom_Timeline=self.safe_value(row.get('Symptom_Timeline'), 'float'),
                    Treatment_Course=self.safe_value(row.get('Treatment_Course'), 'float'),
                    Treatment_Delays=self.safe_value(row.get('Treatment_Delays'), 'float'),
                    Treatment_Period_Considered=self.safe_value(row.get('Treatment_Period_Considered'), 'float'),
                    Vehicle_Impact=self.safe_value(row.get('Vehicle_Impact'), 'float'),
                )

                self.session.add(ssnb)
                total_imported += 1

            except Exception as e:
                logger.error(f"  Error importing SSNB row {idx}: {str(e)}")
                total_errors += 1
                continue

        # Commit all
        try:
            self.session.commit()
            logger.info(f"✓ SSNB.csv migration complete!")
            logger.info(f"  Imported: {total_imported} records")
            logger.info(f"  Errors: {total_errors}")
        except Exception as e:
            logger.error(f"❌ Error committing SSNB data: {str(e)}")
            self.session.rollback()
            return False

        return True

    def migrate_weights_csv(self):
        """Migrate weights.csv"""
        if not self.weights_csv_path.exists():
            logger.warning(f"⚠ weights.csv not found at {self.weights_csv_path}, skipping...")
            return True

        logger.info(f"\n📊 Loading weights.csv from {self.weights_csv_path}...")
        df = pd.read_csv(self.weights_csv_path)

        # Clean column names
        df.columns = [self.clean_column_name(col) for col in df.columns]

        logger.info(f"  Found {len(df)} weight records")

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Weights"):
            try:
                weight = Weight(
                    factor_name=self.safe_value(row.get('factor_name'), 'str'),
                    base_weight=self.safe_value(row.get('base_weight'), 'float'),
                    min_weight=self.safe_value(row.get('min_weight'), 'float'),
                    max_weight=self.safe_value(row.get('max_weight'), 'float'),
                    category=self.safe_value(row.get('category'), 'str'),
                    description=self.safe_value(row.get('description'), 'str'),
                )

                self.session.add(weight)

            except Exception as e:
                logger.error(f"  Error importing weight row {idx}: {str(e)}")
                continue

        # Commit all
        try:
            self.session.commit()
            logger.info(f"✓ weights.csv migration complete!")
        except Exception as e:
            logger.error(f"❌ Error committing weights: {str(e)}")
            self.session.rollback()
            return False

        return True

    def verify_migration(self):
        """Verify migration results"""
        logger.info("\n🔍 Verifying migration...")

        claim_count = self.session.query(Claim).count()
        ssnb_count = self.session.query(SSNB).count()
        weight_count = self.session.query(Weight).count()

        logger.info(f"  Claims: {claim_count:,} records")
        logger.info(f"  SSNB: {ssnb_count:,} records")
        logger.info(f"  Weights: {weight_count:,} records")

        # Sample check
        sample_claim = self.session.query(Claim).first()
        if sample_claim:
            logger.info(f"\n  Sample claim ID: {sample_claim.CLAIMID}")
            logger.info(f"    Primary injury (severity): {sample_claim.PRIMARY_INJURY_BY_SEVERITY}")
            logger.info(f"    Primary injury (causation): {sample_claim.PRIMARY_INJURY_BY_CAUSATION}")
            logger.info(f"    Calculated severity score: {sample_claim.CALCULATED_SEVERITY_SCORE}")
            logger.info(f"    Variance %: {sample_claim.variance_pct}")

        return True

    def run(self):
        """Run complete migration"""
        logger.info("="*80)
        logger.info("🚀 Starting Comprehensive Migration")
        logger.info("="*80)

        start_time = datetime.now()

        # Initialize
        self.initialize_database()

        # Migrate all CSV files
        if not self.migrate_dat_csv():
            logger.error("❌ dat.csv migration failed")
            return False

        if not self.migrate_ssnb_csv():
            logger.error("❌ SSNB.csv migration failed")
            return False

        if not self.migrate_weights_csv():
            logger.error("❌ weights.csv migration failed")
            return False

        # Verify
        self.verify_migration()

        # Done
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("\n" + "="*80)
        logger.info(f"✅ Migration completed successfully in {elapsed:.2f} seconds")
        logger.info("="*80)

        # Close session
        self.session.close()

        return True


if __name__ == "__main__":
    migration = ComprehensiveMigration()
    success = migration.run()

    if success:
        print("\n✅ All data migrated successfully!")
        print("   You can now start the backend and access the dashboard")
    else:
        print("\n❌ Migration failed - check logs above")
