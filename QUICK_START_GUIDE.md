# Quick Start Guide - Testing Your Dashboard

## ✅ Your Dashboard is Ready!

All code has been updated to work with the 80-column data structure. Here's how to test it:

---

## Step 1: Start Backend

Open **Terminal 1** (Git Bash or Command Prompt):

```bash
cd d:/Repositories/dashBoard/backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify backend is working:**
- Open browser: http://localhost:8000/docs
- You should see FastAPI Swagger docs

---

## Step 2: Test Backend API

**Test 1: Get Claims**
```
http://localhost:8000/api/v1/claims/claims/full
```
✅ Should return JSON array with 1000 claims

**Test 2: Get Aggregations**
```
http://localhost:8000/api/v1/aggregated?use_fast=false
```
✅ Should return JSON with:
- `yearSeverity`
- `countyYear`
- `injuryGroup`
- `adjusterPerformance`
- `venueAnalysis`
- `varianceDrivers` ← **This is what Recommendations tab needs!**

---

## Step 3: Start Frontend

Open **Terminal 2**:

```bash
cd d:/Repositories/dashBoard/frontend
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

## Step 4: Open Dashboard

**Browser:** http://localhost:5173

You should see:
- ✅ **Overview tab** - Loads with graphs
- ✅ **Recommendations tab** - Shows variance drivers and recommendations
- ✅ **Injury Analysis tab** - Shows injury distribution
- ✅ **Adjuster Performance tab** - Shows adjuster metrics
- ✅ **Weight Recalibration tab** - Shows weight adjustment UI

---

## Step 5: Test Recommendations Tab

**What you should see:**

### 1. Variance Drivers Chart
Shows top factors contributing to variance:
- Factor names (e.g., "AGE", "DOLLARAMOUNTHIGH", "IOL")
- Contribution scores
- Color-coded by strength (Strong/Moderate/Weak)

### 2. Venue Shift Recommendations
Shows counties where changing venue rating could reduce variance:
- County name + State
- Current venue rating
- Recommended venue rating
- Potential variance reduction %
- Confidence level

### 3. High Variance Alerts
Lists areas with concerning variance levels

---

## 🐛 Troubleshooting

### Issue: Recommendations Tab is Empty

**Possible causes:**

#### 1. Backend not returning varianceDrivers

**Check:**
```bash
curl "http://localhost:8000/api/v1/aggregated?use_fast=false" | grep varianceDrivers
```

**Expected:** Should see `"varianceDrivers":[...]`

**Fix if missing:** Backend aggregation.py already has the code (line 236), just restart backend

#### 2. Frontend not loading aggregated data

**Check browser console (F12):**
- Look for network errors
- Check if API call to `/api/v1/aggregated` succeeds

**Fix:** Verify frontend is calling the right endpoint in `useAggregatedClaimsData.ts`

#### 3. No variance_pct in database

**Check:**
```bash
cd backend
./venv/Scripts/python.exe -c "
import pandas as pd
from app.db.schema import get_engine
engine = get_engine()
df = pd.read_sql_query('SELECT variance_pct FROM claims LIMIT 5', engine)
print(df)
"
```

**Expected:** Should show 5 rows with variance_pct values

**Fix if missing:** Reload database:
```bash
./venv/Scripts/python.exe load_csv_to_database.py
```

#### 4. Venue shift analysis endpoint missing

**Check:**
```bash
curl "http://localhost:8000/api/v1/aggregation/venue-shift-analysis?months=6"
```

**Expected:** JSON with venue shift recommendations

**Fix:** This endpoint might not exist yet. It's optional - recommendations will still show variance drivers without it.

---

## 📊 What Each Tab Should Show

### Overview Tab
- Year-Severity chart (bar chart by year and severity level)
- County distribution
- KPI cards (total claims, avg variance, etc.)

### Recommendations Tab (Was Empty Before)
- **Variance Drivers Chart** - Top 15 factors affecting variance
- **Venue Shift Recommendations** - Counties where venue change would help
- **High Variance Alerts** - Problem areas to investigate

### Injury Analysis Tab
- Injury group distribution
- Settlement by injury type
- Body region analysis

### Adjuster Performance Tab
- Adjuster metrics table
- Variance by adjuster
- Claims handled per adjuster

### Weight Recalibration Tab
- Weight adjustment sliders
- Recalibration metrics
- Before/After comparison

---

## 🎯 Quick Verification Checklist

- [ ] Backend starts without errors
- [ ] `/api/v1/claims/claims/full` returns 1000 claims
- [ ] `/api/v1/aggregated` returns data with `varianceDrivers` array
- [ ] Frontend starts without errors
- [ ] Dashboard opens in browser
- [ ] Overview tab shows graphs
- [ ] **Recommendations tab shows variance drivers chart** ← This was your issue
- [ ] Filters work (Year, Injury Group, County)
- [ ] No console errors in browser (F12)

---

## 💡 Understanding Variance Drivers

**What are variance drivers?**
Factors that correlate with prediction variance (accuracy).

**Example:**
```json
{
  "factor_name": "AGE",
  "contribution_score": 12.5,
  "correlation_strength": "Moderate"
}
```

This means: AGE has a 12.5% contribution to variance - older/younger claimants may have less accurate predictions.

**Why it's useful:**
- Identifies which factors need better modeling
- Shows where prediction model struggles
- Guides weight recalibration decisions

---

## 🚀 Next Steps After Verification

### If Everything Works:
1. Test filters - verify graphs update
2. Try recalibration tab - adjust weights
3. Export CSV - test data export
4. Review all tabs for data accuracy

### If Recommendations Tab Still Empty:
1. Check browser console for errors
2. Verify API response includes `varianceDrivers`
3. Check network tab (F12) for failed requests
4. Share error message for debugging

### For Large Dataset (850K records):
1. See [LARGE_DATASET_OPTIMIZATION.md](LARGE_DATASET_OPTIMIZATION.md)
2. Implement pagination
3. Use materialized views
4. Add database indexes

---

## 📞 Need Help?

**Common Error Messages:**

### "Failed to fetch aggregated data"
- **Cause:** Backend not running
- **Fix:** Start backend (Step 1)

### "varianceDrivers is undefined"
- **Cause:** Backend not calculating variance drivers
- **Fix:** Check variance_pct in database, reload if needed

### "Network Error"
- **Cause:** Port conflict or firewall
- **Fix:** Check if ports 8000 (backend) and 5173 (frontend) are available

### Browser shows blank page
- **Cause:** Frontend build error
- **Fix:** Check terminal for errors, run `npm install` if needed

---

## ✅ Success Criteria

Your dashboard is working correctly when:

1. ✅ Backend API returns data
2. ✅ Frontend loads without errors
3. ✅ All tabs display content
4. ✅ **Recommendations tab shows variance drivers**
5. ✅ Filters update graphs
6. ✅ No console errors

---

**Your system is configured and ready. Follow steps 1-5 above to start testing!**

