# 🚀 How to Run Backend and Frontend (5M Optimized Version)

## Quick Start (Both Backend + Frontend)

### Step 1: Setup Backend

```bash
# Navigate to backend
cd d:\Repositories\dashBoard\backend

# Install dependencies (if not already done)
pip install -r requirements.txt

# If you have existing data, refresh materialized views
python -c "from app.db.materialized_views import create_all_materialized_views, refresh_all_materialized_views; create_all_materialized_views(); refresh_all_materialized_views()"

# OR if starting fresh with CSV files
python migrate_csv_to_sqlite.py
```

### Step 2: Start Backend Server

```bash
# Still in backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
INFO:     ✓ Materialized views active - Ready for 5M+ record performance
```

### Step 3: Setup Frontend (New Terminal)

```bash
# Open NEW terminal/command prompt
cd d:\Repositories\dashBoard\frontend

# Install dependencies (if not already done)
npm install

# Start frontend dev server
npm run dev
```

**Expected output:**
```
VITE v4.x.x  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### Step 4: Open Browser

Open: **http://localhost:5173**

You should see the dashboard load in **<2 seconds** even with 5M records!

---

## Detailed Instructions

### Backend Setup (First Time)

```bash
# 1. Navigate to backend
cd d:\Repositories\dashBoard\backend

# 2. Create virtual environment (recommended)
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Check if you have data
dir data\dat.csv
dir data\weights.csv

# 6. If CSV files exist, run migration
python migrate_csv_to_sqlite.py
```

**Migration Output:**
```
======================================================================
CSV to SQLite Migration Script
======================================================================

[1/4] Migrating weights...
✓ Successfully migrated 150 weights

[2/4] Migrating claims (this may take a while for large files)...
Processing claims: 100% ████████████████ 5,000,000/5,000,000
✓ Successfully migrated 5,000,000 claims

[3/4] Optimizing database...
✓ Database indexes created and analyzed

[4/4] Creating materialized views for fast aggregation...
✓ Materialized views ready for 5M+ record performance

======================================================================
✓ Migration completed successfully!
======================================================================

Database Statistics:
  - Claims: 5,000,000
  - Weights: 150
  - Database location: d:\Repositories\dashBoard\backend\app\db\claims_analytics.db

Performance Optimization:
  - Materialized views: ✓ Created
  - Expected API response time: <1 second
  - Ready for 5M+ records
```

### Start Backend Server

```bash
# Make sure you're in backend directory
cd d:\Repositories\dashBoard\backend

# Activate virtual environment if you created one
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Alternative (using main.py):**
```bash
python app/main.py
```

**Server Logs:**
```
INFO:     Will watch for changes in these directories: ['D:\\Repositories\\dashBoard\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:     Starting StyleLeap Claims Analytics API
INFO:     API docs available at: /api/v1/docs
INFO:     Data directory: D:\Repositories\dashBoard\backend\data
INFO:     ✓ Materialized views active - Ready for 5M+ record performance
INFO:     Application startup complete.
```

✅ **Backend is ready when you see:** `✓ Materialized views active`

### Frontend Setup (First Time)

```bash
# Open NEW terminal (keep backend running)
cd d:\Repositories\dashBoard\frontend

# Install Node.js dependencies
npm install

# If you get errors, try:
npm install --legacy-peer-deps
```

### Start Frontend Server

```bash
# Make sure you're in frontend directory
cd d:\Repositories\dashBoard\frontend

# Start development server
npm run dev

# Or if using Vite with specific port
npm run dev -- --port 5173
```

**Frontend Server Output:**
```
  VITE v4.5.0  ready in 523 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/
  ➜  press h to show help
```

✅ **Frontend is ready!** Open http://localhost:5173

---

## Testing the Optimizations

### 1. Test Backend API Directly

**Open new terminal:**
```bash
# Test health check
curl http://localhost:8000/health

# Test cache status
curl http://localhost:8000/api/v1/aggregation/cache-status

# Test aggregated data (should be fast)
curl "http://localhost:8000/api/v1/aggregation/aggregated" -w "\nTime: %{time_total}s\n"
```

**Expected result:** Response time <1 second

### 2. Run Test Suite

```bash
cd d:\Repositories\dashBoard\backend
python test_materialized_views.py
```

**Expected output:**
```
MATERIALIZED VIEWS TEST SUITE
======================================================================

[1/5] Checking database...
✓ Found 5,000,000 claims in database

[2/5] Checking if materialized views exist...
✓ Materialized views already exist

[3/5] Testing view refresh...
✓ Views refreshed successfully in 15.23 seconds

[4/5] Getting view statistics...
View Statistics:
----------------------------------------------------------------------
  mv_year_severity               75 rows
  mv_county_year              1,523 rows
  mv_injury_group               234 rows
  mv_adjuster_performance        89 rows
  mv_venue_analysis             420 rows
----------------------------------------------------------------------
  COMPRESSION RATIO           2,137x

[5/5] Testing query performance...
  Fast Query: 0.5 ms
  Slow Query: 450 ms
  Performance Improvement: 900x faster

✓ ALL TESTS PASSED
```

### 3. Test Frontend Dashboard

1. **Open browser:** http://localhost:5173
2. **Navigate to Overview tab** (should be default)
3. **Check load time:** Should be <2 seconds
4. **Apply filters:** Should respond instantly
5. **Check KPI cards:** Should show correct numbers

---

## Common Issues & Solutions

### Issue 1: Backend - "Materialized views not found"

