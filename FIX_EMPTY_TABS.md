# Fix Empty Dashboard Tabs

## 🔴 Problem: Recommendations & Weight Recalibration Tabs are Empty

Both tabs are empty because **the backend server is not running**. The tabs need data from the API.

---

## ✅ Solution: Start the Backend

### Step 1: Open Terminal
Open Git Bash or Command Prompt

### Step 2: Navigate to Backend
```bash
cd d:/Repositories/dashBoard/backend
```

### Step 3: Start Backend Server
```bash
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
INFO:     Started server process [xxxxx]
INFO:     Application startup complete.
```

**Keep this terminal open!** Backend must stay running.

---

## 🔍 What Each Tab Needs

### Recommendations Tab

**Needs:**
- `/api/v1/aggregated` - Returns `varianceDrivers` array
- `/api/v1/aggregation/venue-shift-analysis` (optional)

**What it shows:**
- Variance Drivers Chart (top factors affecting predictions)
- Venue Shift Recommendations
- High Variance Alerts

### Weight Recalibration Tab

**Needs:**
1. `/api/v1/claims/claims/full` - Raw claims data (loads when tab is clicked)
2. Weights data from either:
   - `/api/recalibration/weights/data` (backend API)
   - OR `/weights_summary.csv` (frontend public folder)

**What it shows:**
- Weight adjustment sliders
- Before/After metrics
- Recalibration results
- Factor impact analysis
- Optimization recommendations

---

## 📊 How Data Loading Works

### When You Open the Dashboard:

**1. Overview, Injury, Adjuster Tabs (Fast)**
```
Frontend → /api/v1/aggregated → Aggregated data → Display immediately
```
✅ Uses pre-aggregated data (fast even for 850K records)

**2. Recommendations Tab (Fast)**
```
Frontend → /api/v1/aggregated → varianceDrivers → Display chart
```
✅ Same aggregated endpoint

**3. Weight Recalibration Tab (Slower - Lazy Loaded)**
```
User clicks tab → Frontend → /api/v1/claims/claims/full → Load 1000 claims
                        → Load weights_summary.csv
                        → Display recalibration UI
```
⚠️ Loads raw claims (only when needed)

---

## 🧪 Verify Backend is Working

### Test 1: Check Backend is Running
Open browser: http://localhost:8000/docs

**Expected:** FastAPI Swagger documentation page

**If fails:** Backend is not running - go back to Step 3 above

---

### Test 2: Check Aggregated Data
Open browser: http://localhost:8000/api/v1/aggregated?use_fast=false

**Expected:** JSON like:
```json
{
  "yearSeverity": [...],
  "countyYear": [...],
  "injuryGroup": [...],
  "adjusterPerformance": [...],
  "venueAnalysis": [...],
  "varianceDrivers": [
    {
      "factor_name": "AGE",
      "contribution_score": 12.5,
      "correlation_strength": "Moderate"
    },
    ...
  ],
  "metadata": {...}
}
```

**If fails:**
- Backend error - check terminal for Python errors
- Database issue - reload data: `./venv/Scripts/python.exe load_csv_to_database.py`

---

### Test 3: Check Raw Claims Data
Open browser: http://localhost:8000/api/v1/claims/claims/full

**Expected:** JSON array with 1000 claims:
```json
[
  {
    "CLAIMID": 1,
    "CAUSATION_HIGH_RECOMMENDATION": 74802.05,
    "DOLLARAMOUNTHIGH": 59818,
    "PRIMARY_INJURYGROUP_CODE": "Soft Tissue",
    ...
  },
  ...
]
```

**If fails:**
- Check database has data
- Verify API endpoint exists
- Check for column name errors in backend logs

---

### Test 4: Check Weights Data
Open browser: http://localhost:8000/api/recalibration/weights/data

**Expected:** JSON array with weight configs:
```json
[
  {
    "factor_name": "Causation_Compliance",
    "base_weight": 2.4797,
    "min_weight": 0.0012,
    "max_weight": 4.9989,
    "category": "Causation",
    "description": "..."
  },
  ...
]
```

**If fails:**
- Endpoint may not exist (optional)
- Frontend will fallback to loading `/weights_summary.csv` from public folder
- Verify file exists: `frontend/public/weights_summary.csv`

---

## 🎯 Step-by-Step Verification

### After Starting Backend:

**1. Refresh Browser**
- Dashboard should now show data in Recommendations tab

**2. Click Weight Recalibration Tab**
- Should show "Loading raw claims..."
- Then display weight adjustment UI

**3. Check Browser Console (F12)**
- No red errors
- Network tab shows successful API calls

---

## 🐛 Common Issues & Fixes

### Issue 1: "Failed to fetch"

**Symptoms:** All tabs empty, console shows network errors

**Cause:** Backend not running

