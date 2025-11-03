# Column Name Mapping: dat.csv → Database

## Issue Identified:
Your actual dat.csv has different column names than what the migration script expects.

---

## Column Name Differences:

| Expected (Code) | Actual (Your dat.csv) | Fixed? |
|-----------------|----------------------|--------|
| `claim_date` | `CLAIMCLOSEDATE` | ✅ Fixed |
| `predicted_pain_suffering` | `CAUSATION_HIGH_RECOMMENDATION` | ✅ Fixed |
| `adjuster` | `ADJUSTERNAME` | ✅ Fixed |

---

## Updated Migration Script:

The migration script now handles **BOTH** formats automatically:

```python
# Auto-detects column names
claim_date_col = 'CLAIMCLOSEDATE' if 'CLAIMCLOSEDATE' in row else 'claim_date'
predicted_col = 'CAUSATION_HIGH_RECOMMENDATION' if 'CAUSATION_HIGH_RECOMMENDATION' in row else 'predicted_pain_suffering'
adjuster_col = 'ADJUSTERNAME' if 'ADJUSTERNAME' in row else 'adjuster'

# Uses detected column names
claim_date=str(row.get(claim_date_col, '')),
predicted_pain_suffering=float(row.get(predicted_col, 0)),
adjuster=str(row.get(adjuster_col, '')),
```

---

## How to Run Migration Now:

```bash
cd backend
.\venv\Scripts\python.exe migrate_csv_to_sqlite.py
```

The script will:
1. ✅ Check for `CLAIMCLOSEDATE` column, use it if exists
2. ✅ Check for `CAUSATION_HIGH_RECOMMENDATION` column, use it if exists
3. ✅ Check for `ADJUSTERNAME` column, use it if exists
4. ✅ Fall back to old names if new names not found (backward compatible)

---

## Other Potential Issues:

### Check These Columns in Your dat.csv:

If you have different names for these, let me know:

| Database Column | Expected CSV Column | Your Column Name? |
|----------------|---------------------|-------------------|
| `claim_id` | `claim_id` | ? |
| `VERSIONID` | `VERSIONID` | ? |
| `variance_pct` | `variance_pct` | ? |
| `COUNTYNAME` | `COUNTYNAME` | ? |
| `VENUE_RATING` | `VENUE_RATING` | ? |

---

## Common Column Name Issues:

### Issue 1: Date Column
```csv
# ❌ Old name (doesn't match)
claim_date,COUNTYNAME,...

# ✅ Your actual name
CLAIMCLOSEDATE,COUNTYNAME,...
```

**Fixed:** Migration now checks for `CLAIMCLOSEDATE` first.

---

### Issue 2: Prediction Column
```csv
# ❌ Old name (doesn't match)
predicted_pain_suffering,variance_pct,...

# ✅ Your actual name
CAUSATION_HIGH_RECOMMENDATION,variance_pct,...
```

**Fixed:** Migration now checks for `CAUSATION_HIGH_RECOMMENDATION` first.

---

### Issue 3: Adjuster Column
```csv
# ❌ Old name (doesn't match)
adjuster,COUNTYNAME,...

# ✅ Your actual name
ADJUSTERNAME,COUNTYNAME,...
```

**Fixed:** Migration now checks for `ADJUSTERNAME` first.

---

## Testing:

### Step 1: Check your dat.csv header
```bash
head -1 d:\Repositories\dashBoard\backend\data\dat.csv
```

### Step 2: Verify these columns exist:
- ✅ CLAIMCLOSEDATE
- ✅ CAUSATION_HIGH_RECOMMENDATION
- ✅ ADJUSTERNAME
- ✅ claim_id (or equivalent)
- ✅ COUNTYNAME
- ✅ VENUE_RATING

### Step 3: Run migration
```bash
cd backend
.\venv\Scripts\python.exe migrate_csv_to_sqlite.py
```

### Expected Output:
```
Loading weights from: backend\data\weights.csv
✓ Successfully migrated 52 weights

Loading claims from: backend\data\dat.csv
Total rows to migrate: 5,000,000
Migrating claims: 100%|████████████| 5000000/5000000
✓ Successfully migrated 5,000,000 claims

✓ MIGRATION COMPLETED SUCCESSFULLY
```

---

## If You Still Get Constraint Errors:

### Error: "UNIQUE constraint failed: claims.claim_id"

**Cause:** Duplicate claim_ids in your dat.csv

**Solution:**
```python
# Add to migration script (line 101):
claim_id=str(row.get('claim_id', f'GENERATED-{row.name}')),  # Generate if missing
```

---

### Error: "NOT NULL constraint failed: claims.claim_id"

**Cause:** Empty claim_id values

**Solution:** Already handled with default `''`

---

### Error: Column name not found

**Cause:** Your dat.csv has different column name

**Solution:** Tell me the actual column name and I'll add it to the mapping

---

## Summary:

**Problem:** dat.csv columns don't match expected names
- ❌ `claim_date` → Should be `CLAIMCLOSEDATE`
- ❌ `predicted_pain_suffering` → Should be `CAUSATION_HIGH_RECOMMENDATION`
- ❌ `adjuster` → Should be `ADJUSTERNAME`

**Solution:** ✅ Migration script updated to handle both formats automatically

**Next Step:** Run migration again - should work now!
