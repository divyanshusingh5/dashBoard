# Venue Rating Shift - Dollar Amount Based Analysis

## The Better Approach: Compare Actual Dollar Amounts

Instead of using variance percentage, we compare **average actual settlement amounts** and **absolute dollar prediction errors** when all other factors are constant.

---

## Example: Harris County Analysis

### Step 1: Isolate by All Factors EXCEPT Venue Rating

**Keep these CONSTANT:**
- Injury Type: SSNB (Sprain/Strain, Neck/Back)
- Severity: Medium
- IOL: 2
- Attorney: Yes
- Age group: 25-35
- Gender: Male

---

### Step 2: Compare Dollar Amounts Across Venue Ratings

#### Current Rating: "Liberal"

```sql
SELECT
    COUNT(*) as claim_count,
    AVG(DOLLARAMOUNTHIGH) as avg_actual_settlement,
    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
    AVG(ABS(DOLLARAMOUNTHIGH - CAUSATION_HIGH_RECOMMENDATION)) as avg_dollar_error
FROM claims
WHERE COUNTYNAME = 'Harris'
  AND VENUERATING = 'Liberal'
  AND PRIMARY_INJURYGROUP_CODE = 'SSNB'
  AND CAUTION_LEVEL = 'Medium'
  AND IOL = 2
  AND HASATTORNEY = 1
```

**Results - Harris County with "Liberal" rating:**
```
Claims: 45
Avg Actual Settlement: $85,000
Avg Predicted: $55,000
Avg Dollar Error: $30,000    ← Key metric!
```

---

#### Test Alternative: "Moderate" Rating

Look at other counties with "Moderate" rating and SAME factors:

```sql
SELECT
    COUNT(*) as claim_count,
    AVG(DOLLARAMOUNTHIGH) as avg_actual_settlement,
    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
    AVG(ABS(DOLLARAMOUNTHIGH - CAUSATION_HIGH_RECOMMENDATION)) as avg_dollar_error
FROM claims
WHERE VENUERATING = 'Moderate'
  AND PRIMARY_INJURYGROUP_CODE = 'SSNB'
  AND CAUTION_LEVEL = 'Medium'
  AND IOL = 2
  AND HASATTORNEY = 1
```

**Results - "Moderate" rated counties with same factors:**
```
Claims: 120
Avg Actual Settlement: $82,000
Avg Predicted: $60,000
Avg Dollar Error: $22,000    ← Better!
```

---

#### Test Alternative: "Conservative" Rating

```sql
-- Same query with VENUERATING = 'Conservative'
```

**Results - "Conservative" rated counties:**
```
Claims: 65
Avg Actual Settlement: $83,000
Avg Predicted: $58,000
Avg Dollar Error: $25,000
```

---

### Step 3: Compare ALL Options - Dollar-Based

| Venue Rating | Sample | Avg Actual | Avg Predicted | **Avg $ Error** | $ Improvement |
|--------------|--------|------------|---------------|-----------------|---------------|
| Liberal (current) | 45 | $85,000 | $55,000 | **$30,000** | - |
| Moderate (test) | 120 | $82,000 | $60,000 | **$22,000** | **$8,000** ✅ |
| Conservative (test) | 65 | $83,000 | $58,000 | **$25,000** | $5,000 |

**Best Choice:** "Moderate" - Reduces dollar error by $8,000 per claim

---

### Step 4: Modified Decision Thresholds (Dollar-Based)

```python
# Instead of variance percentage thresholds:
# OLD: if improvement > 2.0% or improvement/current > 0.15

# NEW: Dollar-based thresholds
current_dollar_error = AVG(ABS(actual - predicted)) for current venue
alternative_dollar_error = AVG(ABS(actual - predicted)) for alternative venue
dollar_improvement = current_dollar_error - alternative_dollar_error

# Recommend if:
if dollar_improvement > $5,000 or dollar_improvement/current_dollar_error > 0.15:
    recommend_venue_shift()
```

**Thresholds:**
1. **Absolute Dollar Improvement ≥ $5,000** per claim
   - Example: Current $30K error → Alternative $24K error = $6K improvement ✅

2. **Relative Improvement ≥ 15%** of current error
   - Example: Current $30K error → Alternative $26K error = $4K (13%) ❌
   - Example: Current $30K error → Alternative $25K error = $5K (17%) ✅

