# weights.csv Format Guide

## Two Supported Formats

The system now supports **TWO different formats** for `weights.csv`:

---

## Format 1: Original Format (Recommended)

**Best for:** Clear categorization and descriptions

```csv
factor_name,base_weight,min_weight,max_weight,category,description
causation_probability,0.15,0.05,0.30,Causation,Probability of causal relation
severity_injections,0.11,0.05,0.20,Severity,Number and type of injections
severity_objective_findings,0.08,0.03,0.15,Severity,Presence of objective clinical findings
causation_tx_delay,0.07,0.02,0.12,Causation,Delay in seeking treatment
Treatment_Compliance,0.06,0.02,0.10,Treatment,Compliance with treatment plan
```

**Columns:**
- `factor_name` - Must match column name in dat.csv exactly
- `base_weight` - Default weight (0.01-0.30 typical range)
- `min_weight` - Minimum allowed weight for slider
- `max_weight` - Maximum allowed weight for slider
- `category` - One of: Causation, Severity, Treatment, Clinical, Disability
- `description` - Human-readable explanation

---

## Format 2: Column-Based Format (YOUR FORMAT)

**Best for:** Quick export from existing systems

```csv
causation_probability,severity_injections,severity_objective_findings,causation_tx_delay,Treatment_Compliance
0.15,0.11,0.08,0.07,0.06
```

**Structure:**
- **Header row** = factor names (must match dat.csv columns exactly)
- **First data row** = weight values (0.01-1.00)

**Auto-generated settings:**
- `min_weight` = base_weight × 0.3 (30% of base)
- `max_weight` = base_weight × 3.0 (300% of base, capped at 1.0)
- `category` = Auto-detected from name:
  - Contains "causation" → Causation
  - Contains "severity" → Severity
  - Contains "treatment"/"therapy"/"injection" → Treatment
  - Contains "clinical"/"finding"/"diagnosis" → Clinical
  - Contains "disability"/"immobilization" → Disability
  - Otherwise → Other
- `description` = Auto-generated from factor name

---

## Which Format to Use?

### Use Format 1 (Original) if:
- ✅ You want precise control over min/max weights
- ✅ You want custom categories
- ✅ You want descriptive text for each factor
- ✅ You're creating weights.csv manually

### Use Format 2 (Column-Based) if:
- ✅ You're exporting from existing ML model
- ✅ Column names already match dat.csv
- ✅ You just want quick weight values
- ✅ You don't need custom descriptions

---

## Examples

### Example 1: Original Format (Complete Control)

```csv
factor_name,base_weight,min_weight,max_weight,category,description
causation_probability,0.15,0.05,0.30,Causation,Probability injury causally related to incident
severity_injections,0.11,0.05,0.20,Severity,Number and type of injections received
severity_objective_findings,0.08,0.03,0.15,Severity,Presence of objective clinical findings
causation_tx_delay,0.07,0.02,0.12,Causation,Delay in seeking initial treatment
Treatment_Compliance,0.06,0.02,0.10,Treatment,Adherence to prescribed treatment plan
Clinical_Findings,0.05,0.01,0.10,Clinical,Clinical examination findings
Surgical_Intervention,0.12,0.05,0.25,Treatment,Surgical procedures performed
Immobilization_Used,0.04,0.01,0.08,Disability,Use of immobilization devices
```

---

### Example 2: Column-Based Format (Quick Setup)

**Your weights.csv:**
```csv
causation_probability,severity_injections,severity_objective_findings,causation_tx_delay,Treatment_Compliance,Clinical_Findings,Surgical_Intervention,Immobilization_Used
0.15,0.11,0.08,0.07,0.06,0.05,0.12,0.04
```

**Automatically converted to:**
```
factor_name: causation_probability
base_weight: 0.15
min_weight: 0.045 (0.15 × 0.3)
max_weight: 0.45 (0.15 × 3.0)
category: Causation (detected from name)
description: Weight for causation probability

factor_name: severity_injections
base_weight: 0.11
min_weight: 0.033 (0.11 × 0.3)
max_weight: 0.33 (0.11 × 3.0)
category: Severity (detected from name)
description: Weight for severity injections

... (and so on for all columns)
```

---

## How to Use Format 2 (Column-Based)

### Step 1: Create weights.csv with column names from dat.csv

Your `dat.csv` has these columns:
```
claim_id,claim_date,COUNTYNAME,variance_pct,causation_probability,severity_injections,...
```

Your `weights.csv` should have:
```csv
causation_probability,severity_injections,severity_objective_findings,causation_tx_delay
0.15,0.11,0.08,0.07
```

### Step 2: Run flexible migration script

```bash
cd backend
.\venv\Scripts\python.exe migrate_csv_to_sqlite_flexible.py
```

**Output:**
```
Loading weights from: backend\data\weights.csv
Loaded weights file with 1 rows and 50 columns
Detected COLUMN-BASED weights format (column names = factors)
Converting weights: 100%|████████████| 50/50
✓ Successfully migrated 45 weights (column-based format)
(5 skipped: zero or invalid values)
```

### Step 3: Verify weights were imported

```bash
cd backend/app/db
sqlite3 claims_analytics.db

SELECT factor_name, base_weight, category FROM weights LIMIT 5;
```

