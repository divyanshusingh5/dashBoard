"""
Quick diagnostic script to check CSV vs Database schema mismatch
"""
import pandas as pd
from app.db.schema import Claim
from sqlalchemy import inspect

print("=" * 70)
print("CSV vs DATABASE SCHEMA DIAGNOSTIC")
print("=" * 70)

# Load CSV header
print("\n1. Loading dat.csv header...")
df = pd.read_csv('data/dat.csv', nrows=1)
csv_columns = set(df.columns.tolist())
print(f"CSV has {len(csv_columns)} columns")

# Get database model columns
print("\n2. Loading SQLAlchemy Claim model columns...")
db_columns = set()
for column in Claim.__table__.columns:
    if column.name != 'id':  # Skip auto-increment ID
        db_columns.add(column.name)
print(f"Database model has {len(db_columns)} columns (excluding auto-increment id)")

# Find mismatches
print("\n" + "=" * 70)
print("COLUMN COMPARISON")
print("=" * 70)

# Columns in CSV but NOT in database
missing_in_db = csv_columns - db_columns
if missing_in_db:
    print(f"\n⚠️  COLUMNS IN CSV BUT NOT IN DATABASE ({len(missing_in_db)}):")
    for col in sorted(missing_in_db):
        print(f"   - {col}")
else:
    print("\n✓ All CSV columns exist in database")

# Columns in database but NOT in CSV
missing_in_csv = db_columns - csv_columns
if missing_in_csv:
    print(f"\n⚠️  COLUMNS IN DATABASE BUT NOT IN CSV ({len(missing_in_csv)}):")
    for col in sorted(missing_in_csv):
        print(f"   - {col}")
        # Show if it's a calculated field
        if col in ['variance_pct', 'SEVERITY_SCORE', 'CAUTION_LEVEL']:
            print(f"      (This is calculated - OK)")
else:
    print("\n✓ All database columns exist in CSV (or are calculated)")

# Show matching columns
matching = csv_columns & db_columns
print(f"\n✓ MATCHING COLUMNS: {len(matching)}")

print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)

if missing_in_db:
    print("\n1. Your CSV has columns that the database doesn't expect.")
    print("   Either:")
    print("   a) Add these columns to app/db/schema.py (Claim model)")
    print("   b) Or remove these columns from CSV before migration")

if missing_in_csv - {'variance_pct', 'SEVERITY_SCORE', 'CAUTION_LEVEL'}:
    print("\n2. Your database expects columns that aren't in CSV.")
    print("   Either:")
    print("   a) Add these columns to your CSV")
    print("   b) Or remove these columns from app/db/schema.py")
    print("   c) Or make them nullable in the database model")

if not missing_in_db and not (missing_in_csv - {'variance_pct', 'SEVERITY_SCORE', 'CAUTION_LEVEL'}):
    print("\n✓ CSV and Database schemas match!")
    print("  You can run: python migrate_actual_data.py")

print("\n" + "=" * 70)
