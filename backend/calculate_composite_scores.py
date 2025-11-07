"""
Calculate Composite Scores: SEVERITY_SCORE and CAUSATION_SCORE
Based on weighted clinical factors from weights.csv

SEVERITY_SCORE: Sum of all severity-related factors
- Injury extent, type, surgical needs, disability duration, etc.

CAUSATION_SCORE: Sum of all causation/compliance-related factors
- Treatment compliance, delays, consistency, timely care, etc.
"""

# SEVERITY-RELATED FACTORS (19 factors)
# These indicate the physical severity and extent of the injury
# Note: Removed 'Injury_Count' to avoid duplicate with INJURY_COUNT column in dat.csv
SEVERITY_FACTORS = [
    'Injury_Extent',           # How extensive the injury is
    'Injury_Type',             # Type of injury (fracture, sprain, etc.)
    'Injury_Location',         # Where injury occurred
    'Injury_Laterality',       # Left/right/bilateral
    # 'Injury_Count',          # REMOVED - duplicate of INJURY_COUNT column 24
    'Head_Trauma',             # Head injuries (serious)
    'Concussion_Diagnosis',    # Brain injury
    'Consciousness_Impact',    # Loss of consciousness
    'Nerve_Involvement',       # Nerve damage
    'Soft_Tissue_Damage',      # Soft tissue extent
    'Cognitive_Symptoms',      # Brain function impact
    'Physical_Symptoms',       # Severity of symptoms
    'Respiratory_Issues',      # Breathing complications
    'Surgical_Intervention',   # Surgery required
    'Fixation_Method',         # Hardware needed
    'Complete_Disability_Duration',  # Total disability period
    'Partial_Disability_Duration',   # Partial disability period
    'Mobility_Assistance',     # Wheelchair, crutches needed
    'Movement_Restriction',    # Limited movement
    'Dental_Visibility',       # Visible dental damage
]

# CAUSATION/COMPLIANCE-RELATED FACTORS (21 factors)
# These indicate whether patient followed medical advice and treatment protocols
CAUSATION_FACTORS = [
    'Causation_Compliance',    # Did patient follow treatment plan?
    'Treatment_Compliance',    # Adherence to prescribed treatment
    'Treatment_Delays',        # Delays in seeking/receiving care
    'Consistent_Mechanism',    # Injury consistent with incident?
    'Clinical_Findings',       # Clinical evidence supports claim
    'Emergency_Treatment',     # Immediate care sought
    'Treatment_Course',        # Proper treatment progression
    'Symptom_Timeline',        # Symptoms match injury timeline
    'Prior_Treatment',         # Pre-existing conditions treated
    'Recovery_Duration',       # Expected vs actual recovery
    'Treatment_Period_Considered',  # Appropriate treatment timeframe
    'Treatment_Level',         # Appropriate care level
    'Pain_Management',         # Proper pain management
    'Physical_Therapy',        # PT compliance
    'Advanced_Pain_Treatment', # Advanced treatments used
    'Special_Treatment',       # Special procedures
    'Immobilization_Used',     # Proper immobilization
    'Dental_Treatment',        # Dental care received
    'Dental_Procedure',        # Dental procedures done
    'Repair_Type',             # Appropriate repair method
    'Vehicle_Impact',          # Accident severity/causation
]


def calculate_severity_score(row):
    """
    Calculate SEVERITY_SCORE as sum of severity-related factor weights

    Args:
        row: DataFrame row or dict with clinical factor weights

    Returns:
        float: Total severity score (0-100 range expected)
    """
    severity_score = 0.0

    for factor in SEVERITY_FACTORS:
        # Get weight value, handle missing/null values
        weight = row.get(factor, 0)
        if weight and weight != '' and str(weight).lower() not in ['nan', 'none', 'null']:
            try:
                severity_score += float(weight)
            except (ValueError, TypeError):
                pass

    return round(severity_score, 2)


def calculate_causation_score(row):
    """
    Calculate CAUSATION_SCORE as sum of causation/compliance-related factor weights

    Higher score = Better causation/compliance
    - Patient followed doctor's orders
    - Timely medical treatment
    - Consistent injury mechanism
    - Proper treatment progression

    Args:
        row: DataFrame row or dict with clinical factor weights

    Returns:
        float: Total causation score (0-100 range expected)
    """
    causation_score = 0.0

    for factor in CAUSATION_FACTORS:
        # Get weight value, handle missing/null values
        weight = row.get(factor, 0)
        if weight and weight != '' and str(weight).lower() not in ['nan', 'none', 'null']:
            try:
                causation_score += float(weight)
            except (ValueError, TypeError):
                pass

    return round(causation_score, 2)


