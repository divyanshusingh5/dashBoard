import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Number of records
n = 100000

# Generate data
data = {}

# Basic identifiers
data['CLAIMID'] = np.random.randint(14132, 9480322, n)
data['EXPSR_NBR'] = [f"{random.randint(10,99)}-{random.randint(100,9999):04X}-{random.choice('ABCDEFGHKLMNPQRSTUVWXYZ')}{random.randint(10,99)}-0/{random.randint(1,4):02d}" for _ in range(n)]

# Dates
start_date = datetime(2022, 1, 1)
end_date = datetime(2025, 3, 31)
incident_start = datetime(2016, 1, 1)
incident_end = datetime(2018, 12, 31)

data['CLAIMCLOSEDDATE'] = [(start_date + timedelta(days=random.randint(0, (end_date - start_date).days))).strftime('%Y-%m-%d %H:%M:%S.000') for _ in range(n)]
data['INCIDENTDATE'] = [(incident_start + timedelta(days=random.randint(0, (incident_end - incident_start).days))).strftime('%Y-%m-%d %H:%M:%S.000') for _ in range(n)]

# Numeric fields
data['CAUSATION_HIGH_RECOMMENDATION'] = np.round(np.random.uniform(50, 150000, n), 0)
data['SETTLEMENTAMOUNT'] = [0] * n
data['VERSIONID'] = np.random.randint(2, 30, n)
data['DURATIONTOREPORT'] = np.random.randint(0, 1200, n)
data['ADJUSTERNAME'] = ['System System'] * n
data['HASATTORNEY'] = np.random.choice([0, 1], n, p=[0.3, 0.7])
data['GENERALS'] = np.round(np.random.uniform(0.5, 150000, n), 2)
data['DOLLARAMOUNTHIGH'] = np.round(np.random.uniform(1, 200000, n), 2)
data['AGE'] = np.random.randint(18, 85, n)
data['GENDER'] = np.random.choice([-1, 1, 2], n, p=[0.02, 0.49, 0.49])
data['OCCUPATION_AVAILABLE'] = [0] * n
data['OCCUPATION'] = [np.nan] * n

# Calculated scores
data['CALCULATED_SEVERITY_SCORE'] = np.round(np.random.uniform(0, 5000, n), 4)
data['CALCULATED_CAUSATION_SCORE'] = np.round(np.random.uniform(0, 500, n), 4)

# Injury classifications
injury_types = ['Sprain/Strain', 'Minor Closed Head Injury/Mild Concussion', 'Non-Surgical Disc Injury - Herniation/Tear', 
                'Non-Surgical Disc Injury - Bulge', 'Tear', 'Abrasion/Contusion', 'Shaft Fracture', 
                'Closed Head Injury', 'Laceration/Puncture Wound', 'Joint Fracture']

body_parts = ['Neck/Back', 'Shoulder', 'Lumbar/Sacral', 'Cervical', 'Knee', 'Lower Extremity', 
              'Elbow', 'Upper Extremity', 'Head', 'Does not apply', 'Hip', 'Wrist', 'Chest']

injury_codes = ['SSNB', 'SSUE', 'MCHI', 'DINB', 'BULG', 'TRLE', 'WND', 'TRUE', 'SSLE', 'SFLE']

data['PRIMARY_INJURY_BY_SEVERITY'] = np.random.choice(injury_types, n, p=[0.65, 0.08, 0.09, 0.06, 0.03, 0.04, 0.02, 0.01, 0.01, 0.01])
data['PRIMARY_BODYPART_BY_SEVERITY'] = np.random.choice(body_parts, n)
data['PRIMARY_INJURYGROUP_CODE_BY_SEVERITY'] = np.random.choice(injury_codes, n)
data['PRIMARY_INJURY_SEVERITY_SCORE'] = np.round(np.random.uniform(0, 2000, n), 4)
data['PRIMARY_INJURY_CAUSATION_SCORE_BY_SEVERITY'] = np.round(np.random.uniform(0, 150, n), 4)

