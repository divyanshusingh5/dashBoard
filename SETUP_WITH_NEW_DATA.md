# Setup Guide for New Data - Complete Process

## When You Get New Data (dat.csv with more claims)

Follow these steps **in this exact order** to ensure everything works properly:

---

## Step 1: Kill All Running Servers ⚠️

You have multiple backend servers running which can cause port conflicts and confusion.

```bash
# Kill all Python/Uvicorn processes
taskkill //F //IM python.exe
```

**Wait 5 seconds** to ensure all processes are terminated.

---

## Step 2: Place New Data Files

Put your new CSV files in the backend directory:

```
D:\Repositories\dashBoard\backend\
  ├── dat.csv          ← Your new claims data (657K rows)
  └── SSNB.csv         ← SSNB data (if you have it)
```

---

## Step 3: Backup Old Database (Optional but Recommended)

```bash
cd backend
cp app/db/claims_analytics.db app/db/claims_analytics.db.backup_old_data
```

---

## Step 4: Migrate New Data

### Option A: Use Smart Migration (Recommended)

```bash
cd backend
./venv/Scripts/python.exe migrate_smart.py
```

**What it does:**
- Checks if data already exists
- Only migrates what's needed
- Handles duplicates automatically
- Much faster on re-runs

**Expected time:** 2-3 minutes for full migration

### Option B: Use Comprehensive Migration

```bash
cd backend
./venv/Scripts/python.exe migrate_comprehensive.py
```

**What it does:**
- Drops and recreates everything
- Migrates all data fresh
- Takes longer but ensures clean state

**Expected time:** 3-5 minutes for full migration

---

## Step 5: Create Materialized Views ✅ **MOST IMPORTANT!**

**This is the step you're asking about - YES, you must run this with new data!**

```bash
cd backend
./venv/Scripts/python.exe create_materialized_views.py
```

**What it does:**
- Creates pre-computed aggregation tables
- Makes `/aggregation/aggregated` endpoint FAST (sub-second)
- Required for Overview, Analysis, and other tabs to work
- **Without this, aggregation endpoints will timeout!**

**Expected output:**
```
Creating materialized views for fast aggregation...
✓ Created year_severity_summary view
✓ Created county_year_summary view
✓ Created injury_group_summary view
✓ Created adjuster_performance_summary view
✓ Created venue_analysis_summary view
✓ Created variance_driver_summary view
✓ Materialized views created successfully
```

**Expected time:** 30-60 seconds

---

## Step 6: Populate Venue Statistics (For Table-Based Recommendations)

```bash
cd backend
./venv/Scripts/python.exe populate_venue_statistics.py
```

**What it does:**
- Creates venue_statistics table with pre-computed statistics
- Required for fast venue shift recommendations
- Makes venue analysis 120x faster

**Expected time:** 4-5 minutes for 657K claims

---

## Step 7: Clear Python Cache

```bash
cd backend
powershell -Command "Get-ChildItem -Include __pycache__,*.pyc -Recurse -Force | Remove-Item -Force -Recurse"
```

---

## Step 8: Start Backend Server

```bash
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO: Starting StyleLeap Claims Analytics API
INFO: API docs available at: /api/v1/docs
INFO: ✓ Materialized views active - Ready for 5M+ record performance
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete.
```

**Leave this terminal window open!**

---

## Step 9: Test Backend Endpoints

Open a **new terminal** and test:

### Test 1: Aggregated Data
```bash
curl "http://localhost:8000/api/v1/aggregation/aggregated" | python -m json.tool | head -50
```

**Expected:** JSON data with yearSeverity, countyYear, etc.

### Test 2: Venue Shift Analysis
```bash
curl "http://localhost:8000/api/v1/aggregation/venue-shift-analysis?months=24" | python -m json.tool | head -50
```

**Expected:** JSON with venue shift recommendations

### Test 3: Health Check
```bash
curl "http://localhost:8000/health"
```

**Expected:** `{"status":"healthy"}`

---

## Step 10: Start Frontend

Open **another new terminal**:

```bash
cd frontend
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

## Step 11: Open Browser and Test

1. Go to: `http://localhost:5173/`
2. Wait for data to load (should be <1 second)
3. You should see:
   - ✅ Overview tab with KPI cards and charts
   - ✅ 5 tabs total (no Recalibration tab - we disabled it)
   - ✅ All data loading instantly

---

## Common Issues and Fixes

