# Smart Migration Script - Usage Guide

## Overview

The **migrate_smart.py** script is an intelligent migration tool that:
- ✅ Checks if data already exists before migrating
- ✅ Only migrates what's missing (no wasted time re-migrating)
- ✅ Handles duplicates properly
- ✅ Gives you control over what to migrate

## Key Features

### 1. Smart Existence Checks
The script checks what's already in the database before doing anything:
- If `claims` table has 630K records → Skips dat.csv migration
- If `ssnb` table has 100 records → Asks if you want to skip/replace

### 2. No Duplicate Errors
- Automatically deduplicates the CSV before migrating
- Uses `CLAIMID` as unique identifier
- Keeps the last occurrence if duplicates exist

### 3. Fast & Efficient
- Uses pandas `to_sql()` for bulk loading
- Processes in chunks of 1000 records
- Much faster than row-by-row inserts

## How to Use

### Basic Usage

```bash
cd backend
./venv/Scripts/python.exe migrate_smart.py
```

### What Happens

**Step 1: Check Claims Data**
```
================================================================================
CHECKING CLAIMS DATA
================================================================================
✓ Claims table already has 630,000 records
✓ Skipping dat.csv migration (already done)
```
- If claims exist → Automatically skips
- If claims don't exist → Migrates from dat.csv

**Step 2: Check SSNB Data**
```
================================================================================
CHECKING SSNB DATA
================================================================================
ssnb table doesn't exist, creating it...
ssnb table created successfully
Reading SSNB.csv...
Loaded 100 records from SSNB.csv
Migrating to database...

✓ SSNB migration complete:
  - Total records in table: 100
```

**If SSNB table already has data, you'll see:**
```
✓ SSNB table already has 100 records

Do you want to:
  1. Skip SSNB migration (keep existing data)
  2. Replace all SSNB data (clear and re-migrate)
Choice (1/2):
```

**Step 3: Verification**
```
================================================================================
MIGRATION VERIFICATION
================================================================================
Claims table: 630,000 records
SSNB table: 100 records
Matched claims (have SSNB data): 100 (0.0%)

Sample SSNB data:
  CLAIMID: 6437520
    Actual Settlement: $1,205,627.67
    Predicted: $172,601.00
    Injury: Sprain/Strain - Neck/Back
    Severity: 2,099,136.00, Causation: 119,626.58
...

================================================================================
MIGRATION SUMMARY
================================================================================
✓ Claims data: 630,000 records
✓ SSNB data: 100 records
✓ Match rate: 0.0%
✓ Ready for use!
================================================================================
```

## Scenarios

### Scenario 1: Fresh Database (Nothing Migrated Yet)
```bash
./venv/Scripts/python.exe migrate_smart.py
```
**Result:**
- Migrates dat.csv → claims table (630K records, takes ~2 minutes)
- Creates ssnb table
- Migrates SSNB.csv → ssnb table (100 records, takes <1 second)

### Scenario 2: Claims Already Migrated, SSNB Missing
```bash
./venv/Scripts/python.exe migrate_smart.py
```
**Result:**
- Skips dat.csv (already done)
- Creates ssnb table
- Migrates SSNB.csv → ssnb table (100 records, takes <1 second)

**Total time: ~1 second** (vs. 2+ minutes if it re-migrated claims!)

### Scenario 3: Both Already Migrated
```bash
./venv/Scripts/python.exe migrate_smart.py
```
**Result:**
- Skips dat.csv
- Asks what to do with SSNB data
- If you choose option 1 (skip) → Done in <1 second!

### Scenario 4: Re-migrate SSNB Only
If you have new SSNB data and want to replace it:
```bash
./venv/Scripts/python.exe migrate_smart.py
```
When prompted:
```
Do you want to:
  1. Skip SSNB migration (keep existing data)
  2. Replace all SSNB data (clear and re-migrate)
Choice (1/2): 2
```
**Result:**
- Skips dat.csv
- Clears existing SSNB data
- Migrates new SSNB.csv
- Total time: <1 second

## File Requirements

### Required Files:
1. **dat.csv** - Must be in `backend/` directory
   - Contains all 630K claims records
   - Used to populate `claims` table

2. **SSNB.csv** - Must be in `backend/` directory
   - Contains SSNB (Single Soft tissue Neck/Back) claims
   - Currently has 100 records
   - Used to populate `ssnb` table