# Secondary injuries (with nulls)
secondary_mask = np.random.choice([True, False], n, p=[0.69, 0.31])
data['SECONDARY_INJURY_BY_SEVERITY'] = [np.random.choice(injury_types) if m else np.nan for m in secondary_mask]
data['SECONDARY_BODYPART_BY_SEVERITY'] = [np.random.choice(body_parts) if m else np.nan for m in secondary_mask]
data['SECONDARY_INJURYGROUP_CODE_BY_SEVERITY'] = [np.random.choice(injury_codes) if m else np.nan for m in secondary_mask]
data['SECONDARY_INJURY_SEVERITY_SCORE'] = [np.round(np.random.uniform(0, 1500), 4) if m else np.nan for m in secondary_mask]
data['SECONDARY_INJURY_CAUSATION_SCORE_BY_SEVERITY'] = [np.round(np.random.uniform(0, 120), 4) if m else np.nan for m in secondary_mask]

# Tertiary injuries (with more nulls)
tertiary_mask = np.random.choice([True, False], n, p=[0.40, 0.60])
data['TERTIARY_INJURY_BY_SEVERITY'] = [np.random.choice(injury_types) if m else np.nan for m in tertiary_mask]
data['TERTIARY_BODYPART_BY_SEVERITY'] = [np.random.choice(body_parts) if m else np.nan for m in tertiary_mask]
data['TERTIARY_INJURY_SEVERITY_SCORE'] = [np.round(np.random.uniform(0, 1500), 4) if m else np.nan for m in tertiary_mask]
data['TERTIARY_INJURY_CAUSATION_SCORE_BY_SEVERITY'] = [np.round(np.random.uniform(0, 150), 4) if m else np.nan for m in tertiary_mask]

# Causation fields (similar structure)
data['PRIMARY_INJURY_BY_CAUSATION'] = np.random.choice(injury_types, n, p=[0.65, 0.08, 0.06, 0.05, 0.04, 0.05, 0.03, 0.02, 0.01, 0.01])
data['PRIMARY_BODYPART_BY_CAUSATION'] = np.random.choice(body_parts, n)
data['PRIMARY_INJURYGROUP_CODE_BY_CAUSATION'] = np.random.choice(injury_codes, n)
data['PRIMARY_INJURY_CAUSATION_SCORE'] = np.round(np.random.uniform(0, 150, n), 4)
data['PRIMARY_INJURY_SEVERITY_SCORE_BY_CAUSATION'] = np.round(np.random.uniform(0, 2000, n), 4)

data['SECONDARY_INJURY_BY_CAUSATION'] = [np.random.choice(injury_types) if m else np.nan for m in secondary_mask]
data['SECONDARY_BODYPART_BY_CAUSATION'] = [np.random.choice(body_parts) if m else np.nan for m in secondary_mask]
data['SECONDARY_INJURYGROUP_CODE_BY_CAUSATION'] = [np.random.choice(injury_codes) if m else np.nan for m in secondary_mask]
data['SECONDARY_INJURY_CAUSATION_SCORE'] = [np.round(np.random.uniform(0, 150), 4) if m else np.nan for m in secondary_mask]
data['SECONDARY_INJURY_SEVERITY_SCORE_BY_CAUSATION'] = [np.round(np.random.uniform(0, 1500), 4) if m else np.nan for m in secondary_mask]

data['TERTIARY_INJURY_BY_CAUSATION'] = [np.random.choice(injury_types) if m else np.nan for m in tertiary_mask]
data['TERTIARY_BODYPART_BY_CAUSATION'] = [np.random.choice(body_parts) if m else np.nan for m in tertiary_mask]
data['TERTIARY_INJURY_CAUSATION_SCORE'] = [np.round(np.random.uniform(0, 120), 4) if m else np.nan for m in tertiary_mask]
data['TERTIARY_INJURY_SEVERITY_SCORE_BY_CAUSATION'] = [np.round(np.random.uniform(0, 1500), 4) if m else np.nan for m in tertiary_mask]

