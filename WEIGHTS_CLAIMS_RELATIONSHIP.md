# How weights.csv and dat.csv Relate

## Quick Answer: **NO Foreign Key - Linked by Column Names** ✅

---

## The Relationship Explained

### Two Separate Tables:

```
┌─────────────────────────────────────┐
│  weights.csv → weights table        │
│  (52 rows - Metadata)               │
├─────────────────────────────────────┤
│ factor_name          base_weight    │
│ causation_probability    0.15       │
│ severity_injections      0.11       │
│ severity_objective...    0.08       │
└─────────────────────────────────────┘
           ↓
    (Name Matching)
           ↓
┌─────────────────────────────────────┐
│  dat.csv → claims table             │
│  (5,000,000 rows - Actual Data)     │
├─────────────────────────────────────┤
│ claim_id    causation_   severity_  │
│             probability  injections │
│ CLM-001         0.541       0.739   │
│ CLM-002         0.627       0.58    │
│ CLM-003         0.747       0.685   │
│ ... (5M rows)                       │
└─────────────────────────────────────┘
```

---

## How It Works:

### weights.csv = "The Recipe"
```csv
factor_name,base_weight,min_weight,max_weight,category,description
causation_probability,0.15,0.05,0.30,Causation,How important is causation?
severity_injections,0.11,0.05,0.20,Severity,How important are injections?
```

**Says:**
- "causation_probability is 15% important"
- "severity_injections is 11% important"

---

### dat.csv = "The Ingredients"
```csv
claim_id,causation_probability,severity_injections,...
CLM-2025-000001,0.541,0.739,...
CLM-2023-000002,0.627,0.58,...
```

**Says:**
- "Claim CLM-001 has causation_probability VALUE of 0.541"
- "Claim CLM-001 has severity_injections VALUE of 0.739"

---

## The Calculation:

### For Claim CLM-2025-000001:

```python
# Step 1: Get the claim's VALUES
causation_value = 0.541        # From dat.csv
injections_value = 0.739       # From dat.csv

# Step 2: Get the WEIGHTS (importance)
causation_weight = 0.15        # From weights.csv
injections_weight = 0.11       # From weights.csv

# Step 3: Calculate weighted contributions
causation_contribution = 0.541 × 0.15 = 0.0812
injections_contribution = 0.739 × 0.11 = 0.0813

# Step 4: Sum ALL factors (52 total)
predicted_settlement = sum of all (value × weight)
```

---

## Database Schema:

### Claims Table:
```sql
CREATE TABLE claims (
    id INTEGER PRIMARY KEY,
    claim_id TEXT UNIQUE,
    -- ... other fields ...
    causation_probability REAL,    ← Stores VALUES (0.541, 0.627, ...)
    severity_injections REAL,      ← Stores VALUES (0.739, 0.58, ...)
    severity_objective_findings REAL,
    -- ... 50 more factor columns ...
);

-- 5,000,000 rows (one per claim)
```

### Weights Table:
```sql
CREATE TABLE weights (
    id INTEGER PRIMARY KEY,
    factor_name TEXT UNIQUE,        ← Must match column name in claims!
    base_weight REAL,               ← The importance (0.15, 0.11, ...)
    min_weight REAL,
    max_weight REAL,
    category TEXT,
    description TEXT
);

-- 52 rows (one per factor)
```

### NO Foreign Key Constraint!

```sql
-- This does NOT exist:
ALTER TABLE claims
    ADD CONSTRAINT fk_weights
    FOREIGN KEY (???) REFERENCES weights(???);

-- Why? Because the relationship is implicit through naming
```

---

## The Implicit Link:

```python
# In code, the link happens like this:

# 1. Fetch all weights
weights = db.query(Weight).all()
# Result: [
#   {factor_name: "causation_probability", base_weight: 0.15},
#   {factor_name: "severity_injections", base_weight: 0.11},
#   ...
# ]

# 2. Fetch claims
claims = db.query(Claim).all()

# 3. For each claim, calculate prediction
for claim in claims:
    prediction = 0

    for weight in weights:
        # Get the VALUE from claim using the factor_name
        factor_name = weight.factor_name  # "causation_probability"

        # Access claim column dynamically
        claim_value = getattr(claim, factor_name)  # claim.causation_probability

        # Multiply value × weight
        prediction += claim_value * weight.base_weight

    claim.predicted_settlement = prediction
```

---

## Visual Example:

### weights.csv (Configuration):
```
┌──────────────────────┬─────────────┐
│ factor_name          │ base_weight │
├──────────────────────┼─────────────┤
│ causation_probability│    0.15     │ ← "This factor is 15% important"
│ severity_injections  │    0.11     │ ← "This factor is 11% important"
└──────────────────────┴─────────────┘
```