---

## Complete Example with Real Numbers

### Harris County, Texas - Full Analysis

#### Current Situation (Liberal Rating)

**Isolated Cohort:**
- Injury: SSNB (Sprain/Strain, Neck/Back)
- Severity: Medium
- IOL: 2
- Attorney: Yes

**45 Claims Performance:**
```
Claim #1:
  Actual: $90,000
  Predicted: $60,000
  Error: $30,000

Claim #2:
  Actual: $80,000
  Predicted: $52,000
  Error: $28,000

Claim #3:
  Actual: $88,000
  Predicted: $56,000
  Error: $32,000

... (42 more claims)

AVERAGE:
  Actual: $85,000
  Predicted: $55,000
  Dollar Error: $30,000
```

---

#### Alternative: Moderate Rating

**120 Similar Claims from "Moderate" Counties:**
```
Claim #1:
  Actual: $84,000
  Predicted: $62,000
  Error: $22,000

Claim #2:
  Actual: $80,000
  Predicted: $59,000
  Error: $21,000

Claim #3:
  Actual: $82,000
  Predicted: $60,000
  Error: $22,000

... (117 more claims)

AVERAGE:
  Actual: $82,000
  Predicted: $60,000
  Dollar Error: $22,000
```

---

#### Alternative: Conservative Rating

**65 Similar Claims from "Conservative" Counties:**
```
AVERAGE:
  Actual: $83,000
  Predicted: $58,000
  Dollar Error: $25,000
```

---

### Decision Analysis

**Current (Liberal):**
- Average dollar error: **$30,000**

**Best Alternative (Moderate):**
- Average dollar error: **$22,000**
- **Improvement: $8,000 per claim**

**Check Thresholds:**

1. **Absolute improvement:**
   - $8,000 > $5,000 ✅ **PASS**

2. **Relative improvement:**
   - $8,000 / $30,000 = 27%
   - 27% > 15% ✅ **PASS**

3. **Sample size:**
   - Current: 45 ≥ 10 ✅
   - Alternative: 120 ≥ 10 ✅
   - **Confidence: HIGH**

---

### Final Recommendation

```json
{
  "county": "Harris",
  "state": "TX",
  "current_venue_rating": "Liberal",
  "current_avg_actual": 85000,
  "current_avg_predicted": 55000,
  "current_avg_dollar_error": 30000,
  "current_claim_count": 45,

  "recommended_venue_rating": "Moderate",
  "alternative_avg_actual": 82000,
  "alternative_avg_predicted": 60000,
  "alternative_avg_dollar_error": 22000,
  "alternative_claim_count": 120,

  "dollar_improvement": 8000,
  "percent_improvement": 27,
  "confidence": "high",

  "annual_impact": {
    "claims_per_year": 45,
    "total_dollar_improvement": 360000,
    "description": "Expected to save $360K annually in prediction errors"
  },

  "controlled_for": [
    "injury_type",
    "severity",
    "impact",
    "attorney"
  ]
}
```

**Business Impact:**
- **Per Claim:** $8,000 closer prediction
- **45 claims/year:** $8,000 × 45 = **$360,000 annual improvement**
- **Confidence:** High (both samples >10 claims)
- **Action:** Shift Harris County from "Liberal" to "Moderate"

---

## Why Dollar-Based is Better Than Variance-Based

### Problem with Variance Percentage

**Example 1: Low-value claim**
```
Actual: $10,000
Predicted: $8,000
Error: $2,000
Variance: 20%
```

**Example 2: High-value claim**
```
Actual: $100,000
Predicted: $80,000
Error: $20,000
Variance: 20%
```

**Both show 20% variance, but Example 2 is 10x more costly!**

---

### Advantage of Dollar-Based

**Same examples:**
```
Example 1: $2,000 error  ← Minor issue
Example 2: $20,000 error ← Major issue
```

**Dollar-based analysis prioritizes fixing the $20K errors!**

---

## Modified SQL Query for Implementation

