# Fix: Constraint Error During Migration

## Problem:
Migration fails with constraint error because your actual dat.csv has different column names.

---

## Your Actual Column Names:

```csv
# Your dat.csv header:
claim_id,VERSIONID,CLAIMCLOSEDATE,...,CAUSATION_HIGH_RECOMMENDATION,...,ADJUSTERNAME,...
```

Not:
```csv
# What code expected:
claim_id,VERSIONID,claim_date,...,predicted_pain_suffering,...,adjuster,...
```

---

## What I Fixed:

### Migration script now handles BOTH formats:

```python
# Auto-detects your column names
claim_date_col = 'CLAIMCLOSEDATE' if 'CLAIMCLOSEDATE' in row else 'claim_date'
predicted_col = 'CAUSATION_HIGH_RECOMMENDATION' if 'CAUSATION_HIGH_RECOMMENDATION' in row else 'predicted_pain_suffering'
adjuster_col = 'ADJUSTERNAME' if 'ADJUSTERNAME' in row else 'adjuster'
```

---

## Column Mapping:

| Database Field | Your CSV Column | Old CSV Column |
|---------------|----------------|----------------|
| `claim_date` | `CLAIMCLOSEDATE` | `claim_date` |
| `predicted_pain_suffering` | `CAUSATION_HIGH_RECOMMENDATION` | `predicted_pain_suffering` |
| `adjuster` | `ADJUSTERNAME` | `adjuster` |

---

## How to Run Now:

```bash
cd d:\Repositories\dashBoard\backend
.\venv\Scripts\python.exe migrate_csv_to_sqlite.py
```

**Should work now!** ✅

---

## If Still Fails:

Tell me:
1. What is the exact error message?
2. Does your dat.csv have a `claim_id` column?
3. Run this to see first row:
   ```bash
   head -2 data\dat.csv
   ```

---

## Changes Made:

**File:** `backend/migrate_csv_to_sqlite.py`
**Lines:** 95-98, 138-139

**Status:** ✅ Fixed - Migration now supports your column names
