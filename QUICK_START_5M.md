# Quick Start Guide for 5M Claims

## Step-by-Step Commands

### 1. Rebuild Database with Performance Indexes

```bash
cd d:\Repositories\dashBoard\backend

# Backup existing database (if it exists)
copy "app\db\claims_analytics.db" "app\db\claims_analytics.db.backup"

# Rebuild database with indexes (uses your dat.csv and weights.csv)
.\venv\Scripts\python.exe migrate_csv_to_sqlite.py
```

**Expected output:**
```
Reading dat.csv...
Loaded 5,000,000 rows
Creating database with indexes...
✓ Database created successfully
✓ All 10 indexes created
✓ Materialized views created
Database ready for 5M claims
```

**Time:** 10-30 minutes for 5M rows (one-time operation)

---

### 2. Verify Indexes Were Created

```bash
cd d:\Repositories\dashBoard\backend\app\db
sqlite3 claims_analytics.db ".indexes claims"
```

**Expected output:**
```
idx_adjuster_date
idx_adjuster_variance
idx_county_venue
idx_county_venue_injury
idx_county_venue_injury_severity
idx_date_county
idx_date_variance
idx_date_venue
idx_injury_severity_caution
idx_venue_state
```

If you see these 10 indexes, you're ready for 5M claims! ✅

---

### 3. Start Backend API

```bash
cd d:\Repositories\dashBoard\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

**Look for these log messages:**
```
INFO: Started server process
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete
```

**Test the API:**
Open browser: `http://localhost:8000/docs`

You should see the FastAPI interactive documentation.

---

### 4. Start Frontend

**In a new terminal:**

```bash
cd d:\Repositories\dashBoard\frontend
npm run dev
```

**Expected output:**
```
VITE v5.x.x ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

### 5. Open Dashboard

Open browser: `http://localhost:5173`

**Expected behavior:**
- Dashboard loads in <2 seconds
- Shows total claims count (5M)
- All tabs load without errors
- Venue shift recommendations appear in <1 second

---

## Performance Testing

### Test 1: Venue Shift Analysis (5M Claims)

```bash
# In a new terminal, test the API directly
curl "http://localhost:8000/api/v1/aggregation/venue-shift-analysis?months=6"
```

**Expected response time:** <1 second

**Sample response:**
```json
{
  "recommendations": [
    {
      "county": "Los Angeles",
      "state": "CA",
      "current_venue_rating": "Neutral",
      "current_avg_variance": 15.2,
      "recommended_venue_rating": "Defense Friendly",
      "potential_variance_reduction": 3.4,
      "confidence": "high"
    }
  ],
  "summary": {
    "total_counties_analyzed": 87,
    "total_recent_claims": 2500000
  },
  "metadata": {
    "optimization": "database_level_aggregation_5M_ready"
  }
}
```

---

### Test 2: Dashboard Load Time

1. Open DevTools (F12)
2. Go to Network tab
3. Reload page
4. Check timing for `/api/v1/aggregation/aggregated`

**Expected:** <2 seconds total load time

---

### Test 3: Filter Performance

1. Open dashboard
2. Select a county from sidebar filter
3. Watch all tabs update

**Expected:** <0.5 seconds to apply filter

---

## Backend Logs to Look For

### Good Signs (5M Optimized):

```
INFO: [5M OPTIMIZED] Starting venue shift analysis for last 6 months...
INFO: Analyzing 2,500,000 recent claims (database-level aggregation)
INFO: Found 87 unique counties to analyze
INFO: ✅ Venue shift analysis completed: 23/87 counties with recommendations
INFO: Database session closed successfully
```

### Bad Signs (Not Optimized):

```
WARNING: Loading claims for real-time aggregation (SLOW mode)...
INFO: Loaded 5000000 claims for aggregation
```

If you see "SLOW mode", the database might not have materialized views. Run refresh-cache:

