"""
Load CSV files into SQLite database with proper column mapping
Maps CSV columns with single quotes to DB columns without quotes
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from app.db.schema import Base, Claim, Weight
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Map CSV column names (with quotes) to DB column names (without quotes)
CLINICAL_FEATURE_MAPPING = {
    "'Advanced_Pain_Treatment'": 'Advanced_Pain_Treatment',
    "'Causation_Compliance'": 'Causation_Compliance',
    "'Clinical_Findings'": 'Clinical_Findings',
    "'Cognitive_Symptoms'": 'Cognitive_Symptoms',
    "'Complete_Disability_Duration'": 'Complete_Disability_Duration',
    "'Concussion_Diagnosis'": 'Concussion_Diagnosis',
    "'Consciousness_Impact'": 'Consciousness_Impact',
    "'Consistent_Mechanism'": 'Consistent_Mechanism',
    "'Dental_Procedure'": 'Dental_Procedure',
    "'Dental_Treatment'": 'Dental_Treatment',
    "'Dental_Visibility'": 'Dental_Visibility',
    "'Emergency_Treatment'": 'Emergency_Treatment',
    "'Fixation_Method'": 'Fixation_Method',
    "'Head_Trauma'": 'Head_Trauma',
    "'Immobilization_Used'": 'Immobilization_Used',
    "'Injury_Count'": 'Injury_Count_Feature',  # Note: renamed to avoid conflict
    "'Injury_Extent'": 'Injury_Extent',
    "'Injury_Laterality'": 'Injury_Laterality',
    "'Injury_Location'": 'Injury_Location',
    "'Injury_Type'": 'Injury_Type',
    "'Mobility_Assistance'": 'Mobility_Assistance',
    "'Movement_Restriction'": 'Movement_Restriction',
    "'Nerve_Involvement'": 'Nerve_Involvement',
    "'Pain_Management'": 'Pain_Management',
    "'Partial_Disability_Duration'": 'Partial_Disability_Duration',
    "'Physical_Symptoms'": 'Physical_Symptoms',
    "'Physical_Therapy'": 'Physical_Therapy',
    "'Prior_Treatment'": 'Prior_Treatment',
    "'Recovery_Duration'": 'Recovery_Duration',
    "'Repair_Type'": 'Repair_Type',
    "'Respiratory_Issues'": 'Respiratory_Issues',
    "'Soft_Tissue_Damage'": 'Soft_Tissue_Damage',
    "'Special_Treatment'": 'Special_Treatment',
    "'Surgical_Intervention'": 'Surgical_Intervention',
    "'Symptom_Timeline'": 'Symptom_Timeline',
    "'Treatment_Compliance'": 'Treatment_Compliance',
    "'Treatment_Course'": 'Treatment_Course',
    "'Treatment_Delays'": 'Treatment_Delays',
    "'Treatment_Level'": 'Treatment_Level',
    "'Treatment_Period_Considered'": 'Treatment_Period_Considered',
    "'Vehicle_Impact'": 'Vehicle_Impact'
}

def load_claims_data():
    """Load claims data from dat.csv into database"""
    logger.info("Loading dat.csv...")

    # Load CSV
    df = pd.read_csv('data/dat.csv', low_memory=False)
    logger.info(f"Loaded {len(df)} claims from CSV")

    # Rename clinical feature columns (remove quotes)
    df.rename(columns=CLINICAL_FEATURE_MAPPING, inplace=True)

    # Calculate derived fields
    df['variance_pct'] = np.where(
        (df['CAUSATION_HIGH_RECOMMENDATION'].notna()) & (df['CAUSATION_HIGH_RECOMMENDATION'] != 0),
        ((df['DOLLARAMOUNTHIGH'] - df['CAUSATION_HIGH_RECOMMENDATION']) / df['CAUSATION_HIGH_RECOMMENDATION'] * 100),
        0
    )

    # Calculate severity score based on settlement amount
    df['SEVERITY_SCORE'] = pd.cut(
        df['DOLLARAMOUNTHIGH'].fillna(0),
        bins=[0, 10000, 25000, 50000, 100000, float('inf')],
        labels=[3, 5, 7, 9, 10]
    ).astype(float)

    # Calculate caution level
    df['CAUTION_LEVEL'] = pd.cut(
        df['SEVERITY_SCORE'].fillna(5),
        bins=[0, 4, 8, 11],
        labels=['Low', 'Medium', 'High']
    ).astype(str)

    # Create database
    db_path = Path('app/db/claims_analytics.db')
    db_url = f'sqlite:///{db_path}'

    engine = create_engine(db_url, echo=False)

    # Drop and recreate tables
    logger.info("Dropping existing tables...")
    Base.metadata.drop_all(engine)

    logger.info("Creating new tables...")
    Base.metadata.create_all(engine)

    # Load data (use smaller chunksize to avoid SQLite variable limit)
    # SQLite has a limit of 999 SQL variables, with 83 columns we need chunksize <= 999/83 = ~12
    logger.info("Loading data into database...")
    df.to_sql('claims', engine, if_exists='append', index=False, chunksize=10)

    logger.info(f"Successfully loaded {len(df)} claims into database")

    # Verify
    result = pd.read_sql_query("SELECT COUNT(*) as count FROM claims", engine)
    logger.info(f"Verification: {result['count'].iloc[0]} claims in database")

    return engine

def load_weights_data(engine):
    """Load weights data from weights.csv into database"""
    logger.info("Loading weights.csv...")

    # Load CSV
    df = pd.read_csv('data/weights.csv', low_memory=False)
    logger.info(f"Loaded {len(df)} weight records from CSV")

    # Rename clinical feature columns (remove quotes)
    df.rename(columns=CLINICAL_FEATURE_MAPPING, inplace=True)

    # Calculate derived fields (same as claims)
    df['variance_pct'] = np.where(
        (df['CAUSATION_HIGH_RECOMMENDATION'].notna()) & (df['CAUSATION_HIGH_RECOMMENDATION'] != 0),
        ((df['DOLLARAMOUNTHIGH'] - df['CAUSATION_HIGH_RECOMMENDATION']) / df['CAUSATION_HIGH_RECOMMENDATION'] * 100),
        0
    )

    df['SEVERITY_SCORE'] = pd.cut(
        df['DOLLARAMOUNTHIGH'].fillna(0),
        bins=[0, 10000, 25000, 50000, 100000, float('inf')],
        labels=[3, 5, 7, 9, 10]
    ).astype(float)

    df['CAUTION_LEVEL'] = pd.cut(
        df['SEVERITY_SCORE'].fillna(5),
        bins=[0, 4, 8, 11],
        labels=['Low', 'Medium', 'High']
    ).astype(str)

    # Note: For weights table, we store it with same structure but it represents weight values
    # You might want to create a separate table structure for this
    logger.info("Weights have same structure as claims - storing for reference")
    logger.info(f"Weights contain numeric values for clinical features: {df.columns.tolist()[-10:]}")

    # Optionally save weights metadata
    logger.info("Note: weights.csv now has same 80 columns as dat.csv")

    return df

if __name__ == '__main__':
    try:
        engine = load_claims_data()
        weights_df = load_weights_data(engine)
        logger.info("Database loading complete!")
    except Exception as e:
        logger.error(f"Error loading database: {e}")
        raise