### Database:
- `backend/app/db/claims_analytics.db` (SQLite database)

## Table Structures

### claims table
- All claim data from dat.csv
- 630,000 records
- Includes: CLAIMID, DOLLARAMOUNTHIGH, demographics, venue info, etc.

### ssnb table
- SSNB-specific claim data
- Fields:
  - Basic: CLAIMID, VERSIONID, EXPSR_NBR
  - Financial: CAUSATION_HIGH_RECOMMENDATION, DOLLARAMOUNTHIGH
  - Venue: VENUERATING, RATINGWEIGHT, VENUERATINGTEXT, VENUERATINGPOINT
  - Demographics: AGE, GENDER, HASATTORNEY, IOL, etc.
  - Fixed injury: PRIMARY_INJURY, PRIMARY_BODYPART (always Sprain/Strain, Neck/Back)
  - Scores: PRIMARY_SEVERITY_SCORE, PRIMARY_CAUSATION_SCORE
  - Clinical factors: Causation_Compliance, Clinical_Findings, Consistent_Mechanism, etc. (12 float factors)

## Error Handling

### Duplicate CLAIMID in CSV
```
⚠ Found 5 duplicate CLAIMID entries in CSV
Keeping only the last occurrence of each duplicate CLAIMID...
After deduplication: 95 records
```
**Action:** Automatically handled - keeps last occurrence

### Missing CSV File
```
Error: SSNB.csv not found!
```
**Action:** Script stops, migration fails
**Fix:** Ensure CSV files are in backend/ directory

### Database Connection Error
```
Error migrating SSNB data: unable to open database file
```
**Action:** Script stops
**Fix:** Check database file permissions and path

## Comparison: Old vs New Script

| Feature | migrate_comprehensive.py | migrate_smart.py |
|---------|-------------------------|------------------|
| **Checks existing data** | ❌ No - always re-migrates | ✅ Yes - skips what exists |
| **Re-migration time** | 2-3 minutes | <1 second |
| **Duplicate handling** | ❌ Crashes with error | ✅ Auto-deduplicates |
| **User control** | ❌ No - all or nothing | ✅ Yes - choose what to migrate |
| **Error recovery** | ❌ Start from scratch | ✅ Resume from where it failed |

## Advanced Usage

### Force Re-migrate Everything
1. Drop tables first:
```bash
cd backend
./venv/Scripts/python.exe -c "import sqlite3; conn = sqlite3.connect('app/db/claims_analytics.db'); conn.execute('DROP TABLE IF EXISTS claims'); conn.execute('DROP TABLE IF EXISTS ssnb'); conn.commit(); print('Tables dropped')"
```

2. Run migration:
```bash
./venv/Scripts/python.exe migrate_smart.py
```

### Verify Migration Without Re-running
```bash
./venv/Scripts/python.exe -c "import sqlite3; conn = sqlite3.connect('app/db/claims_analytics.db'); print('Claims:', conn.execute('SELECT COUNT(*) FROM claims').fetchone()[0]); print('SSNB:', conn.execute('SELECT COUNT(*) FROM ssnb').fetchone()[0])"
```

### Check for Duplicates in CSV Before Migrating
```bash
./venv/Scripts/python.exe -c "import pandas as pd; df = pd.read_csv('SSNB.csv'); print(f'Total: {len(df)}, Unique: {df[\"CLAIMID\"].nunique()}, Duplicates: {df[\"CLAIMID\"].duplicated().sum()}')"
```

## Tips

1. **First time migrating?** Just run `migrate_smart.py` - it handles everything

2. **Claims already migrated?** Run `migrate_smart.py` - it will skip claims and only do SSNB

3. **Want to update SSNB data?** Replace SSNB.csv with new file, run script, choose option 2

4. **Script seems stuck?** It's probably migrating 630K claims - wait 2-3 minutes

5. **Need to restart?** Safe to Ctrl+C and re-run - it won't duplicate data

## Summary

**Old way (migrate_comprehensive.py):**
- Migrates everything every time
- 2-3 minutes even if data exists
- Crashes on duplicates
- No control

**New way (migrate_smart.py):**
- Only migrates what's missing
- <1 second if data exists
- Handles duplicates automatically
- Full control over what to migrate

**Bottom line:** Use `migrate_smart.py` - it's faster, smarter, and safer!