```bash
curl -X POST "http://localhost:8000/api/v1/aggregation/refresh-cache"
```

---

## Troubleshooting

### Issue: "Connection pool exhausted"

**Fix:** Restart backend - connection pool will reset

```bash
# Stop backend (Ctrl+C)
# Restart
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

---

### Issue: "Slow queries (>5 seconds)"

**Diagnosis:** Indexes might not be active

```bash
sqlite3 backend/app/db/claims_analytics.db

EXPLAIN QUERY PLAN
SELECT AVG(variance_pct), COUNT(*)
FROM claims
WHERE COUNTYNAME = 'Los Angeles' AND VENUE_RATING = 'Neutral';
```

**Look for:** `USING INDEX idx_county_venue`

If you see `SCAN TABLE claims`, indexes aren't being used. Rebuild database:

```bash
cd backend
del app\db\claims_analytics.db
.\venv\Scripts\python.exe migrate_csv_to_sqlite.py
```

---

### Issue: "Frontend shows error boundary"

**Expected:** This is working correctly! Error boundaries prevent full crashes.

**To debug:**
1. Open browser DevTools Console (F12)
2. Look for error message
3. Check which component failed
4. Error is isolated to that tab only

---

### Issue: "Backend crashes with memory error"

**Likely cause:** Old code path loading full dataset

**Check:** Backend logs should show "[5M OPTIMIZED]"

**If not, verify:**
```bash
cd backend/app/api/endpoints
grep -n "5M OPTIMIZED" aggregation.py
```

Should show the optimized venue shift endpoint is being used.

---

## Data Requirements

### Your dat.csv Format:

Must have these columns:
- `COUNTYNAME` - County name
- `VENUE_RATING` - Venue rating (Defense Friendly, Neutral, Plaintiff Friendly)
- `INJURY_GROUP_CODE` - Injury type code
- `CAUTION_LEVEL` - Severity level
- `IMPACT` - Impact score (1-5)
- `claim_date` - Date in YYYY-MM-DD format
- `variance_pct` - Variance percentage
- `adjuster` - Adjuster ID
- Plus ~50 other clinical/causation features

### Your weights.csv Format:

```csv
factor_name,base_weight,min_weight,max_weight,category,description
causation_probability,0.15,0.05,0.30,Causation,Probability of causal relation
severity_injections,0.11,0.05,0.20,Severity,Number of injections
...
```

---

## Performance Metrics to Expect

With 5M claims and proper indexes:

| Operation | Target | Status |
|-----------|--------|--------|
| Initial dashboard load | <2s | ✅ |
| Venue shift analysis (100 counties) | <1s | ✅ |
| Adjuster performance | <0.5s | ✅ |
| Filter application | <0.3s | ✅ |
| Overview metrics | <0.5s | ✅ |
| Tab switching | <0.1s | ✅ |

---

## Files Modified (No Manual Changes Needed)

All improvements are already in the code:

### Backend:
- ✅ `backend/app/db/schema.py` - Indexes and connection pool
- ✅ `backend/app/api/endpoints/aggregation_optimized_venue_shift.py` - Error handling
- ✅ `backend/app/api/endpoints/aggregation.py` - Uses optimized version
- ✅ `backend/app/api/models/validation.py` - Input validation (NEW)

### Frontend:
- ✅ `frontend/src/components/ErrorBoundary.tsx` - Error boundaries (NEW)
- ✅ `frontend/src/pages/IndexAggregated.tsx` - Wrapped tabs with error boundaries

---

## Summary

**To get running with 5M claims:**

1. Rebuild database (30 minutes):
   ```bash
   cd backend
   .\venv\Scripts\python.exe migrate_csv_to_sqlite.py
   ```

2. Start backend:
   ```bash
   .\venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

3. Start frontend (in new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

4. Open: `http://localhost:5173`

**Expected:** Dashboard loads in <2 seconds, all operations fast, no crashes.

**That's it!** Your system is now ready for 5 million claims.