### dat.csv (Data - Claim CLM-001):
```
┌─────────┬───────────────────┬──────────────────┐
│ claim_id│ causation_prob... │ severity_inject..│
├─────────┼───────────────────┼──────────────────┤
│ CLM-001 │      0.541        │      0.739       │ ← "This claim's values"
└─────────┴───────────────────┴──────────────────┘
```

### Calculation:
```
Weighted Score for CLM-001:

  causation_probability:
    value = 0.541 (from claim)
    weight = 0.15 (from weights)
    contribution = 0.541 × 0.15 = 0.0812

  severity_injections:
    value = 0.739 (from claim)
    weight = 0.11 (from weights)
    contribution = 0.739 × 0.11 = 0.0813

  ... (50 more factors)

  Final Prediction = 0.0812 + 0.0813 + ... = 74,802.05
```

---

## What Happens in Recalibration Tab:

### Step 1: Load Weights
```javascript
// Frontend fetches weights
GET /api/v1/weights

Response:
[
  {
    id: 1,
    factor_name: "causation_probability",
    base_weight: 0.15,
    min_weight: 0.05,
    max_weight: 0.30,
    category: "Causation",
    description: "Probability that injury is causally related"
  },
  ...
]
```

### Step 2: User Adjusts Slider
```javascript
// User moves slider for causation_probability
Old value: 0.15
New value: 0.20  ← User increased importance
```

### Step 3: Recalculate All 5M Claims
```python
# Backend recalculates predictions
new_weights = {"causation_probability": 0.20, ...}

for claim in all_5_million_claims:
    # Get claim value
    causation_value = claim.causation_probability  # 0.541

    # Get NEW weight
    causation_weight = new_weights["causation_probability"]  # 0.20

    # Recalculate
    new_contribution = 0.541 × 0.20 = 0.1082  # (was 0.0812)

    # Sum with all other factors
    new_prediction = sum(all_new_contributions)
```

### Step 4: Show Impact
```javascript
// Frontend shows:
Old prediction: $74,802.05
New prediction: $76,450.23  ← Increased because weight increased
Variance change: +2.2%
```

---

## Why NO Foreign Key?

### Reason 1: Different Granularity
```
weights: 52 rows (one per factor)
claims: 5,000,000 rows (one per claim)

Can't have FK: One weight applies to ALL claims
```

### Reason 2: Many-to-Many Conceptually
```
Each weight is used by ALL 5M claims
Each claim uses ALL 52 weights

Traditional FK doesn't fit this pattern
```

### Reason 3: Dynamic Column Access
```python
# The relationship is through column naming
weight.factor_name = "causation_probability"
                  ↓ (matches)
claim.causation_probability (column name)

# Accessed dynamically:
getattr(claim, weight.factor_name)
```

---

## Critical Requirement: **Names MUST Match**

### ✅ Correct:

**weights.csv:**
```csv
factor_name,base_weight,...
causation_probability,0.15,...
severity_injections,0.11,...
```

**dat.csv columns:**
```csv
claim_id,causation_probability,severity_injections,...
```

**Result:** ✅ Perfect match! Everything works.

---

### ❌ Broken:

**weights.csv:**
```csv
factor_name,base_weight,...
causation_prob,0.15,...          ← Typo!
severity_inject,0.11,...         ← Shortened!
```

**dat.csv columns:**
```csv
claim_id,causation_probability,severity_injections,...
```

**Result:**
- ❌ `causation_prob` weight ignored (no matching column)
- ❌ `causation_probability` column not weighted
- ❌ Predictions will be wrong!

---

## Summary:

| Aspect | weights.csv | dat.csv | Relationship |
|--------|------------|---------|--------------|
| **Purpose** | Configuration/Metadata | Actual claim data | Name matching |
| **Rows** | 52 (one per factor) | 5,000,000 (one per claim) | N/A |
| **Contains** | Importance of factors | Values of factors | N/A |
| **Example** | causation_probability = 0.15 | CLM-001 causation_probability = 0.541 | Column name |
| **Link Type** | NO Foreign Key | NO Foreign Key | Implicit via naming |
| **Database** | `weights` table | `claims` table | Separate tables |

---

## In Practice:

**Your weights.csv defines WHAT matters:**
```csv
causation_probability,0.15,...  ← "Causation is 15% of the prediction"
severity_injections,0.11,...     ← "Injections are 11% of the prediction"
```

**Your dat.csv provides the DATA:**
```csv
CLM-001,0.541,0.739,...  ← "This claim has causation=0.541, injections=0.739"
```

**System combines them:**
```
Prediction = (0.541 × 0.15) + (0.739 × 0.11) + ... (50 more)
           = 0.0812      + 0.0813      + ...
           = $74,802.05
```

---

## Final Answer:

**Question:** Will it have reference with dat.csv like linking of claim ID?

**Answer:**
- ❌ **NO** - No claim_id linking
- ❌ **NO** - No foreign key
- ✅ **YES** - Linked by column name matching
- ✅ **YES** - Each weight factor_name must match a column in claims table

**Type:** Implicit relationship through naming convention, not database FK.