**Fix:**
```bash
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

---

### Issue 2: "varianceDrivers is undefined"

**Symptoms:** Recommendations tab empty, no chart

**Cause:** Backend not calculating variance drivers

**Fix:**
1. Check if `variance_pct` exists in database:
```bash
cd backend
./venv/Scripts/python.exe -c "
from app.db.schema import get_engine
import pandas as pd
engine = get_engine()
df = pd.read_sql_query('SELECT variance_pct FROM claims LIMIT 5', engine)
print(df)
"
```

2. If NULL or missing, reload database:
```bash
./venv/Scripts/python.exe load_csv_to_database.py
```

---

### Issue 3: Weight Recalibration tab shows "Loading..." forever

**Symptoms:** Tab stuck on loading, no error message

**Causes:**
1. Backend timeout (850K records taking too long)
2. API endpoint not returning data
3. Wrong API URL

**Fix:**

**For timeout issue:**
```python
# backend/app/services/data_service.py
# Add limit to prevent loading all 850K records
async def get_full_claims_data(self, limit: int = 5000):
    # Load max 5K claims for recalibration
    # (Sufficient for weight calibration)
```

**For API endpoint:**
- Verify: http://localhost:8000/api/v1/claims/claims/full
- Check backend logs for errors
- Verify data_service is returning correct format

---

### Issue 4: "Cannot read property 'base_weight' of undefined"

**Symptoms:** Weight Recalibration tab crashes

**Cause:** Weights data not loading

**Fix:**

**Option 1: Check weights_summary.csv exists**
```bash
ls -la frontend/public/weights_summary.csv
```

**If missing:**
```bash
cd backend
./venv/Scripts/python.exe create_weights_summary.py
cp data/weights_summary.csv ../frontend/public/weights_summary.csv
```

**Option 2: Check API endpoint**
http://localhost:8000/api/recalibration/weights/data

---

### Issue 5: Tabs work but show wrong data

**Symptoms:** Graphs show but values seem incorrect

**Cause:** Column name mismatch after migration

**Fix:**
1. Check browser console for errors
2. Verify backend is using correct column names:
   - `PRIMARY_INJURYGROUP_CODE` (not `INJURY_GROUP_CODE`)
   - `ADJUSTERNAME` (not `adjuster`)
   - `VENUERATING` (not `VENUE_RATING`)
   - `IOL` (not `IMPACT`)
   - `CLAIMCLOSEDDATE` (not `claim_date`)

3. If wrong columns, update backend code as needed

---

## 📋 Complete Startup Checklist

**Before Opening Dashboard:**

- [ ] Backend server running (`uvicorn` command)
- [ ] Backend accessible at http://localhost:8000
- [ ] Database file exists: `backend/app/db/claims_analytics.db`
- [ ] Database has data (1000 claims loaded)
- [ ] weights_summary.csv exists in `frontend/public/`

**After Opening Dashboard:**

- [ ] Overview tab shows graphs
- [ ] Recommendations tab shows variance drivers
- [ ] Injury Analysis tab shows injury data
- [ ] Adjuster Performance tab shows adjuster metrics
- [ ] Weight Recalibration tab loads and shows sliders
- [ ] No console errors (F12)
- [ ] Filters work and update graphs

---

## ⚡ Quick Start (TL;DR)

**1. Start Backend:**
```bash
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

**2. Wait for:** `Application startup complete`

**3. Open Frontend:** http://localhost:5173

**4. Check Tabs:**
- Recommendations tab → Should show variance drivers chart
- Weight Recalibration tab → Click it, wait 2-3 seconds, should show UI

**Done!** ✅

---

## 📞 Still Having Issues?

### Check This:

1. **Backend Terminal** - Any Python errors?
2. **Browser Console (F12)** - Any red errors?
3. **Network Tab (F12)** - Are API calls succeeding (status 200)?
4. **Backend Logs** - Any 500 errors or exceptions?

### Collect This Info:

- Backend terminal output (copy last 20 lines)
- Browser console errors (screenshot)
- Network tab showing failed request (screenshot)
- Which tab is empty

---

## 🎓 Understanding the Architecture

```
┌─────────────────┐
│   FRONTEND      │
│  (localhost:    │
│     5173)       │
└────────┬────────┘
         │
         │ HTTP Requests
         │
         ▼
┌─────────────────┐
│   BACKEND API   │ ← MUST BE RUNNING
│  (localhost:    │
│     8000)       │
└────────┬────────┘
         │
         │ SQL Queries
         │
         ▼
┌─────────────────┐
│   DATABASE      │
│  claims_        │
│  analytics.db   │
└─────────────────┘
```

**If Backend is not running:**
- ❌ Frontend can't get data
- ❌ All tabs that need API will be empty
- ❌ Console shows "Failed to fetch" errors

**When Backend is running:**
- ✅ Frontend gets data from API
- ✅ Tabs populate automatically
- ✅ Real-time updates work

---

**Your tabs are empty because backend is not running. Start backend and tabs will populate automatically!** 🚀

