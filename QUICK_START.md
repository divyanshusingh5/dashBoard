# Quick Start Guide

## 🚀 How to Run the Dashboard

### System Status
✅ **Backend:** Running on http://localhost:8000
✅ **Frontend:** Running on http://localhost:5180
✅ **Database:** SQLite with 1,000 claims loaded

---

## 📋 Prerequisites

- Python 3.8+ installed
- Node.js 18+ installed
- Data files: `dat.csv` and `weights.csv` in `backend/data/`

---

## ⚡ Step-by-Step Instructions

### 1️⃣ Start Backend (First Terminal)

```bash
# Navigate to backend folder
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Start server
python run.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Application startup complete.
```

**Verify Backend:**
```bash
# Check health
curl http://localhost:8000/health

# Expected: {"status":"healthy","service":"StyleLeap Claims Analytics API"}
```

---

### 2️⃣ Start Frontend (Second Terminal)

```bash
# Navigate to frontend folder
cd frontend

# Start development server
npm run dev
```

**Expected Output:**
```
VITE v5.4.21  ready in 2756 ms

➜  Local:   http://localhost:5180/
```

---

### 3️⃣ Open Dashboard

Open your browser and navigate to:

**http://localhost:5180**

You should see:
- ✅ Dashboard loads within 2 seconds
- ✅ Data displays correctly
- ✅ All tabs work (Overview, Recommendations, Injury Analysis, etc.)
- ✅ No console errors

---

## 🔧 First-Time Setup

If this is your first time running the dashboard:

### 1. Install Backend Dependencies
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Migrate Data to Database
```bash
# Make sure dat.csv and weights.csv are in backend/data/
python migrate_csv_to_sqlite.py
```

**Expected Output:**
```
✓ Migrating dat.csv to SQLite...
✓ Migrated 1,000 claims
✓ Migrated 51 weights
✓ Database created: claims_analytics.db
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
```

---

## 🌐 Available URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend Dashboard** | http://localhost:5180 | Main application |
| **Backend API** | http://localhost:8000 | REST API |
| **API Documentation** | http://localhost:8000/api/v1/docs | Interactive API docs |
| **Health Check** | http://localhost:8000/health | Server health status |
| **ReDoc** | http://localhost:8000/api/v1/redoc | Alternative API docs |

---

## 📊 Test the System

### Test 1: Backend Health
```bash
curl http://localhost:8000/health
```
✅ Expected: `{"status":"healthy",...}`

### Test 2: Get Aggregated Data
```bash
curl http://localhost:8000/api/v1/aggregation/aggregated
```
✅ Expected: JSON with `yearSeverity`, `countyYear`, etc.

### Test 3: Recent Performance Analysis
```bash
curl http://localhost:8000/api/v1/recalibration/recent-performance?months=12
```
✅ Expected: JSON with performance metrics

### Test 4: Frontend Access
Open http://localhost:5180 in browser
✅ Expected: Dashboard loads and displays data

---

## 🐛 Troubleshooting

### Problem: Backend won't start

**Error:** "Port 8000 already in use"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Error:** "No module named 'app'"
```bash
# Make sure you're in the backend directory
cd backend
python run.py
```

---

### Problem: Frontend won't start

**Error:** "Port 5180 already in use"
```bash
# Frontend will automatically try the next available port
# Just use the port shown in the terminal output
```

**Error:** "Module not found"
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

### Problem: Dashboard shows "Error loading data"

**Solution 1:** Check backend is running
```bash
curl http://localhost:8000/health
```

**Solution 2:** Check database has data
```bash
cd backend
python -c "
from app.services.data_service_sqlite import data_service_sqlite
import asyncio
claims = asyncio.run(data_service_sqlite.get_full_claims_data())
print(f'Claims loaded: {len(claims)}')
"
```

**Solution 3:** Re-run migration
```bash
cd backend
python migrate_csv_to_sqlite.py
```

---

### Problem: "No claims data available"

**Root Cause:** Database not populated

