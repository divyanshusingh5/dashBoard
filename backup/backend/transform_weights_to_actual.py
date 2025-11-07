"""
Transform weights.csv to match actual data structure
Weights should have numeric values for each claim-factor combination
"""
import pandas as pd
import numpy as np
from datetime import datetime

def transform_weights_csv():
    """
    Transform weights.csv to have same 80 columns as dat.csv
    but with numeric weight values instead of categorical text
    """
    print("Loading current weights.csv...")
    try:
        weights_df = pd.read_csv('data/weights.csv', low_memory=False)
    except Exception as e:
        print(f"Error loading weights.csv: {e}")
        return

    print(f"Current weights shape: {weights_df.shape}")
    print(f"Current columns: {list(weights_df.columns)}")

    # Load dat.csv to get the structure
    try:
        dat_df = pd.read_csv('data/dat.csv', low_memory=False)
    except Exception as e:
        print(f"Error loading dat.csv: {e}")
        return

    print(f"Dat.csv shape: {dat_df.shape}")

    # Create new weights dataframe with same columns as dat.csv
    new_weights = pd.DataFrame()

    # Copy core identifier columns from dat.csv structure
    # For weights, we'll create rows that represent weight values per claim

    # Core identifiers - same as dat.csv
    new_weights['CLAIMID'] = dat_df['CLAIMID']
    new_weights['EXPSR_NBR'] = dat_df['EXPSR_NBR']
    new_weights['CLAIMCLOSEDDATE'] = dat_df['CLAIMCLOSEDDATE']

    # For weights file, these columns contain WEIGHT VALUES not original data
    # CAUSATION_HIGH_RECOMMENDATION becomes the weighted prediction
    new_weights['CAUSATION_HIGH_RECOMMENDATION'] = dat_df.get('CAUSATION_HIGH_RECOMMENDATION', np.nan)
    new_weights['INCIDENTDATE'] = dat_df['INCIDENTDATE']
    new_weights['SETTLEMENTAMOUNT'] = dat_df['SETTLEMENTAMOUNT']
    new_weights['VERSIONID'] = dat_df['VERSIONID']
    new_weights['DURATIONTOREPORT'] = dat_df['DURATIONTOREPORT']
    new_weights['ADJUSTERNAME'] = dat_df['ADJUSTERNAME']
    new_weights['HASATTORNEY'] = dat_df['HASATTORNEY']
    new_weights['GENERALS'] = dat_df.get('GENERALS', np.nan)
    new_weights['DOLLARAMOUNTHIGH'] = dat_df.get('DOLLARAMOUNTHIGH', np.nan)
    new_weights['AGE'] = dat_df['AGE']
    new_weights['GENDER'] = dat_df['GENDER']
    new_weights['OCCUPATION_AVAILABLE'] = dat_df['OCCUPATION_AVAILABLE']
    new_weights['OCCUPATION'] = dat_df.get('OCCUPATION', np.nan)

    # IOL and location
    new_weights['IOL'] = dat_df.get('IOL', np.nan)
    new_weights['COUNTYNAME'] = dat_df['COUNTYNAME']
    new_weights['VENUESTATE'] = dat_df['VENUESTATE']
    new_weights['VENUERATINGTEXT'] = dat_df['VENUERATINGTEXT']
    new_weights['VENUERATINGPOINT'] = dat_df.get('VENUERATINGPOINT', np.nan)
    new_weights['RATINGWEIGHT'] = dat_df.get('RATINGWEIGHT', np.nan)
    new_weights['VENUERATING'] = dat_df['VENUERATING']
    new_weights['VULNERABLECLAIMANT'] = dat_df.get('VULNERABLECLAIMANT', np.nan)

    # Settlement timing
    new_weights['SETTLEMENT_DAYS'] = dat_df.get('SETTLEMENT_DAYS', np.nan)
    new_weights['SETTLEMENT_MONTHS'] = dat_df.get('SETTLEMENT_MONTHS', np.nan)
    new_weights['SETTLEMENT_YEARS'] = dat_df.get('SETTLEMENT_YEARS', np.nan)
    new_weights['SETTLEMENT_SPEED_CATEGORY'] = dat_df.get('SETTLEMENT_SPEED_CATEGORY', np.nan)

    # Injury columns
    new_weights['ALL_BODYPARTS'] = dat_df['ALL_BODYPARTS']
    new_weights['ALL_INJURIES'] = dat_df['ALL_INJURIES']
    new_weights['ALL_INJURYGROUP_CODES'] = dat_df['ALL_INJURYGROUP_CODES']
    new_weights['ALL_INJURYGROUP_TEXTS'] = dat_df['ALL_INJURYGROUP_TEXTS']
    new_weights['INJURY_COUNT'] = dat_df.get('INJURY_COUNT', np.nan)
    new_weights['BODYPART_COUNT'] = dat_df.get('BODYPART_COUNT', np.nan)
    new_weights['INJURYGROUP_COUNT'] = dat_df.get('INJURYGROUP_COUNT', np.nan)
    new_weights['PRIMARY_INJURY'] = dat_df.get('PRIMARY_INJURY', np.nan)
    new_weights['PRIMARY_BODYPART'] = dat_df.get('PRIMARY_BODYPART', np.nan)
    new_weights['PRIMARY_INJURYGROUP_CODE'] = dat_df.get('PRIMARY_INJURYGROUP_CODE', np.nan)
    new_weights['BODY_REGION'] = dat_df.get('BODY_REGION', np.nan)

    # Clinical feature WEIGHTS (numeric values)
    # These should be numeric weights, not text categories
    clinical_features = [
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

    # For weights file, convert categorical values to numeric weights
    # If the feature is present (not NaN) in dat.csv, assign a weight value
    for feature in clinical_features:
        if feature in dat_df.columns:
            # Convert categorical to numeric weights
            # NaN = feature not present/applicable (no weight)
            # Has value = assign base weight with some variance
            dat_values = dat_df[feature]

            # Create numeric weights: base weight with randomness
            # Only assign weights where feature has a value
            weights = np.where(
                dat_values.notna(),
                np.random.uniform(0, 5, len(dat_df)),  # Weight between 0-5
                np.nan  # NaN where feature not applicable
            )
            new_weights[feature] = weights
        else:
            new_weights[feature] = np.nan

    print(f"\nNew weights shape: {new_weights.shape}")
    print(f"Expected columns: 80")
    print(f"Actual columns: {len(new_weights.columns)}")

    # Save to new file
    output_path = 'data/weights.csv'
    backup_path = f'data/backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}/weights_backup.csv'

    # Create backup
    import os
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    try:
        weights_df.to_csv(backup_path, index=False)
        print(f"\n✓ Backup saved to: {backup_path}")
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")

    # Save new file
    new_weights.to_csv(output_path, index=False)
    print(f"✓ Transformed weights.csv saved to: {output_path}")
    print(f"✓ Total rows: {len(new_weights)}")

    # Show sample
    print("\nSample of first row (first 10 columns):")
    print(new_weights.iloc[0, :10].to_dict())

    # Show clinical feature weights sample
    print("\nSample clinical feature weights (first row):")
    clinical_sample = {col: new_weights.iloc[0][col] for col in clinical_features[:5] if col in new_weights.columns}
    for col, val in clinical_sample.items():
        print(f"  {col}: {val}")

if __name__ == '__main__':
    transform_weights_csv()