# Aggregated fields
data['ALL_BODYPARTS'] = [np.random.choice(body_parts) + (' | ' + np.random.choice(body_parts) if random.random() > 0.5 else '') for _ in range(n)]
data['ALL_INJURIES'] = [np.random.choice(injury_types) + (' | ' + np.random.choice(injury_types) if random.random() > 0.6 else '') for _ in range(n)]
data['ALL_INJURYGROUP_CODES'] = [np.random.choice(injury_codes) + (' | ' + np.random.choice(injury_codes) if random.random() > 0.5 else '') for _ in range(n)]
data['ALL_INJURYGROUP_TEXTS'] = ['Sprain/Strain, Neck/Back' if random.random() > 0.3 else 'Non-Surgical Disc Injury - Herniation/Tear' for _ in range(n)]

data['INJURY_COUNT'] = np.random.randint(1, 10, n)
data['BODYPART_COUNT'] = np.random.randint(1, 8, n)
data['INJURYGROUP_COUNT'] = np.random.randint(1, 6, n)
data['BODY_REGION'] = np.random.choice(['Spine', 'Upper Extremity', 'Lower Extremity', 'Head/Face', 'Torso', 'Other'], n, p=[0.56, 0.15, 0.10, 0.09, 0.05, 0.05])

# Settlement information
data['SETTLEMENT_DAYS'] = np.random.randint(0, 3000, n)
data['SETTLEMENT_MONTHS'] = (data['SETTLEMENT_DAYS'] / 30).astype(int)
data['SETTLEMENT_YEARS'] = np.round(data['SETTLEMENT_DAYS'] / 365, 1)
data['SETTLEMENT_SPEED_CATEGORY'] = pd.cut(data['SETTLEMENT_MONTHS'], 
                                            bins=[0, 3, 6, 12, 18, 24, 36, 60, 300],
                                            labels=['Within 3 months', 'Within 6 months', 'Within 1 year', 
                                                   'Within 1.5 years', 'Within 2 years', 'Within 3 years',
                                                   'Within 5 years', 'More than 5 years'])

data['SETTLEMENT_VARIANCE'] = np.round(np.random.uniform(0, 50000, n), 2)
data['VARIANCE_PERCENTAGE'] = np.round(np.random.uniform(-99, 500, n), 2)
data['PREDICTION_DIRECTION'] = np.random.choice(['Perfect Match', 'Model Under-Predicted', 'Model Over-Predicted'], 
                                                 n, p=[0.90, 0.08, 0.02])

# Location data
data['IOL'] = np.random.randint(1, 5, n)
counties = ['Harris', 'Miami-Dade', 'Los Angeles', 'Cook', 'Maricopa', 'Orange', 'San Diego', 'Kings', 'Dallas']
states = ['TX', 'FL', 'CA', 'IL', 'AZ', 'NY', 'GA', 'OH', 'PA', 'NC']
data['COUNTYNAME'] = [np.random.choice(counties) if random.random() > 0.0001 else np.nan for _ in range(n)]
data['VENUESTATE'] = np.random.choice(states, n)
data['VENUERATINGTEXT'] = [np.random.choice(['Conservative', 'Moderate', 'Liberal', 'Very Liberal']) if random.random() > 0.0001 else np.nan for _ in range(n)]
data['VENUERATINGPOINT'] = [float(np.random.choice([1, 2, 3, 4])) if random.random() > 0.0001 else np.nan for _ in range(n)]
data['RATINGWEIGHT'] = [float(np.random.choice([80, 95, 100, 133, 147, 180, 200, 250])) if random.random() > 0.0001 else np.nan for _ in range(n)]
data['VENUERATING'] = np.random.choice(['Conservative', 'Moderate', 'Liberal', 'Very Liberal'], n, p=[0.22, 0.54, 0.23, 0.01])

# Vulnerable claimant (mostly null)
data['VULNERABLECLAIMANT'] = [False if random.random() < 0.34 else np.nan for _ in range(n)]