**Expected output:**
```
causation_probability|0.15|Causation
severity_injections|0.11|Severity
severity_objective_findings|0.08|Severity
causation_tx_delay|0.07|Causation
Treatment_Compliance|0.06|Treatment
```

---

## Format Detection (Automatic)

The migration script **automatically detects** which format you're using:

```python
def detect_weights_format(df):
    # Has 'factor_name' and 'base_weight' columns?
    if 'factor_name' in df.columns and 'base_weight' in df.columns:
        return 'original'  # Format 1
    else:
        return 'column_based'  # Format 2
```

**You don't need to specify** - it figures it out automatically!

---

## Important Notes for Column-Based Format

### ✅ Column Names Must Match dat.csv Exactly

**Your dat.csv columns:**
```
causation_probability,severity_injections,Treatment_Compliance
```

**Your weights.csv header MUST match:**
```csv
causation_probability,severity_injections,Treatment_Compliance
0.15,0.11,0.06
```

**❌ This will NOT work (mismatched names):**
```csv
causation_prob,severity_inject,treatment_comply
0.15,0.11,0.06
```

---

### ✅ Only First Row is Read

If your weights.csv has multiple rows:
```csv
causation_probability,severity_injections
0.15,0.11
0.20,0.13
0.18,0.12
```

**Only the first data row is used:** 0.15, 0.11

---

### ✅ Zero or Invalid Values are Skipped

```csv
causation_probability,severity_injections,invalid_column
0.15,0.0,abc
```

**Result:**
- causation_probability: ✅ Imported (0.15)
- severity_injections: ⏭️ Skipped (zero weight)
- invalid_column: ⏭️ Skipped (invalid value 'abc')

---

### ✅ Weights are Capped at 1.0

```csv
some_factor
0.99
```

**Calculated:**
- base_weight: 0.99
- min_weight: 0.297 (0.99 × 0.3)
- max_weight: 1.0 (capped, not 2.97)

---

## Migration Command

### For Format 1 (Original):
```bash
cd backend
.\venv\Scripts\python.exe migrate_csv_to_sqlite.py
```

### For Format 2 (Column-Based - YOUR FORMAT):
```bash
cd backend
.\venv\Scripts\python.exe migrate_csv_to_sqlite_flexible.py
```

### For Both Formats (Auto-Detect):
```bash
cd backend
.\venv\Scripts\python.exe migrate_csv_to_sqlite_flexible.py
```

---

## Full Example: Using Your Column-Based Format

### Your Setup:

**dat.csv** (5,000,000 rows):
```csv
claim_id,claim_date,COUNTYNAME,variance_pct,causation_probability,severity_injections,causation_tx_delay,...
C001,2024-01-15,Los Angeles,12.5,0.85,0.92,0.45,...
C002,2024-01-16,Orange,8.3,0.72,0.65,0.88,...
... (5M rows)
```

**weights.csv** (YOUR FORMAT):
```csv
causation_probability,severity_injections,causation_tx_delay,severity_objective_findings,Treatment_Compliance
0.15,0.11,0.07,0.08,0.06
```

### Steps:

1. **Place files:**
```
backend/data/dat.csv        (5M rows)
backend/data/weights.csv    (1 row with weights)
```

2. **Run migration:**
```bash
cd backend
.\venv\Scripts\python.exe migrate_csv_to_sqlite_flexible.py
```

3. **Expected output:**
```
Loading weights from: backend\data\weights.csv
Loaded weights file with 1 rows and 5 columns
Detected COLUMN-BASED weights format (column names = factors)
Converting weights: 100%|████████████| 5/5
✓ Successfully migrated 5 weights (column-based format)

Loading claims from: backend\data\dat.csv
Total rows to migrate: 5,000,000
Migrating claims: 100%|████████████| 5000000/5000000
✓ Successfully migrated 5,000,000 claims

✓ MIGRATION COMPLETED SUCCESSFULLY
```

4. **Verify:**
```bash
sqlite3 backend/app/db/claims_analytics.db "SELECT * FROM weights;"
```

**Output:**
```
1|causation_probability|0.15|0.045|0.45|Causation|Weight for causation probability
2|severity_injections|0.11|0.033|0.33|Severity|Weight for severity injections
3|causation_tx_delay|0.07|0.021|0.21|Causation|Weight for causation tx delay
4|severity_objective_findings|0.08|0.024|0.24|Severity|Weight for severity objective findings
5|Treatment_Compliance|0.06|0.018|0.18|Treatment|Weight for Treatment Compliance
```

---

## Summary

**Question:** If weights.csv has column names matching dat.csv with weight values, will it work?

**Answer:** **YES ✅** - Use `migrate_csv_to_sqlite_flexible.py`

**Your Format:**
```csv
causation_probability,severity_injections,causation_tx_delay
0.15,0.11,0.07
```

**What Happens:**
1. Script detects column-based format
2. Reads column names from header
3. Reads weight values from first row
4. Auto-generates min/max weights (30% and 300% of base)
5. Auto-detects category from factor name
6. Creates descriptions automatically
7. Imports into database

**Result:** All weights available in recalibration tab with sliders!
