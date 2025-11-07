import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Number of records
n = 100

# Generate data for SSNB.csv
data = {}

# Basic identifiers
data['CLAIMID'] = np.random.randint(14132, 9480322, n)
data['VERSIONID'] = np.random.randint(2, 30, n)
data['EXPSR_NBR'] = [f"{random.randint(10,99)}-{random.randint(100,9999):02X}{random.choice('ABCDEFGHKLMNPQRSTUVWXYZ')}{random.randint(0,9)}-{random.randint(10,99)}{random.choice('ABCDEFGHKLMNPQRSTUVWXYZ')}-0/{random.randint(1,4):02d}" for _ in range(n)]

# Numeric fields with proper null handling
causation_high = np.round(np.random.uniform(100, 500000, n), 0)
# Add 2 nulls
null_indices = random.sample(range(n), 2)
data['CAUSATION_HIGH_RECOMMENDATION'] = [np.nan if i in null_indices else causation_high[i] for i in range(n)]

data['DOLLARAMOUNTHIGH'] = np.round(np.random.uniform(1, 16001150, n), 2)

# Venue information
venue_ratings = ['Conservative', 'Liberal', 'Moderate', 'Very Liberal']
data['VENUERATING'] = np.random.choice(venue_ratings, n, p=[0.22, 0.24, 0.54, 0.006])

# Rating weight with 22 nulls (approximately)
rating_weights = [80.0, 81.0, 83.0, 85.0, 95.0, 100.0, 115.0, 131.0, 132.0, 133.0, 134.0, 
                  147.0, 154.0, 179.0, 180.0, 181.0, 184.0, 200.0, 250.0, 255.0, 364.0]
null_indices_rw = random.sample(range(n), min(22, n))
data['RATINGWEIGHT'] = [np.nan if i in null_indices_rw else float(random.choice(rating_weights)) for i in range(n)]

# Venue rating text
venue_text_options = ['Conservative', 'LA - Liberal', 'Moderate', 'GA - Moderate', 'Liberal', 
                      'FL - Moderate', 'LA - Moderate', 'TX - Moderate', 'CA - Liberal', 'TX - Liberal',
                      'LA - Conservative', 'FL - Liberal', 'TX - Conservative', 'CA - Moderate',
                      'NY - Liberal', 'FL - Conservative', 'Very Liberal']
data['VENUERATINGTEXT'] = [np.nan if i in null_indices_rw else random.choice(venue_text_options) for i in range(n)]

# Venue rating point
data['VENUERATINGPOINT'] = [np.nan if i in null_indices_rw else float(random.choice([1.0, 2.0, 3.0, 4.0])) for i in range(n)]

# Dates
incident_start = datetime(2022, 1, 1)
incident_end = datetime(2025, 7, 31)
closed_start = datetime(2023, 1, 1)
closed_end = datetime(2025, 11, 4)

data['INCIDENTDATE'] = [(incident_start + timedelta(days=random.randint(0, (incident_end - incident_start).days))).strftime('%Y-%m-%d %H:%M:%S.000') for _ in range(n)]
data['CLAIMCLOSEDDATE'] = [(closed_start + timedelta(days=random.randint(0, (closed_end - closed_start).days))).strftime('%Y-%m-%d %H:%M:%S.000') for _ in range(n)]

# Demographics
data['AGE'] = np.random.randint(-61, 143, n)  # Including outliers as in original
data['GENDER'] = np.random.choice([-1, 1, 2], n, p=[0.01, 0.49, 0.50])
data['HASATTORNEY'] = np.random.choice([0, 1], n, p=[0.3, 0.7])
data['IOL'] = np.random.randint(1, 5, n)
data['ADJUSTERNAME'] = ['System System'] * n
data['OCCUPATION'] = [np.nan] * n

# Location
counties = ['Maricopa', 'Orleans', 'Mecklenburg', 'Marion', 'Fayette', 'Fulton', 'Cook', 
            'Saint Lucie', 'Suffolk', 'Charles', 'Harris', 'Miami-Dade', 'Los Angeles', 
            'Orange', 'San Diego', 'Dallas', 'Travis', 'Bexar']
states = ['AZ', 'LA', 'NC', 'OR', 'GA', 'IL', 'FL', 'NY', 'MD', 'PA', 'TX', 'CA', 'OH', 
          'WA', 'MI', 'VA', 'TN', 'MA', 'NJ', 'IN']

data['COUNTYNAME'] = [np.nan if i in null_indices_rw else random.choice(counties) for i in range(n)]
data['VENUESTATE'] = np.random.choice(states, n)

# Vulnerable claimant (mostly null, about 33% populated)
vulnerable_mask = random.sample(range(n), int(n * 0.33))
data['VULNERABLECLAIMANT'] = [False if i in vulnerable_mask else np.nan for i in range(n)]

# Primary injury fields (all same value as per your data)
data['PRIMARY_INJURY'] = ['Sprain/Strain'] * n
data['PRIMARY_BODYPART'] = ['Neck/Back'] * n
data['PRIMARY_INJURY_GROUP'] = ['Sprain/Strain, Neck/Back'] * n