# Medical treatment fields (many with nulls)
data['Advanced_Pain_Treatment'] = [np.random.choice(['No', 'Yes']) if random.random() < 0.03 else np.nan for _ in range(n)]
data['Causation_Compliance'] = [np.random.choice(['Compliant', 'Non-Compliant'], p=[0.96, 0.04]) if random.random() < 0.98 else np.nan for _ in range(n)]
data['Clinical_Findings'] = [np.random.choice(['Yes', 'No', 'Mild', 'Moderate']) if random.random() < 0.75 else np.nan for _ in range(n)]
data['Cognitive_Symptoms'] = [np.random.choice(['Yes - Alleged', 'Yes - Diagnosed']) if random.random() < 0.024 else np.nan for _ in range(n)]
data['Complete_Disability_Duration'] = [np.random.choice(['Less than 1 week', '1 -3 weeks', '2-4 Weeks', 'More than 8 Weeks']) if random.random() < 0.022 else np.nan for _ in range(n)]
data['Concussion_Diagnosis'] = [np.random.choice(['Yes', 'No']) if random.random() < 0.0007 else np.nan for _ in range(n)]
data['Consciousness_Impact'] = [np.random.choice(['Temp Unconsciousness-Subjective', 'Altered', 'Temp Unconsciousness-Objective']) if random.random() < 0.012 else np.nan for _ in range(n)]
data['Consistent_Mechanism'] = [np.random.choice(['Consistent', 'Questionable', 'Highly Unlikely'], p=[0.85, 0.12, 0.03]) if random.random() < 0.9999 else np.nan for _ in range(n)]
data['Dental_Procedure'] = [np.random.choice(['No', 'Yes']) if random.random() < 0.0018 else np.nan for _ in range(n)]
data['Dental_Treatment'] = [np.random.choice(['Repair', 'Replace']) if random.random() < 0.0013 else np.nan for _ in range(n)]
data['Dental_Visibility'] = [np.random.choice(['Yes', 'No']) if random.random() < 0.0018 else np.nan for _ in range(n)]
data['Emergency_Treatment'] = [np.random.choice(['Yes - Treated & Released', 'Yes - Treated & Admitted']) if random.random() < 0.05 else np.nan for _ in range(n)]
data['Fixation_Method'] = [np.random.choice(['Cast w/o Reduction', 'ORIF w/o Hdw Removal', 'Sling/Brace', 'Immobilization']) if random.random() < 0.026 else np.nan for _ in range(n)]
data['Head_Trauma'] = [np.random.choice(['No', 'Yes'], p=[0.68, 0.32]) if random.random() < 0.072 else np.nan for _ in range(n)]
data['Immobilization_Used'] = [np.random.choice(['No', 'Yes', 'Brace/Sling', 'Cast'], p=[0.88, 0.09, 0.025, 0.005]) if random.random() < 0.195 else np.nan for _ in range(n)]
data['Injury_Count'] = [np.random.choice(['Single Level', 'Multi Level', 'Single', 'Multiple']) if random.random() < 0.133 else np.nan for _ in range(n)]
data['Injury_Extent'] = [np.random.choice(['Mild', 'Moderate', 'Severe'], p=[0.51, 0.38, 0.11]) if random.random() < 0.12 else np.nan for _ in range(n)]
data['Injury_Laterality'] = [np.random.choice(['Yes', 'No', 'Unilateral'], p=[0.52, 0.43, 0.05]) if random.random() < 0.172 else np.nan for _ in range(n)]
data['Injury_Location'] = [np.random.choice(['Cervical/Thoracic/Lumbar', 'Cervical/Lumbar', 'Cervical', 'Lumbar'], p=[0.50, 0.12, 0.11, 0.27]) if random.random() < 0.47 else np.nan for _ in range(n)]
data['Injury_Type'] = [np.random.choice(['Bruise Only', 'Herniation', 'Bruise w/Abrasion', 'Annular Tear', 'Abrasion Only']) if random.random() < 0.246 else np.nan for _ in range(n)]
data['Mobility_Assistance'] = [np.random.choice(['Crutches/Cane/Walker', 'Scooter/Wheelchair', 'Wheelchair']) if random.random() < 0.0068 else np.nan for _ in range(n)]
data['Movement_Restriction'] = [np.random.choice(['Partial Restriction', 'No Restriction', 'Full Restriction'], p=[0.58, 0.38, 0.04]) if random.random() < 0.72 else np.nan for _ in range(n)]
data['Nerve_Involvement'] = [np.random.choice(['Yes', 'No'], p=[0.65, 0.35]) if random.random() < 0.162 else np.nan for _ in range(n)]
data['Pain_Management'] = [np.random.choice(['RX', 'OTC', 'Single Injection', 'Multiple Injections']) if random.random() < 0.72 else np.nan for _ in range(n)]
data['Partial_Disability_Duration'] = [np.random.choice(['Less than 1 Week', '1 - 3 weeks', '2-4 Weeks', 'More than 8 Weeks']) if random.random() < 0.027 else np.nan for _ in range(n)]
data['Physical_Symptoms'] = [np.random.choice(['No', 'Yes', 'Yes - Alleged', 'Yes - Treated']) if random.random() < 0.167 else np.nan for _ in range(n)]
data['Physical_Therapy'] = [np.random.choice(['Yes - Outpatient', 'Yes', 'No', 'Yes - Inpatient']) if random.random() < 0.036 else np.nan for _ in range(n)]
data['Prior_Treatment'] = [np.random.choice(['No', 'No/Non-Factor', 'Yes - Tx More than 1 Yr', 'Yes - No Tx'], p=[0.65, 0.17, 0.07, 0.11]) if random.random() < 0.814 else np.nan for _ in range(n)]
data['Recovery_Duration'] = [np.random.choice(['Less than 2 weeks', '2 - 4 weeks', '5 - 12 weeks', 'More than 4 weeks']) if random.random() < 0.103 else np.nan for _ in range(n)]
data['Repair_Type'] = [np.random.choice(['Implant', 'Bridge', 'Crown']) if random.random() < 0.00075 else np.nan for _ in range(n)]
data['Respiratory_Issues'] = [np.random.choice(['No', 'Yes'], p=[0.72, 0.28]) if random.random() < 0.008 else np.nan for _ in range(n)]
data['Soft_Tissue_Damage'] = [np.random.choice(['Partial Tear w/o Cart Damage', 'Full Tear w/o Cart Damage', 'Partial Tear w/ Cart Damage']) if random.random() < 0.032 else np.nan for _ in range(n)]
data['Special_Treatment'] = [np.random.choice(['No', 'Series', 'Single', 'Yes']) if random.random() < 0.0026 else np.nan for _ in range(n)]
data['Surgical_Intervention'] = [np.random.choice(['No', 'Yes - Arthroscopic', 'Recommended Not Performed', 'Yes', 'Fusion']) if random.random() < 0.044 else np.nan for _ in range(n)]
data['Symptom_Timeline'] = [np.random.choice(['Immediate/ER', 'First 48 Hours', '3 - 7 Days', 'More Than 7 Days']) if random.random() < 0.707 else np.nan for _ in range(n)]
data['Treatment_Course'] = [np.random.choice(['Active', 'Passive', 'Eval Only', 'None/Ice/Rest'], p=[0.45, 0.37, 0.12, 0.06]) if random.random() < 0.795 else np.nan for _ in range(n)]
data['Treatment_Delays'] = [np.random.choice(['None/Explained', 'Delay Only', 'Gaps Only', 'Delay and Gaps'], p=[0.75, 0.13, 0.07, 0.05]) if random.random() < 0.9999 else np.nan for _ in range(n)]
data['Treatment_Level'] = [np.random.choice(['Yes', 'Non-Invasive', 'No', 'Clean & Dress']) if random.random() < 0.188 else np.nan for _ in range(n)]
data['Treatment_Period_Considered'] = [np.random.choice(['7 - 12 weeks', '3 - 6 months', 'More than 6 months', 'Less than 6 weeks']) if random.random() < 0.821 else np.nan for _ in range(n)]
data['Vehicle_Impact'] = [np.random.choice(['Moderate', 'Minimal', 'Heavy'], p=[0.46, 0.29, 0.25]) if random.random() < 0.813 else np.nan for _ in range(n)]

data['RN'] = [1] * n

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('dat.csv', index=False)
print(f"Generated {n} records and saved to dat.csv")
print(f"DataFrame shape: {df.shape}")
print("\nFirst few rows:")
print(df.head())