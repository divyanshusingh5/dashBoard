"""
Transform current dat.csv to match actual data structure
Based on 80 columns from the real dataset
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Column names from actual data (80 columns total)
ACTUAL_COLUMNS = [
    'CLAIMID', 'EXPSR_NBR', 'CLAIMCLOSEDDATE', 'CAUSATION_HIGH_RECOMMENDATION',
    'INCIDENTDATE', 'SETTLEMENTAMOUNT', 'VERSIONID', 'DURATIONTOREPORT',
    'ADJUSTERNAME', 'HASATTORNEY', 'GENERALS', 'DOLLARAMOUNTHIGH',
    'AGE', 'GENDER', 'OCCUPATION_AVAILABLE', 'OCCUPATION',
    'ALL_BODYPARTS', 'ALL_INJURIES', 'ALL_INJURYGROUP_CODES', 'ALL_INJURYGROUP_TEXTS',
    'PRIMARY_INJURY', 'PRIMARY_BODYPART', 'PRIMARY_INJURYGROUP_CODE',
    'INJURY_COUNT', 'BODYPART_COUNT', 'INJURYGROUP_COUNT', 'BODY_REGION',
    'SETTLEMENT_DAYS', 'SETTLEMENT_MONTHS', 'SETTLEMENT_YEARS', 'SETTLEMENT_SPEED_CATEGORY',
    'IOL', 'COUNTYNAME', 'VENUESTATE', 'VENUERATINGTEXT', 'VENUERATINGPOINT',
    'RATINGWEIGHT', 'VENUERATING', 'VULNERABLECLAIMANT',
    "'Advanced_Pain_Treatment'", "'Causation_Compliance'", "'Clinical_Findings'",
    "'Cognitive_Symptoms'", "'Complete_Disability_Duration'", "'Concussion_Diagnosis'",
    "'Consciousness_Impact'", "'Consistent_Mechanism'", "'Dental_Procedure'",
    "'Dental_Treatment'", "'Dental_Visibility'", "'Emergency_Treatment'",
    "'Fixation_Method'", "'Head_Trauma'", "'Immobilization_Used'",
    "'Injury_Count'", "'Injury_Extent'", "'Injury_Laterality'",
    "'Injury_Location'", "'Injury_Type'", "'Mobility_Assistance'",
    "'Movement_Restriction'", "'Nerve_Involvement'", "'Pain_Management'",
    "'Partial_Disability_Duration'", "'Physical_Symptoms'", "'Physical_Therapy'",
    "'Prior_Treatment'", "'Recovery_Duration'", "'Repair_Type'",
    "'Respiratory_Issues'", "'Soft_Tissue_Damage'", "'Special_Treatment'",
    "'Surgical_Intervention'", "'Symptom_Timeline'", "'Treatment_Compliance'",
    "'Treatment_Course'", "'Treatment_Delays'", "'Treatment_Level'",
    "'Treatment_Period_Considered'", "'Vehicle_Impact'"
]

def transform_dat_csv():
    """Transform current dat.csv to actual structure"""
    print("Loading current dat.csv...")
    try:
        df = pd.read_csv('data/dat.csv', low_memory=False)
    except Exception as e:
        print(f"Error loading dat.csv: {e}")
        return

    print(f"Current shape: {df.shape}")
    print(f"Current columns: {list(df.columns)[:10]}...")

    # Create new dataframe with actual columns
    new_df = pd.DataFrame()

    # Map existing columns to new structure
    # Core identifiers
    new_df['CLAIMID'] = df.get('CLAIMID', range(1, len(df) + 1))
    new_df['EXPSR_NBR'] = df.get('EXPSR_NBR', [f"{i:08d}-EXP" for i in range(1, len(df) + 1)])

    # Dates - keep as strings in format "YYYY-MM-DD HH:MM:SS.000"
    new_df['CLAIMCLOSEDDATE'] = df.get('CLAIMCLOSEDDATE', pd.to_datetime('2024-01-01').strftime('%Y-%m-%d %H:%M:%S.000'))
    new_df['INCIDENTDATE'] = df.get('INCIDENTDATE', pd.to_datetime('2023-01-01').strftime('%Y-%m-%d %H:%M:%S.000'))

    # Financial
    new_df['CAUSATION_HIGH_RECOMMENDATION'] = df.get('CAUSATION_HIGH_RECOMMENDATION', df.get('DOLLARAMOUNTHIGH', 10000))
    new_df['SETTLEMENTAMOUNT'] = df.get('SETTLEMENTAMOUNT', 0)
    new_df['DOLLARAMOUNTHIGH'] = df.get('DOLLARAMOUNTHIGH', 10000)
    new_df['GENERALS'] = df.get('GENERALS', new_df['DOLLARAMOUNTHIGH'] * 0.4)

    # Version and duration
    new_df['VERSIONID'] = df.get('VERSIONID', 1)
    new_df['DURATIONTOREPORT'] = df.get('DURATIONTOREPORT', np.random.randint(0, 30, len(df)))

    # Person info
    new_df['ADJUSTERNAME'] = df.get('ADJUSTERNAME', 'System System')
    new_df['HASATTORNEY'] = df.get('HASATTORNEY', 0)
    new_df['AGE'] = df.get('AGE', np.random.randint(20, 70, len(df)))
    new_df['GENDER'] = df.get('GENDER', np.random.choice([1, 2], len(df)))
    new_df['OCCUPATION_AVAILABLE'] = df.get('OCCUPATION_AVAILABLE', 0)
    new_df['OCCUPATION'] = df.get('OCCUPATION', np.nan)

    # Injury information
    new_df['ALL_BODYPARTS'] = df.get('ALL_BODYPARTS', 'Knee')
    new_df['ALL_INJURIES'] = df.get('ALL_INJURIES', 'Sprain/Strain')
    new_df['ALL_INJURYGROUP_CODES'] = df.get('ALL_INJURYGROUP_CODES', 'SSLE')
    new_df['ALL_INJURYGROUP_TEXTS'] = df.get('ALL_INJURYGROUP_TEXTS', 'Sprain/Strain, Lower Extremity')
    new_df['PRIMARY_INJURY'] = df.get('PRIMARY_INJURY', 'Sprain/Strain')
    new_df['PRIMARY_BODYPART'] = df.get('PRIMARY_BODYPART', 'Knee')
    new_df['PRIMARY_INJURYGROUP_CODE'] = df.get('PRIMARY_INJURYGROUP_CODE', 'SSLE')
    new_df['INJURY_COUNT'] = df.get('INJURY_COUNT', 1)
    new_df['BODYPART_COUNT'] = df.get('BODYPART_COUNT', 1)
    new_df['INJURYGROUP_COUNT'] = df.get('INJURYGROUP_COUNT', 1)
    new_df['BODY_REGION'] = df.get('BODY_REGION', 'Lower Extremity')

    # Settlement timing
    new_df['SETTLEMENT_DAYS'] = df.get('SETTLEMENT_DAYS', np.random.randint(30, 1000, len(df)))
    new_df['SETTLEMENT_MONTHS'] = (new_df['SETTLEMENT_DAYS'] / 30).astype(int)
    new_df['SETTLEMENT_YEARS'] = round(new_df['SETTLEMENT_DAYS'] / 365, 2)
    new_df['SETTLEMENT_SPEED_CATEGORY'] = df.get('SETTLEMENT_SPEED_CATEGORY', 'Within 5 years')

    # Location and venue
    new_df['IOL'] = df.get('IOL', df.get('IMPACT', np.random.choice([1, 2, 3], len(df))))
    new_df['COUNTYNAME'] = df.get('COUNTYNAME', 'Unknown')
    new_df['VENUESTATE'] = df.get('VENUESTATE', 'IL')
    new_df['VENUERATINGTEXT'] = df.get('VENUERATINGTEXT', df.get('VENUERATING', 'Neutral'))
    new_df['VENUERATINGPOINT'] = df.get('VENUERATINGPOINT', 2.0)
    new_df['RATINGWEIGHT'] = df.get('RATINGWEIGHT', df.get('WEIGHTINGINDEX', 100.0))
    new_df['VENUERATING'] = df.get('VENUERATING', 'Neutral')
    new_df['VULNERABLECLAIMANT'] = df.get('VULNERABLECLAIMANT', np.nan)

    # Clinical features (40+ columns with single quotes)
    # Map from old column names (without quotes) to new (with quotes)
    clinical_features = {
        'Advanced_Pain_Treatment': "'Advanced_Pain_Treatment'",
        'Causation_Compliance': "'Causation_Compliance'",
        'Clinical_Findings': "'Clinical_Findings'",
        'Cognitive_Symptoms': "'Cognitive_Symptoms'",
        'Complete_Disability_Duration': "'Complete_Disability_Duration'",
        'Concussion_Diagnosis': "'Concussion_Diagnosis'",
        'Consciousness_Impact': "'Consciousness_Impact'",
        'Consistent_Mechanism': "'Consistent_Mechanism'",
        'Dental_Procedure': "'Dental_Procedure'",
        'Dental_Treatment': "'Dental_Treatment'",
        'Dental_Visibility': "'Dental_Visibility'",
        'Emergency_Treatment': "'Emergency_Treatment'",
        'Fixation_Method': "'Fixation_Method'",
        'Head_Trauma': "'Head_Trauma'",
        'Immobilization_Used': "'Immobilization_Used'",
        'Injury_Count': "'Injury_Count'",
        'Injury_Extent': "'Injury_Extent'",
        'Injury_Laterality': "'Injury_Laterality'",
        'Injury_Location': "'Injury_Location'",
        'Injury_Type': "'Injury_Type'",
        'Mobility_Assistance': "'Mobility_Assistance'",
        'Movement_Restriction': "'Movement_Restriction'",
        'Nerve_Involvement': "'Nerve_Involvement'",
        'Pain_Management': "'Pain_Management'",
        'Partial_Disability_Duration': "'Partial_Disability_Duration'",
        'Physical_Symptoms': "'Physical_Symptoms'",
        'Physical_Therapy': "'Physical_Therapy'",
        'Prior_Treatment': "'Prior_Treatment'",
        'Recovery_Duration': "'Recovery_Duration'",
        'Repair_Type': "'Repair_Type'",
        'Respiratory_Issues': "'Respiratory_Issues'",
        'Soft_Tissue_Damage': "'Soft_Tissue_Damage'",
        'Special_Treatment': "'Special_Treatment'",
        'Surgical_Intervention': "'Surgical_Intervention'",
        'Symptom_Timeline': "'Symptom_Timeline'",
        'Treatment_Compliance': "'Treatment_Compliance'",
        'Treatment_Course': "'Treatment_Course'",
        'Treatment_Delays': "'Treatment_Delays'",
        'Treatment_Level': "'Treatment_Level'",
        'Treatment_Period_Considered': "'Treatment_Period_Considered'",
        'Vehicle_Impact': "'Vehicle_Impact'"
    }

    for old_name, new_name in clinical_features.items():
        if old_name in df.columns:
            new_df[new_name] = df[old_name]
        else:
            # Fill with mostly NaN, some with sample values
            new_df[new_name] = np.nan

    print(f"\nNew shape: {new_df.shape}")
    print(f"Expected columns: {len(ACTUAL_COLUMNS)}")
    print(f"Actual columns: {len(new_df.columns)}")

    # Verify all columns are present
    missing = set(ACTUAL_COLUMNS) - set(new_df.columns)
    if missing:
        print(f"Missing columns: {missing}")

    # Save to new file
    output_path = 'data/dat.csv'
    backup_path = f'data/backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}/dat_backup.csv'

    # Create backup
    import os
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    try:
        df.to_csv(backup_path, index=False)
        print(f"\n✓ Backup saved to: {backup_path}")
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")

    # Save new file
    new_df.to_csv(output_path, index=False)
    print(f"✓ Transformed dat.csv saved to: {output_path}")
    print(f"✓ Total rows: {len(new_df)}")

    # Show sample
    print("\nSample of first row:")
    print(new_df.iloc[0].to_dict())

if __name__ == '__main__':
    transform_dat_csv()