# Severity and causation scores
data['PRIMARY_SEVERITY_SCORE'] = np.round(np.random.uniform(0, 2184164.352, n), 4)
data['PRIMARY_CAUSATION_SCORE'] = np.round(np.random.uniform(0, 144173.2608, n), 4)

# Medical treatment fields - all float64 with specific values and nulls
# Causation_Compliance - 4 unique values, 6 nulls
causation_values = [0.142, 0.1621, 0.1897, 0.0]
null_cc = random.sample(range(n), min(6, n))
data['Causation_Compliance'] = [np.nan if i in null_cc else random.choice(causation_values) for i in range(n)]

# Clinical_Findings - 4 unique values, 17 nulls
clinical_values = [3.9848, 3.0568, 0.0, 3.0193]
null_cf = random.sample(range(n), min(17, n))
data['Clinical_Findings'] = [np.nan if i in null_cf else random.choice(clinical_values) for i in range(n)]

# Consistent_Mechanism - 7 unique values, 10 nulls
mechanism_values = [0.4208, 0.1918, 0.183, 0.344, 0.3944, 0.0, 0.139]
null_cm = random.sample(range(n), min(10, n))
data['Consistent_Mechanism'] = [np.nan if i in null_cm else random.choice(mechanism_values) for i in range(n)]

# Injury_Location - 19 unique values, 17 nulls
location_values = [1.779, 1.3444, 0.7177, 1.1252, 0.7536, 1.2265, 0.7054, 0.41, 0.535, 1.5677,
                   2.6152, 1.4932, 0.0, 0.9192, 1.6251, 1.8195, 0.8721, 1.9665, 1.6727]
data['Injury_Location'] = [np.nan if i in null_cf else random.choice(location_values) for i in range(n)]

# Movement_Restriction - 7 unique values, 17 nulls
restriction_values = [2.2136, 1.5948, 0.0, 1.3441, 4.4168, 2.8133, 3.1848]
data['Movement_Restriction'] = [np.nan if i in null_cf else random.choice(restriction_values) for i in range(n)]

# Pain_Management - 16 unique values, 19 nulls
pain_values = [0.7496, 0.0, 4.344, 3.5106, 0.1301, 1.1558, 0.9452, 3.3411, 0.9964, 2.4714,
               1.96, 0.5848, 2.9949, 2.911, 4.3793, 0.3285]
null_pm = random.sample(range(n), min(19, n))
data['Pain_Management'] = [np.nan if i in null_pm else random.choice(pain_values) for i in range(n)]

# Prior_Treatment - 14 unique values, 17 nulls
prior_values = [0.0868, 0.0908, 0.1195, 0.1174, 0.2115, 0.0936, 0.0379, 0.0344, 0.1041, 0.0,
                0.1394, 0.1056, 0.1183, 0.0627]
data['Prior_Treatment'] = [np.nan if i in null_cf else random.choice(prior_values) for i in range(n)]

# Symptom_Timeline - 10 unique values, 18 nulls
symptom_values = [1.8125, 1.2233, 0.9662, 0.0, 2.4348, 2.5804, 1.7318, 0.4084, 2.8525, 0.7596]
null_st = random.sample(range(n), min(18, n))
data['Symptom_Timeline'] = [np.nan if i in null_st else random.choice(symptom_values) for i in range(n)]

# Treatment_Course - 10 unique values, 15 nulls
course_values = [1.7718, 0.9557, 0.0, 0.5559, 2.626, 0.3285, 1.9854, 1.9797, 3.0058, 0.1792]
null_tc = random.sample(range(n), min(15, n))
data['Treatment_Course'] = [np.nan if i in null_tc else random.choice(course_values) for i in range(n)]

# Treatment_Delays - 10 unique values, 12 nulls
delay_values = [0.1716, 0.0345, 0.1328, 0.0627, 0.1367, 0.0749, 0.0878, 0.0, 0.0432, 0.0823]
null_td = random.sample(range(n), min(12, n))
data['Treatment_Delays'] = [np.nan if i in null_td else random.choice(delay_values) for i in range(n)]

# Treatment_Period_Considered - 10 unique values, 18 nulls
period_values = [1.6727, 0.6218, 1.8195, 0.8721, 1.9665, 1.7771, 1.4964, 0.9192, 0.0, 1.6251]
data['Treatment_Period_Considered'] = [np.nan if i in null_st else random.choice(period_values) for i in range(n)]

# Vehicle_Impact - all 0.0, about 85% populated
null_vi = random.sample(range(n), int(n * 0.155))
data['Vehicle_Impact'] = [np.nan if i in null_vi else 0.0 for i in range(n)]

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('SSNB.csv', index=False)
print(f"Generated {n} records and saved to SSNB.csv")
print(f"DataFrame shape: {df.shape}")
print(f"\nColumn dtypes:")
print(df.dtypes)
print("\nFirst few rows:")
print(df.head())
print("\nNull counts:")
print(df.isnull().sum())