def categorize_severity(severity_score):
    """
    Categorize severity score into Low/Medium/High

    Based on actual data distribution:
    - Mean: 20.75, Std: 4.38
    - 25th percentile: 17.83
    - 75th percentile: 23.60

    Thresholds (adjusted based on real data):
    - Low: < 18 (bottom ~28%)
    - Medium: 18-24 (middle ~58%)
    - High: >= 24 (top ~14%)
    """
    if severity_score < 18:
        return 'Low'
    elif severity_score < 24:
        return 'Medium'
    else:
        return 'High'


def categorize_causation(causation_score):
    """
    Categorize causation score into Low/Medium/High

    Higher score = Better causation/compliance

    Based on actual data distribution:
    - Mean: 35.60, Std: 5.57
    - 25th percentile: 31.61
    - 75th percentile: 39.38

    Thresholds (adjusted based on real data):
    - Low: < 32 (bottom ~28% - Poor compliance)
    - Medium: 32-39 (middle ~58% - Moderate compliance)
    - High: >= 39 (top ~14% - Good compliance)
    """
    if causation_score < 32:
        return 'Low'      # Poor compliance
    elif causation_score < 39:
        return 'Medium'   # Moderate compliance
    else:
        return 'High'     # Good compliance


def calculate_caution_level(severity_score, causation_score):
    """
    Calculate overall CAUTION_LEVEL based on both scores

    Logic:
    - High Severity + Low Causation = High Risk (needs review)
    - High Severity + High Causation = Medium Risk (legitimate high claim)
    - Low Severity + Low Causation = Medium Risk (suspicious low claim)
    - Low Severity + High Causation = Low Risk (legitimate low claim)
    """
    severity_cat = categorize_severity(severity_score)
    causation_cat = categorize_causation(causation_score)

    # High risk scenarios
    if severity_cat == 'High' and causation_cat == 'Low':
        return 'High'  # High severity but poor compliance - suspicious

    if severity_cat == 'Medium' and causation_cat == 'Low':
        return 'High'  # Moderate severity with poor compliance

    # Low risk scenarios
    if severity_cat == 'Low' and causation_cat == 'High':
        return 'Low'   # Low severity with good compliance

    # Everything else is Medium
    return 'Medium'


if __name__ == "__main__":
    # Test with sample data
    import pandas as pd

    print("Loading weights.csv to analyze score distributions...")
    df = pd.read_csv('data/weights.csv', low_memory=False)

    # Rename quoted columns
    df.columns = [col.strip("'") for col in df.columns]

    # Calculate scores
    df['SEVERITY_SCORE'] = df.apply(calculate_severity_score, axis=1)
    df['CAUSATION_SCORE'] = df.apply(calculate_causation_score, axis=1)
    df['SEVERITY_CATEGORY'] = df['SEVERITY_SCORE'].apply(categorize_severity)
    df['CAUSATION_CATEGORY'] = df['CAUSATION_SCORE'].apply(categorize_causation)
    df['CAUTION_LEVEL'] = df.apply(lambda row: calculate_caution_level(
        row['SEVERITY_SCORE'],
        row['CAUSATION_SCORE']
    ), axis=1)

    # Print statistics
    print("\n" + "="*60)
    print("SEVERITY SCORE STATISTICS")
    print("="*60)
    print(df['SEVERITY_SCORE'].describe())
    print(f"\nDistribution:")
    print(df['SEVERITY_CATEGORY'].value_counts())

    print("\n" + "="*60)
    print("CAUSATION SCORE STATISTICS")
    print("="*60)
    print(df['CAUSATION_SCORE'].describe())
    print(f"\nDistribution:")
    print(df['CAUSATION_CATEGORY'].value_counts())

    print("\n" + "="*60)
    print("CAUTION LEVEL DISTRIBUTION")
    print("="*60)
    print(df['CAUTION_LEVEL'].value_counts())

    # Show sample rows
    print("\n" + "="*60)
    print("SAMPLE ROWS")
    print("="*60)
    sample = df[['CLAIMID', 'SEVERITY_SCORE', 'SEVERITY_CATEGORY',
                 'CAUSATION_SCORE', 'CAUSATION_CATEGORY', 'CAUTION_LEVEL']].head(10)
    print(sample.to_string(index=False))

    # Save analysis
    df[['CLAIMID', 'SEVERITY_SCORE', 'CAUSATION_SCORE', 'SEVERITY_CATEGORY',
        'CAUSATION_CATEGORY', 'CAUTION_LEVEL']].to_csv(
        'data/score_analysis.csv', index=False
    )
    print("\n[OK] Analysis saved to data/score_analysis.csv")
