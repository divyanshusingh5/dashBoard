"""
Transform dat.csv and weights.csv to match actual data structure
- dat.csv: 80 columns with proper naming
- weights.csv: Ensure all feature columns are present
"""

import pandas as pd
import numpy as np
from pathlib import Path
import shutil
from datetime import datetime

# Define the exact 80 columns from actual data structure
ACTUAL_COLUMNS = [
    'CLAIMID',
    'EXPSR_NBR',
    'CLAIMCLOSEDDATE',
    'CAUSATION_HIGH_RECOMMENDATION',
    'INCIDENTDATE',
    'SETTLEMENTAMOUNT',
    'VERSIONID',
    'DURATIONTOREPORT',
    'ADJUSTERNAME',
    'HASATTORNEY',
    'GENERALS',
    'DOLLARAMOUNTHIGH',
    'AGE',
    'GENDER',
    'OCCUPATION_AVAILABLE',
    'OCCUPATION',
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
    'BODY_REGION',
    'SETTLEMENT_DAYS',
    'SETTLEMENT_MONTHS',
    'SETTLEMENT_YEARS',
    'SETTLEMENT_SPEED_CATEGORY',
    'IOL',
    'COUNTYNAME',
    'VENUESTATE',
    'VENUERATINGTEXT',
    'VENUERATINGPOINT',
    'RATINGWEIGHT',
    'VENUERATING',
    'VULNERABLECLAIMANT',
    'Advanced_Pain_Treatment',
    'Causation_Compliance',
    'Clinical_Findings',
    'Cognitive_Symptoms',
    'Complete_Disability_Duration',
    'Concussion_Diagnosis',
    'Consciousness_Impact',
    'Consistent_Mechanism',
    'Dental_Procedure',
    'Dental_Treatment',
    'Dental_Visibility',
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

# Feature columns that should be in weights.csv (40 features)
FEATURE_COLUMNS = [
    'Advanced_Pain_Treatment',
    'Causation_Compliance',
    'Clinical_Findings',
    'Cognitive_Symptoms',
    'Complete_Disability_Duration',
    'Concussion_Diagnosis',
    'Consciousness_Impact',
    'Consistent_Mechanism',
    'Dental_Procedure',
    'Dental_Treatment',
    'Dental_Visibility',
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

def create_backup():
    """Create backup of existing CSV files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    data_dir = Path('data')
    backup_dir = data_dir / f'backup_{timestamp}'
    backup_dir.mkdir(exist_ok=True)

    print(f"Creating backup in {backup_dir}...")
    shutil.copy2(data_dir / 'dat.csv', backup_dir / 'dat.csv')
    shutil.copy2(data_dir / 'weights.csv', backup_dir / 'weights.csv')
    print(f"Backup created successfully!")
    return backup_dir

def transform_dat_csv():
    """Transform dat.csv to match actual 80-column structure"""
    print("\n" + "="*60)
    print("Transforming dat.csv...")
    print("="*60)

    # Read current dat.csv
    df = pd.read_csv('data/dat.csv')
    print(f"Current dat.csv shape: {df.shape}")
    print(f"Current columns: {len(df.columns)}")

    # Create new dataframe with actual structure
    new_df = pd.DataFrame()

    # Map existing columns to new structure
    column_mapping = {
        'CLAIMID': 'CLAIMID',
        'EXPSR_NBR': 'EXPSR_NBR',
        'VERSIONID': 'VERSIONID',
        'CLAIMCLOSEDDATE': 'CLAIMCLOSEDDATE',
        'INCIDENTDATE': 'INCIDENTDATE',
        'DURATIONTOREPORT': 'DURATIONTOREPORT',
        'CAUSATION_HIGH_RECOMMENDATION': 'CAUSATION_HIGH_RECOMMENDATION',
        'SETTLEMENTAMOUNT': 'SETTLEMENTAMOUNT',
        'DOLLARAMOUNTHIGH': 'DOLLARAMOUNTHIGH',
        'GENERALS': 'GENERALS',
        'ALL_BODYPARTS': 'ALL_BODYPARTS',
        'ALL_INJURIES': 'ALL_INJURIES',
        'ALL_INJURYGROUP_CODES': 'ALL_INJURYGROUP_CODES',
        'ALL_INJURYGROUP_TEXTS': 'ALL_INJURYGROUP_TEXTS',
        'PRIMARY_INJURY': 'PRIMARY_INJURY',
        'PRIMARY_BODYPART': 'PRIMARY_BODYPART',
        'PRIMARY_INJURYGROUP_CODE': 'PRIMARY_INJURYGROUP_CODE',
        'INJURY_COUNT': 'INJURY_COUNT',
        'BODYPART_COUNT': 'BODYPART_COUNT',
        'INJURYGROUP_COUNT': 'INJURYGROUP_COUNT',
        'HASATTORNEY': 'HASATTORNEY',
        'AGE': 'AGE',
        'GENDER': 'GENDER',
        'ADJUSTERNAME': 'ADJUSTERNAME',
        'IOL': 'IOL',
        'COUNTYNAME': 'COUNTYNAME',
        'VENUESTATE': 'VENUESTATE',
        'VENUERATING': 'VENUERATING',
        'WEIGHTINGINDEX': 'RATINGWEIGHT',
        'BODY_REGION': 'BODY_REGION',
    }

    # Copy mapped columns
    for new_col, old_col in column_mapping.items():
        if old_col in df.columns:
            new_df[new_col] = df[old_col]
        else:
            print(f"Warning: Column {old_col} not found in source, creating empty column")
            new_df[new_col] = np.nan

    # Add missing core columns with default values or calculations
    if 'OCCUPATION_AVAILABLE' not in new_df.columns:
        new_df['OCCUPATION_AVAILABLE'] = 0

    if 'OCCUPATION' not in new_df.columns:
        new_df['OCCUPATION'] = np.nan

    # Calculate settlement-related fields if not present
    if 'SETTLEMENT_DAYS' not in new_df.columns and 'CLAIMCLOSEDDATE' in new_df.columns and 'INCIDENTDATE' in new_df.columns:
        try:
            closed_date = pd.to_datetime(new_df['CLAIMCLOSEDDATE'], errors='coerce')
            incident_date = pd.to_datetime(new_df['INCIDENTDATE'], errors='coerce')
            new_df['SETTLEMENT_DAYS'] = (closed_date - incident_date).dt.days
        except:
            new_df['SETTLEMENT_DAYS'] = 0

    if 'SETTLEMENT_MONTHS' not in new_df.columns:
        new_df['SETTLEMENT_MONTHS'] = (new_df.get('SETTLEMENT_DAYS', 0) / 30).astype(int)

    if 'SETTLEMENT_YEARS' not in new_df.columns:
        new_df['SETTLEMENT_YEARS'] = (new_df.get('SETTLEMENT_DAYS', 0) / 365).round(2)

    if 'SETTLEMENT_SPEED_CATEGORY' not in new_df.columns:
        years = new_df.get('SETTLEMENT_YEARS', 0)
        new_df['SETTLEMENT_SPEED_CATEGORY'] = pd.cut(
            years,
            bins=[-np.inf, 1, 2, 5, np.inf],
            labels=['Within 1 year', 'Within 2 years', 'Within 5 years', 'Over 5 years']
        ).astype(str)

    # Add venue-related fields
    if 'VENUERATINGTEXT' not in new_df.columns:
        new_df['VENUERATINGTEXT'] = new_df.get('VENUERATING', 'Neutral')

    if 'VENUERATINGPOINT' not in new_df.columns:
        rating_map = {'Defense Friendly': 1.0, 'Neutral': 2.0, 'Plaintiff Friendly': 3.0}
        new_df['VENUERATINGPOINT'] = new_df.get('VENUERATING', 'Neutral').map(rating_map)

    if 'VULNERABLECLAIMANT' not in new_df.columns:
        new_df['VULNERABLECLAIMANT'] = np.nan

    # Add all feature columns (copy from existing or create as NaN)
    for feature_col in FEATURE_COLUMNS:
        if feature_col in df.columns:
            new_df[feature_col] = df[feature_col]
        else:
            print(f"Creating new feature column: {feature_col}")
            new_df[feature_col] = np.nan

    # Reorder columns to match ACTUAL_COLUMNS
    final_df = pd.DataFrame()
    for col in ACTUAL_COLUMNS:
        if col in new_df.columns:
            final_df[col] = new_df[col]
        else:
            print(f"Adding missing column: {col}")
            final_df[col] = np.nan

    # Save transformed dat.csv
    final_df.to_csv('data/dat.csv', index=False)
    print(f"\nTransformed dat.csv saved!")
    print(f"New shape: {final_df.shape}")
    print(f"New columns: {len(final_df.columns)}")

    # Show sample of first few columns
    print("\nFirst 5 rows, first 10 columns:")
    print(final_df.iloc[:5, :10])

    return final_df

def verify_weights_csv():
    """Verify weights.csv has all required feature columns"""
    print("\n" + "="*60)
    print("Verifying weights.csv...")
    print("="*60)

    # Read current weights.csv
    df = pd.read_csv('data/weights.csv')
    print(f"Current weights.csv shape: {df.shape}")
    print(f"Current factor_names: {len(df)}")

    existing_factors = set(df['factor_name'].values)
    required_factors = set(FEATURE_COLUMNS)

    missing_factors = required_factors - existing_factors
    extra_factors = existing_factors - required_factors

    print(f"\nExisting factors: {len(existing_factors)}")
    print(f"Required factors: {len(required_factors)}")
    print(f"Missing factors: {len(missing_factors)}")
    print(f"Extra factors: {len(extra_factors)}")

    if missing_factors:
        print("\nMissing factors:")
        for factor in sorted(missing_factors):
            print(f"  - {factor}")

        # Add missing factors with default weights
        print("\nAdding missing factors with default weights...")
        new_rows = []
        for factor in missing_factors:
            # Determine category based on name
            if 'Treatment' in factor or 'Therapy' in factor or 'Pain' in factor:
                category = 'Treatment'
            elif 'Disability' in factor or 'Recovery' in factor:
                category = 'Disability'
            elif 'Injury' in factor or 'Damage' in factor or 'Trauma' in factor:
                category = 'Clinical'
            elif 'Compliance' in factor or 'Mechanism' in factor:
                category = 'Causation'
            else:
                category = 'Clinical'

            new_rows.append({
                'factor_name': factor,
                'base_weight': 0.08,
                'min_weight': 0.03,
                'max_weight': 0.15,
                'category': category,
                'description': f'{factor.replace("_", " ")} factor'
            })

        new_df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        new_df.to_csv('data/weights.csv', index=False)
        print(f"Updated weights.csv saved with {len(new_df)} factors!")
    else:
        print("\nAll required factors present in weights.csv!")

    if extra_factors:
        print("\nExtra factors (not in feature list):")
        for factor in sorted(extra_factors):
            print(f"  - {factor}")

    return df

def main():
    """Main transformation process"""
    print("="*60)
    print("CSV Transformation Script")
    print("Converting to actual data structure (80 columns)")
    print("="*60)

    # Create backup
    backup_dir = create_backup()
    print(f"\nBackup location: {backup_dir}")

    # Transform dat.csv
    transformed_df = transform_dat_csv()

    # Verify weights.csv
    weights_df = verify_weights_csv()

    print("\n" + "="*60)
    print("Transformation Complete!")
    print("="*60)
    print(f"\ndat.csv: {transformed_df.shape[0]} rows × {transformed_df.shape[1]} columns")
    print(f"weights.csv: {len(weights_df)} factors")
    print(f"\nBackup saved to: {backup_dir}")
    print("\nNext steps:")
    print("1. Review the transformed files")
    print("2. Update backend code to handle new structure")
    print("3. Update frontend code if needed")
    print("4. Test the application")

if __name__ == '__main__':
    main()
