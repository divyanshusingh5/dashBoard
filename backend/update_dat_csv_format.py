"""
Update dat.csv to match actual production data format
Changes column names from test format to actual format
"""

import pandas as pd
import numpy as np

# Load existing dat.csv
df = pd.read_csv('data/dat.csv')

print(f"Loaded {len(df)} rows from dat.csv")
print(f"Current columns: {len(df.columns)}")

# Column name mapping: old -> new
column_mapping = {
    'claim_id': 'CLAIMID',
    'claim_date': 'CLAIMCLOSEDDATE',
    'adjuster': 'ADJUSTERNAME',
    'predicted_pain_suffering': 'CAUSATION_HIGH_RECOMMENDATION',
    'VENUE_RATING': 'VENUERATING',
    'RATINGWEIGHT': 'WEIGHTINGINDEX',
    'INJURY_GROUP_CODE': 'PRIMARY_INJURYGROUP_CODE',
    'IMPACT': 'IOL',
}

# Rename columns
df = df.rename(columns=column_mapping)

# Convert CLAIMID from string to integer
# Extract numeric part from "CLM-2025-000001" format
if df['CLAIMID'].dtype == 'object':  # If string type
    df['CLAIMID'] = df['CLAIMID'].str.extract(r'(\d+)$').astype(int)
else:  # Already numeric
    df['CLAIMID'] = df['CLAIMID'].astype(int)

# Add new columns that exist in actual data
df['EXPSR_NBR'] = df['CLAIMID'].astype(str).str.zfill(8) + '-EXP'

# Calculate INCIDENTDATE (random days before claim close date)
incident_dates = []
for close_date in pd.to_datetime(df['CLAIMCLOSEDDATE']):
    days_before = np.random.randint(1, 180)
    incident_date = close_date - pd.Timedelta(days=days_before)
    incident_dates.append(incident_date.strftime('%Y-%m-%d'))
df['INCIDENTDATE'] = incident_dates

# Add person information
df['HASATTORNEY'] = np.random.choice(['Yes', 'No'], len(df), p=[0.35, 0.65])
df['AGE'] = np.random.randint(25, 75, len(df))
df['GENDER'] = np.random.choice(['Male', 'Female'], len(df), p=[0.52, 0.48])

# Add financial columns
df['SETTLEMENTAMOUNT'] = (df['DOLLARAMOUNTHIGH'] * 0.85).astype(int)
df['GENERALS'] = (df['DOLLARAMOUNTHIGH'] * 0.40).round(2)

# Add body region
body_regions = ['Head/Neck', 'Upper Extremity', 'Lower Extremity', 'Spine', 'Torso', 'Multiple']
df['BODY_REGION'] = np.random.choice(body_regions, len(df))

# Remove old columns that don't exist in actual data
columns_to_remove = [
    'SETTLEMENT_DAYS',
    'SETTLEMENT_MONTHS',
    'SETTLEMENT_YEARS',
    'CAUSATION__HIGH_RECOMMENDATION',  # typo column
    'causation_probability',
    'causation_tx_delay',
    'causation_tx_gaps',
    'causation_compliance',
    'severity_allowed_tx_period',
    'severity_initial_tx',
    'severity_injections',
    'severity_objective_findings',
    'severity_pain_mgmt',
    'severity_type_tx',
    'severity_injury_site',
    'severity_code'
]

# Remove columns if they exist
for col in columns_to_remove:
    if col in df.columns:
        df = df.drop(columns=[col])

# Reorder columns to match actual data structure
column_order = [
    # Core identifiers
    'CLAIMID',
    'EXPSR_NBR',
    'VERSIONID',

    # Dates
    'CLAIMCLOSEDDATE',
    'INCIDENTDATE',
    'DURATIONTOREPORT',

    # Financial
    'CAUSATION_HIGH_RECOMMENDATION',
    'SETTLEMENTAMOUNT',
    'DOLLARAMOUNTHIGH',
    'GENERALS',

    # Injury information
    'ALL_BODYPARTS',
    'ALL_INJURIES',
    'ALL_INJURYGROUP_CODES',
    'ALL_INJURYGROUP_TEXTS',
    'PRIMARY_INJURY',
    'PRIMARY_BODYPART',
    'PRIMARY_INJURYGROUP_CODE',
    'INJURY_COUNT',
    'BODYPART_COUNT',
    'INJURYGROUP_COUNT',

    # Person information
    'HASATTORNEY',
    'AGE',
    'GENDER',
    'ADJUSTERNAME',

    # Location and venue
    'IOL',
    'COUNTYNAME',
    'VENUESTATE',
    'VENUERATING',
    'WEIGHTINGINDEX',
    'BODY_REGION',

    # Calculated fields
    'SEVERITY_SCORE',
    'CAUTION_LEVEL',
    'variance_pct',
]

# Add all clinical feature columns at the end
clinical_features = [
    'Advanced_Pain_Treatment',
    'Causation_Compliance',
    'Clinical_Findings',
    'Cognitive_Symptoms',
    'Complete_Disability_Duration',
    'Concussion_Diagnosis',
    'Consciousness_Impact',
    'Consistent_Mechanism',
    'Dental_Procedure',
    'Emergency_Treatment',
    'Fixation_Method',
    'Head_Trauma',
    'Immobilization_Used',
    'Injury_Count',
    'Injury_Extent',
    'Injury_Laterality',
    'Injury_Location',
    'Injury_Type',
    'Mobility_Assistance',
    'Movement_Restriction',
    'Nerve_Involvement',
    'Pain_Management',
    'Partial_Disability_Duration',
    'Physical_Symptoms',
    'Physical_Therapy',
    'Prior_Treatment',
    'Recovery_Duration',
    'Repair_Type',
    'Respiratory_Issues',
    'Soft_Tissue_Damage',
    'Special_Treatment',
    'Surgical_Intervention',
    'Symptom_Timeline',
    'Treatment_Compliance',
    'Treatment_Course',
    'Treatment_Delays',
    'Treatment_Level',
    'Treatment_Period_Considered',
    'Vehicle_Impact'
]

# Only add columns that exist in the DataFrame
final_column_order = []
for col in column_order:
    if col in df.columns:
        final_column_order.append(col)

for col in clinical_features:
    if col in df.columns and col not in final_column_order:
        final_column_order.append(col)

# Reorder DataFrame
df = df[final_column_order]

# Save updated CSV
df.to_csv('data/dat.csv', index=False)

print(f"\n[SUCCESS] Updated dat.csv successfully!")
print(f"[SUCCESS] New columns: {len(df.columns)}")
print(f"[SUCCESS] Total rows: {len(df)}")
print(f"\nFirst few columns: {list(df.columns[:10])}")
print(f"\nSample CLAIMID values: {df['CLAIMID'].head().tolist()}")
