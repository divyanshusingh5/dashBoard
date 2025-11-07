"""
Update weights.csv to match actual production data format
Remove old test weights that don't have corresponding columns in dat.csv
"""

import pandas as pd

# Load current files
weights = pd.read_csv('data/weights.csv')
dat = pd.read_csv('data/dat.csv')

print(f"Original weights: {len(weights)}")

# Columns to remove (old test data weights)
old_weights = [
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

# Filter out old weights
weights_updated = weights[~weights['factor_name'].isin(old_weights)]

print(f"Removed {len(old_weights)} old weights")
print(f"Updated weights: {len(weights_updated)}")

# Verify all remaining weights have matching columns in dat.csv
missing = [f for f in weights_updated['factor_name'].values if f not in dat.columns]
if missing:
    print(f"\nWARNING: {len(missing)} weights still don't match dat.csv columns:")
    for m in missing:
        print(f"  - {m}")
else:
    print("\n[SUCCESS] All weights now have matching columns in dat.csv!")

# Save updated weights
weights_updated.to_csv('data/weights.csv', index=False)

print(f"\n[SUCCESS] Updated weights.csv!")
print(f"Total clinical feature weights: {len(weights_updated)}")

# Show categories
print("\nWeights by category:")
print(weights_updated['category'].value_counts().to_dict())