### Issue 1: "timeout of 60000ms exceeded"

**Cause:** Materialized views not created

**Fix:**
```bash
cd backend
./venv/Scripts/python.exe create_materialized_views.py
```

Then restart backend server.

### Issue 2: "Failed to fetch" or CORS errors

**Cause:** Backend not running or wrong port

**Fix:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not running, start it
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Issue 3: "Address already in use" when starting backend

**Cause:** Multiple backend servers running

**Fix:**
```bash
# Kill all Python processes
taskkill //F //IM python.exe

# Wait 5 seconds, then start fresh
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Issue 4: Backend shows "Loaded 657K data" but frontend still times out

**Cause:** Materialized views missing or corrupt

**Fix:**
```bash
# Recreate materialized views
cd backend
./venv/Scripts/python.exe create_materialized_views.py

# Verify they exist
./venv/Scripts/python.exe -c "import sqlite3; conn = sqlite3.connect('app/db/claims_analytics.db'); tables = [t[0] for t in conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall()]; print('Materialized views:', [t for t in tables if '_summary' in t])"
```

**Expected output:**
```
Materialized views: ['year_severity_summary', 'county_year_summary', 'injury_group_summary', 'adjuster_performance_summary', 'venue_analysis_summary', 'variance_driver_summary']
```

### Issue 5: Frontend shows old data count

**Cause:** Frontend caching or backend showing wrong count

**Fix:**
```bash
# Check actual database count
cd backend
./venv/Scripts/python.exe -c "import sqlite3; conn = sqlite3.connect('app/db/claims_analytics.db'); print('Total claims:', conn.execute('SELECT COUNT(*) FROM claims').fetchone()[0])"

# Hard refresh browser: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)
```

---

## Complete Setup Checklist

When setting up with new data, check these boxes:

- [ ] Step 1: Kill all running servers (`taskkill //F //IM python.exe`)
- [ ] Step 2: Place new dat.csv in backend/
- [ ] Step 3: Backup old database (optional)
- [ ] Step 4: Run migration (`migrate_smart.py` or `migrate_comprehensive.py`)
- [ ] Step 5: **Create materialized views** (`create_materialized_views.py`) ⚠️ CRITICAL
- [ ] Step 6: Populate venue statistics (`populate_venue_statistics.py`)
- [ ] Step 7: Clear Python cache
- [ ] Step 8: Start backend server (port 8000)
- [ ] Step 9: Test backend endpoints (curl)
- [ ] Step 10: Start frontend (port 5173)
- [ ] Step 11: Test in browser

---

## Quick Commands Summary

```bash
# Complete setup from scratch (copy-paste all these)
cd backend

# 1. Kill old servers
taskkill //F //IM python.exe
sleep 5

# 2. Migrate data
./venv/Scripts/python.exe migrate_smart.py

# 3. Create materialized views (CRITICAL!)
./venv/Scripts/python.exe create_materialized_views.py

# 4. Populate venue statistics
./venv/Scripts/python.exe populate_venue_statistics.py

# 5. Clear cache
powershell -Command "Get-ChildItem -Include __pycache__,*.pyc -Recurse -Force | Remove-Item -Force -Recurse"

# 6. Start backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then in a **new terminal**:
```bash
cd frontend
npm run dev
```

---

## Why Materialized Views Are Critical

**Without materialized views:**
- `/aggregation/aggregated` endpoint has to calculate everything on-the-fly
- For 657K claims, this takes 60+ seconds
- Frontend times out waiting for data
- UI shows error: "timeout of 60000ms exceeded"

**With materialized views:**
- Pre-computed summary tables store aggregated data
- `/aggregation/aggregated` just reads from these tables
- Response time: <1 second
- UI loads instantly ✅

**When to recreate materialized views:**
1. After migrating new data ✅
2. When data changes significantly
3. When adding new columns
4. When aggregation endpoints timeout

---

## Summary

**Your Question:** "should i 1st run create materialized views.py or what?"

**Answer:** YES! After migrating new data, you MUST run:

1. `migrate_smart.py` (or `migrate_comprehensive.py`)
2. **`create_materialized_views.py`** ← THIS IS CRITICAL
3. `populate_venue_statistics.py` (for venue recommendations)
4. Start backend server
5. Start frontend

If you skip step 2 (create_materialized_views.py), the aggregation endpoints will timeout and your UI won't load data.

**The timeout error you're seeing is almost certainly because materialized views don't exist for your new data!**