```sql
-- Dollar-based venue comparison
WITH current_venue AS (
  SELECT
    'Harris' as county,
    'Liberal' as venue_rating,
    COUNT(*) as claim_count,
    AVG(DOLLARAMOUNTHIGH) as avg_actual,
    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
    AVG(ABS(DOLLARAMOUNTHIGH - CAUSATION_HIGH_RECOMMENDATION)) as avg_dollar_error
  FROM claims
  WHERE COUNTYNAME = 'Harris'
    AND VENUERATING = 'Liberal'
    AND PRIMARY_INJURYGROUP_CODE = 'SSNB'
    AND CAUTION_LEVEL = 'Medium'
    AND IOL = 2
),
moderate_venue AS (
  SELECT
    'Moderate' as venue_rating,
    COUNT(*) as claim_count,
    AVG(DOLLARAMOUNTHIGH) as avg_actual,
    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
    AVG(ABS(DOLLARAMOUNTHIGH - CAUSATION_HIGH_RECOMMENDATION)) as avg_dollar_error
  FROM claims
  WHERE VENUERATING = 'Moderate'
    AND PRIMARY_INJURYGROUP_CODE = 'SSNB'
    AND CAUTION_LEVEL = 'Medium'
    AND IOL = 2
),
conservative_venue AS (
  SELECT
    'Conservative' as venue_rating,
    COUNT(*) as claim_count,
    AVG(DOLLARAMOUNTHIGH) as avg_actual,
    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
    AVG(ABS(DOLLARAMOUNTHIGH - CAUSATION_HIGH_RECOMMENDATION)) as avg_dollar_error
  FROM claims
  WHERE VENUERATING = 'Conservative'
    AND PRIMARY_INJURYGROUP_CODE = 'SSNB'
    AND CAUTION_LEVEL = 'Medium'
    AND IOL = 2
)
SELECT
  c.venue_rating as current_venue,
  c.avg_dollar_error as current_error,
  m.venue_rating as moderate_venue,
  m.avg_dollar_error as moderate_error,
  (c.avg_dollar_error - m.avg_dollar_error) as moderate_improvement,
  co.venue_rating as conservative_venue,
  co.avg_dollar_error as conservative_error,
  (c.avg_dollar_error - co.avg_dollar_error) as conservative_improvement,
  CASE
    WHEN m.avg_dollar_error < c.avg_dollar_error
         AND m.avg_dollar_error < co.avg_dollar_error
         AND (c.avg_dollar_error - m.avg_dollar_error) > 5000
    THEN 'Recommend: Moderate'
    WHEN co.avg_dollar_error < c.avg_dollar_error
         AND co.avg_dollar_error < m.avg_dollar_error
         AND (c.avg_dollar_error - co.avg_dollar_error) > 5000
    THEN 'Recommend: Conservative'
    ELSE 'Keep current: Liberal'
  END as recommendation
FROM current_venue c, moderate_venue m, conservative_venue co;
```

---

## Summary: Dollar-Based vs Variance-Based

| Metric | Variance-Based | Dollar-Based |
|--------|---------------|--------------|
| **Small claims** | Over-weighted | Appropriately weighted |
| **Large claims** | Under-weighted | Appropriately weighted |
| **Business impact** | Unclear | Direct ($360K savings) |
| **Interpretation** | "27% better" | "$8K closer per claim" |
| **Decision making** | Less intuitive | Highly intuitive |

---

## Recommendation: Use Both!

**Primary metric:** Dollar-based (main business impact)
**Secondary metric:** Variance-based (relative performance)

**Example output:**
```
Harris County Recommendation:
✅ Shift from Liberal to Moderate

Dollar Impact:
  Current avg error: $30,000
  Moderate avg error: $22,000
  Improvement: $8,000 per claim (27% reduction)
  Annual savings: $360,000 (45 claims/year)

Settlement Amounts (when factors constant):
  Liberal counties: $85,000 avg actual
  Moderate counties: $82,000 avg actual
  Difference: $3,000 (not significant)

Prediction Accuracy:
  Liberal: $55K predicted vs $85K actual
  Moderate: $60K predicted vs $82K actual
  Moderate predictions are $5K closer!
```

**This gives stakeholders both perspectives:**
1. **Dollar impact:** "We'll save $360K/year"
2. **Performance improvement:** "27% more accurate"
3. **Settlement context:** "Actual settlements are similar"

---

**Would you like me to modify the backend code to use dollar-based comparison instead of variance-based?**
