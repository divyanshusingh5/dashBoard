"""
Add new columns to existing database
Adds multi-tier injury system columns
"""

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'app' / 'db' / 'claims_analytics.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List of new columns to add
new_columns = [
    # Multi-tier injury by SEVERITY
    ("PRIMARY_INJURY_BY_SEVERITY", "TEXT"),
    ("PRIMARY_BODYPART_BY_SEVERITY", "TEXT"),
    ("PRIMARY_INJURYGROUP_CODE_BY_SEVERITY", "TEXT"),
    ("PRIMARY_INJURY_SEVERITY_SCORE", "REAL"),
    ("PRIMARY_INJURY_CAUSATION_SCORE_BY_SEVERITY", "REAL"),

    ("SECONDARY_INJURY_BY_SEVERITY", "TEXT"),
    ("SECONDARY_BODYPART_BY_SEVERITY", "TEXT"),
    ("SECONDARY_INJURYGROUP_CODE_BY_SEVERITY", "TEXT"),
    ("SECONDARY_INJURY_SEVERITY_SCORE", "REAL"),
    ("SECONDARY_INJURY_CAUSATION_SCORE_BY_SEVERITY", "REAL"),

    ("TERTIARY_INJURY_BY_SEVERITY", "TEXT"),
    ("TERTIARY_BODYPART_BY_SEVERITY", "TEXT"),
    ("TERTIARY_INJURY_SEVERITY_SCORE", "REAL"),
    ("TERTIARY_INJURY_CAUSATION_SCORE_BY_SEVERITY", "REAL"),

    # Multi-tier injury by CAUSATION
    ("PRIMARY_INJURY_BY_CAUSATION", "TEXT"),
    ("PRIMARY_BODYPART_BY_CAUSATION", "TEXT"),
    ("PRIMARY_INJURYGROUP_CODE_BY_CAUSATION", "TEXT"),
    ("PRIMARY_INJURY_CAUSATION_SCORE", "REAL"),
    ("PRIMARY_INJURY_SEVERITY_SCORE_BY_CAUSATION", "REAL"),

    ("SECONDARY_INJURY_BY_CAUSATION", "TEXT"),
    ("SECONDARY_BODYPART_BY_CAUSATION", "TEXT"),
    ("SECONDARY_INJURYGROUP_CODE_BY_CAUSATION", "TEXT"),
    ("SECONDARY_INJURY_CAUSATION_SCORE", "REAL"),
    ("SECONDARY_INJURY_SEVERITY_SCORE_BY_CAUSATION", "REAL"),

    ("TERTIARY_INJURY_BY_CAUSATION", "TEXT"),
    ("TERTIARY_BODYPART_BY_CAUSATION", "TEXT"),
    ("TERTIARY_INJURY_CAUSATION_SCORE", "REAL"),
    ("TERTIARY_INJURY_SEVERITY_SCORE_BY_CAUSATION", "REAL"),

    # Composite scores
    ("CALCULATED_SEVERITY_SCORE", "REAL"),
    ("CALCULATED_CAUSATION_SCORE", "REAL"),
    ("RN", "INTEGER"),
]

print("Adding new columns to claims table...")

for column_name, column_type in new_columns:
    try:
        cursor.execute(f"ALTER TABLE claims ADD COLUMN {column_name} {column_type}")
        print(f"[OK] Added {column_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"[-] {column_name} already exists")
        else:
            print(f"[ERROR] Error adding {column_name}: {e}")

conn.commit()

# Add indexes
print("\nAdding indexes for new columns...")

indexes = [
    ("idx_primary_severity_by_severity", "PRIMARY_INJURYGROUP_CODE_BY_SEVERITY, PRIMARY_INJURY_SEVERITY_SCORE"),
    ("idx_calculated_scores", "CALCULATED_SEVERITY_SCORE, CALCULATED_CAUSATION_SCORE"),
    ("idx_primary_causation_by_causation", "PRIMARY_INJURYGROUP_CODE_BY_CAUSATION, PRIMARY_INJURY_CAUSATION_SCORE"),
    ("idx_model_performance", "PRIMARY_INJURYGROUP_CODE_BY_SEVERITY, variance_pct, CALCULATED_SEVERITY_SCORE"),
]

for idx_name, idx_cols in indexes:
    try:
        cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON claims ({idx_cols})")
        print(f"[OK] Created index {idx_name}")
    except Exception as e:
        print(f"[ERROR] Error creating index {idx_name}: {e}")

conn.commit()
conn.close()

print("\n[SUCCESS] Database schema updated successfully!")