**Solution:**
```bash
cd backend

# Check if CSV files exist
dir data\dat.csv
dir data\weights.csv

# If missing, copy your CSV files to backend/data/
# Then run migration
python migrate_csv_to_sqlite.py
```

---

## 🎯 What You Can Do

### 1. View Dashboard Analytics
- **Overview Tab:** KPIs, trends, variance analysis
- **Recommendations Tab:** Top variance drivers, bad combinations
- **Injury Analysis Tab:** Statistics by injury type
- **Adjuster Performance Tab:** Adjuster rankings and metrics
- **Model Performance Tab:** Prediction accuracy charts

### 2. Recalibrate Weights
- Navigate to **Recalibration Tab**
- Adjust weight values with sliders
- Click **Recalibrate** to see new metrics
- Compare before/after performance

### 3. Use Enhanced Features (API)
```bash
# Get statistical analysis
curl -X POST http://localhost:8000/api/v1/recalibration/analyze-statistics \
  -H "Content-Type: application/json" \
  -d '{"weight_column": "SEVERITY_SCORE"}'

# Find similar cases
curl -X POST http://localhost:8000/api/v1/recalibration/find-similar-cases \
  -H "Content-Type: application/json" \
  -d '{
    "target_claim": {
      "INJURY_GROUP_CODE": "HEAD",
      "SEVERITY_SCORE": 7
    }
  }'

# Get optimal weight suggestions
curl -X POST http://localhost:8000/api/v1/recalibration/suggest-optimal-weights \
  -H "Content-Type: application/json" \
  -d '{
    "current_weights": {
      "SEVERITY_SCORE": 0.25,
      "VENUE_RATING": 0.15
    },
    "focus_recent_data": true
  }'
```

---

## 📚 Learn More

- **Full Documentation:** [README.md](./README.md)
- **Migration Guide:** [MIGRATION_COMPLETE.md](./MIGRATION_COMPLETE.md)
- **Enhanced Features:** [ENHANCED_RECALIBRATION_COMPLETE.md](./ENHANCED_RECALIBRATION_COMPLETE.md)
- **API Docs:** http://localhost:8000/api/v1/docs

---

## 🛑 How to Stop

### Stop Frontend
Press `Ctrl+C` in the terminal running `npm run dev`

### Stop Backend
Press `Ctrl+C` in the terminal running `python run.py`

---

## 🔄 Daily Workflow

### Morning Startup
```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate
python run.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Evening Shutdown
```bash
# Press Ctrl+C in both terminals
```

---

## ✅ System Architecture

```
┌─────────────────────────────────────────┐
│         Your Browser                    │
│         http://localhost:5180           │
└──────────────┬──────────────────────────┘
               │ Fetch data via API
               ▼
┌─────────────────────────────────────────┐
│       FastAPI Backend                   │
│       http://localhost:8000             │
│  ├── REST API endpoints                 │
│  ├── Real-time aggregation              │
│  └── Statistical analysis               │
└──────────────┬──────────────────────────┘
               │ SQL queries
               ▼
┌─────────────────────────────────────────┐
│       SQLite Database                   │
│  backend/app/db/claims_analytics.db     │
│  ├── 1,000 claims                       │
│  └── 51 weight factors                  │
└─────────────────────────────────────────┘
               ▲
               │ One-time migration
┌──────────────┴──────────────────────────┐
│       CSV Files                         │
│  backend/data/                          │
│  ├── dat.csv                            │
│  └── weights.csv                        │
└─────────────────────────────────────────┘
```

---

## 🎉 You're Ready!

Your Claims Analytics Dashboard is fully operational:

✅ **Backend API:** Serving data at http://localhost:8000
✅ **Frontend UI:** Interactive dashboard at http://localhost:5180
✅ **Database:** 1,000 claims ready for analysis
✅ **Features:** Real-time aggregation, statistical analysis, weight optimization

**Start exploring your data!** 🚀

---

**Last Updated:** 2025-11-01
**Version:** 1.0.0
**Status:** Production Ready