**Solution:**
```bash
cd backend
python -c "from app.db.materialized_views import create_all_materialized_views, refresh_all_materialized_views; create_all_materialized_views(); refresh_all_materialized_views()"
```

### Issue 2: Backend - Port 8000 already in use

**Solution:**
```bash
# Use different port
python -m uvicorn app.main:app --reload --port 8001

# Update frontend API URL in: frontend/.env or frontend/src/api/claimsAPI.ts
# Change: http://localhost:8000 → http://localhost:8001
```

### Issue 3: Frontend - API connection error

**Check:**
1. Backend is running: http://localhost:8000/health
2. CORS is enabled (should be automatic)
3. Frontend .env file has correct API URL

**Fix frontend API URL:**
```bash
# Check file: frontend/src/api/claimsAPI.ts
# Look for:
const API_BASE_URL = 'http://localhost:8000/api/v1'
```

### Issue 4: Frontend - npm install fails

**Solution:**
```bash
# Clear cache and retry
npm cache clean --force
npm install --legacy-peer-deps
```

### Issue 5: Database file not found

**Solution:**
```bash
cd backend
python migrate_csv_to_sqlite.py
```

### Issue 6: Slow API responses (still 30+ seconds)

**Check if materialized views are populated:**
```bash
curl http://localhost:8000/api/v1/aggregation/cache-status
```

**If views are empty, refresh them:**
```bash
curl -X POST http://localhost:8000/api/v1/aggregation/refresh-cache
```

---

## Production Deployment

### Backend (Production Mode)

```bash
cd backend

# Install production server
pip install gunicorn

# Run with Gunicorn (Linux/Mac)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# Or use Uvicorn directly (Windows/Linux/Mac)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend (Production Build)

```bash
cd frontend

# Build for production
npm run build

# Output will be in: frontend/dist

# Serve with any static server, e.g.:
npx serve dist -p 3000
```

---

## Environment Variables

### Backend (.env file)

Create `backend/.env`:
```env
# Optional - defaults are fine for most cases
DEBUG=False
PROJECT_NAME="Claims Analytics API"
API_V1_STR="/api/v1"
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

### Frontend (.env file)

Create `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## Quick Commands Cheat Sheet

### Backend

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload

# Refresh cache
curl -X POST http://localhost:8000/api/v1/aggregation/refresh-cache

# Check status
curl http://localhost:8000/api/v1/aggregation/cache-status

# Run tests
python test_materialized_views.py

# Run migration
python migrate_csv_to_sqlite.py
```

### Frontend

```bash
# Start frontend
cd frontend
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Both (Open 2 Terminals)

**Terminal 1 (Backend):**
```bash
cd d:\Repositories\dashBoard\backend
python -m uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd d:\Repositories\dashBoard\frontend
npm run dev
```

**Browser:**
```
http://localhost:5173
```

---

## File Locations

### Backend
- **Main app:** `backend/app/main.py`
- **Database:** `backend/app/db/claims_analytics.db` (auto-created)
- **Materialized views:** `backend/app/db/materialized_views.py`
- **API endpoints:** `backend/app/api/endpoints/`
- **Data files:** `backend/data/dat.csv`, `backend/data/weights.csv`

### Frontend
- **Main app:** `frontend/src/main.tsx`
- **Pages:** `frontend/src/pages/`
- **Components:** `frontend/src/components/`
- **API config:** `frontend/src/api/claimsAPI.ts`
- **Hooks:** `frontend/src/hooks/`

---

## Verification Checklist

✅ Backend running at http://localhost:8000
✅ Backend logs show: "✓ Materialized views active"
✅ API responds in <1s: `curl http://localhost:8000/api/v1/aggregation/aggregated`
✅ Cache status is active: `curl http://localhost:8000/api/v1/aggregation/cache-status`
✅ Frontend running at http://localhost:5173
✅ Dashboard loads in <2 seconds
✅ Filters work instantly
✅ KPIs show correct values

---

## Performance Monitoring

### Check API Response Time

```bash
# Using curl
curl -w "\nTotal time: %{time_total}s\n" http://localhost:8000/api/v1/aggregation/aggregated

# Expected: <1 second for 5M records
```

### Monitor Backend Logs

Backend logs will show:
```
INFO:     Retrieved aggregated data from materialized views (FAST)
INFO:     Returned aggregated data for 5,000,000 claims
```

If you see this, views are working! ✅

### Check Browser Network Tab

1. Open browser DevTools (F12)
2. Go to Network tab
3. Refresh dashboard
4. Check `/aggregation/aggregated` request
5. Should complete in <1 second

---

## 🎉 Success Indicators

When everything is working correctly:

✅ Backend starts with: `✓ Materialized views active - Ready for 5M+ record performance`
✅ API responds in <1 second
✅ Dashboard loads completely in <2 seconds
✅ Filters apply instantly
✅ No browser console errors
✅ Memory usage is low (<500MB for backend, <200MB for frontend)

**Your optimized dashboard is now running!** 🚀

---

## Need Help?

1. **Check logs** in both backend and frontend terminals
2. **Run test suite:** `python test_materialized_views.py`
3. **Verify cache:** `curl http://localhost:8000/api/v1/aggregation/cache-status`
4. **Re-run migration:** `python migrate_csv_to_sqlite.py`
5. **Check this guide:** [PERFORMANCE_OPTIMIZATION_GUIDE.md](backend/PERFORMANCE_OPTIMIZATION_GUIDE.md)
