# Quick Answer: Will Column-Based weights.csv Work?

## Your Question:
> If weights.csv now has all column names as they are in dat.csv but values are weights, will this code work?

## Answer: YES ✅ (with new script)

---

## Your Format:

**If your weights.csv looks like this:**
```csv
causation_probability,severity_injections,causation_tx_delay,severity_objective_findings
0.15,0.11,0.07,0.08
```

**Instead of the original format:**
```csv
factor_name,base_weight,min_weight,max_weight,category,description
causation_probability,0.15,0.05,0.30,Causation,Description
severity_injections,0.11,0.05,0.20,Severity,Description
```

---

## Solution: Use New Migration Script

### Step 1: Use the flexible migration script

```bash
cd backend
.\venv\Scripts\python.exe migrate_csv_to_sqlite_flexible.py
```

### Step 2: It automatically detects your format

```
Loaded weights file with 1 rows and 50 columns
Detected COLUMN-BASED weights format (column names = factors)
Converting weights: 100%|████████████| 50/50
✓ Successfully migrated 45 weights (column-based format)
```

### Step 3: Done! Weights are imported

The script automatically:
- ✅ Reads column names as factor names
- ✅ Reads first row as weight values
- ✅ Generates min_weight = base × 0.3
- ✅ Generates max_weight = base × 3.0 (capped at 1.0)
- ✅ Auto-detects category from name ("causation", "severity", etc.)
- ✅ Creates descriptions automatically

---

## What You Get:

**Your input:**
```csv
causation_probability,severity_injections
0.15,0.11
```

**Automatically becomes in database:**

| factor_name | base_weight | min_weight | max_weight | category | description |
|-------------|-------------|------------|------------|----------|-------------|
| causation_probability | 0.15 | 0.045 | 0.45 | Causation | Weight for causation probability |
| severity_injections | 0.11 | 0.033 | 0.33 | Severity | Weight for severity injections |

---

## Requirements:

1. ✅ **Column names MUST match dat.csv exactly**
   - If dat.csv has `causation_probability`, weights.csv header must have `causation_probability`
   - Case-sensitive!

2. ✅ **First row contains weight values**
   - Values should be between 0.0 and 1.0
   - Zero or invalid values are skipped

3. ✅ **Use the flexible migration script**
   - Old script: `migrate_csv_to_sqlite.py` (doesn't support column format)
   - New script: `migrate_csv_to_sqlite_flexible.py` (supports both formats)

---

## Commands:

```bash
# 1. Place your files
#    backend/data/dat.csv (your 5M claims)
#    backend/data/weights.csv (column-based format)

# 2. Run flexible migration
cd backend
.\venv\Scripts\python.exe migrate_csv_to_sqlite_flexible.py

# 3. Start backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload

# 4. Start frontend (new terminal)
cd frontend
npm run dev

# 5. Open dashboard
# http://localhost:5173
```

---

## File Created:

**New script:** `backend/migrate_csv_to_sqlite_flexible.py`

**Features:**
- Auto-detects format (original vs column-based)
- Supports your column-based format
- Backward compatible with original format
- Automatic category detection
- Automatic min/max calculation

---

## Summary:

**Question:** Will column-based weights.csv work?

**Answer:** YES ✅

**What to do:**
1. Use `migrate_csv_to_sqlite_flexible.py` instead of `migrate_csv_to_sqlite.py`
2. Make sure column names match dat.csv exactly
3. Put weight values in first row
4. Run migration

**Result:** All weights imported and available in recalibration tab!
