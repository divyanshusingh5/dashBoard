# How to Run the Project

## 🎯 Current Status: ALREADY RUNNING! ✅

Your dashboard is currently live at:
- **Dashboard**: http://localhost:5179
- **API Docs**: http://localhost:8000/api/v1/docs

---

## 🚀 Quick Start (If Not Running)

### Option 1: Quick Start (Recommended)

Open **2 terminal windows**:

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Option 2: One-Line Commands

**Start Backend:**
```bash
cd backend && venv\Scripts\python.exe run.py
```

**Start Frontend:**
```bash
cd frontend && npm run dev
```

---

## 📊 Current Setup (CSV-Based)

Your dashboard is currently using **CSV files** (the original setup):

```
frontend/public/
├── dat.csv (1,000 rows) → Loaded directly by browser
└── weights.csv (51 factors) → Used for recalibration

Backend reads these files when needed.
```

### Access URLs:
- **Frontend Dashboard**: http://localhost:5179
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health

---

## 🗄️ Optional: Switch to SQLite (For 2M+ Rows)

If you want better performance with large datasets:

### Step 1: Run Migration
```bash
cd backend
venv\Scripts\python.exe migrate_csv_to_sqlite.py
```

This creates `backend/app/db/claims_analytics.db` from your CSV files.

### Step 2: Update Backend Code

**File:** `backend/app/api/endpoints/claims.py`

**Change:**
```python
from app.services.data_service import data_service
```

**To:**
```python
from app.services.data_service_sqlite import data_service_sqlite as data_service
```

### Step 3: Restart Backend
```bash
# Kill current backend (Ctrl+C in terminal)
cd backend
venv\Scripts\python.exe run.py
```

**See [SQLITE_MIGRATION_GUIDE.md](SQLITE_MIGRATION_GUIDE.md) for details**

---

## 🛠️ Troubleshooting

### Frontend won't start
```bash
cd frontend
npm install  # Install dependencies
npm run dev
```

### Backend won't start
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt  # Install dependencies
python run.py
```

### Port already in use
```bash
# Find and kill process on port 8000 (backend)
netstat -ano | findstr :8000
taskkill //F //PID <PID_NUMBER>

# Find and kill process on port 5173 (frontend)
netstat -ano | findstr :5173
taskkill //F //PID <PID_NUMBER>
```

### Can't see data in dashboard
1. Check `frontend/public/dat.csv` exists
2. Check `frontend/public/weights.csv` exists
3. Refresh browser (Ctrl+F5)

---

## 📂 Project Structure

```
dashBoard/
├── frontend/               Frontend (React + Vite)
│   ├── public/
│   │   ├── dat.csv        ← Your claims data
│   │   └── weights.csv    ← Your weight factors
│   ├── src/
│   │   ├── components/    React components
│   │   ├── pages/         Dashboard pages
│   │   └── api/           API client
│   └── package.json
│
├── backend/               Backend (FastAPI + Python)
│   ├── app/
│   │   ├── api/           API endpoints
│   │   ├── services/      Data services
│   │   ├── core/          Configuration
│   │   └── db/            SQLite (optional)
│   ├── venv/              Python virtual environment
│   ├── run.py             Start backend
│   └── requirements.txt
│
└── Documentation/
    ├── HOW_TO_RUN.md              ← This file
    ├── SQLITE_MIGRATION_GUIDE.md   SQLite setup
    ├── ANALYSIS_FEATURES.md        What you get
    └── QUICK_START_SQLITE.md       Quick SQLite setup
```

---

## 📋 Common Tasks

### View Logs
```bash
# Backend logs
# Already visible in terminal

# Frontend logs
# Already visible in terminal
```

### Update Data
1. Replace `frontend/public/dat.csv` with new file
2. Refresh browser
3. (If using SQLite, re-run migration script)

### Update Weights
1. Edit `frontend/public/weights.csv`
2. Refresh dashboard
3. Go to "Weight Recalibration" tab
4. (If using SQLite, re-run migration script)

### Check API Endpoints
Visit: http://localhost:8000/api/v1/docs

Available endpoints:
- `/api/v1/claims/claims` - Get all claims
- `/api/v1/claims/aggregated` - Get aggregated data
- `/api/v1/claims/kpis` - Get KPIs
- `/api/v1/recalibration/recalibrate` - Recalibrate weights
- And more...

---

## 🎯 Dashboard Tabs

Once running, you can access:

1. **Overview** - Executive summary, KPIs, trends
2. **Recommendations** - High variance cases, suggestions
3. **Injury Analysis** - Injury breakdown, severity
4. **Adjuster Performance** - Adjuster rankings
5. **Model Performance** - Prediction accuracy
6. **Weight Recalibration** - Edit weights, optimize

---

## 🔧 Development

### Install New Dependencies

**Frontend:**
```bash
cd frontend
npm install <package-name>
```

**Backend:**
```bash
cd backend
venv\Scripts\activate
pip install <package-name>
pip freeze > requirements.txt  # Save dependencies
```

### Build for Production

**Frontend:**
```bash
cd frontend
npm run build
# Output in: frontend/dist/
```

**Backend:**
```bash
# Already production-ready
# Just run: python run.py
```

---

## 🌐 Deployment

### Frontend (Static Files)
```bash
cd frontend
npm run build
# Deploy 'dist' folder to any static host
# (Netlify, Vercel, GitHub Pages, etc.)
```

### Backend (API Server)
```bash
# Option 1: Using uvicorn directly
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Option 2: Using Docker (create Dockerfile)
# Option 3: Deploy to cloud (AWS, Azure, etc.)
```

---

## 💡 Tips

- **Development Mode**: Hot reload enabled (changes auto-refresh)
- **Data Updates**: Just replace CSV files and refresh browser
- **Performance**: Use SQLite for 100K+ rows
- **Debugging**: Check browser console (F12) and terminal logs

---

## 📞 Need Help?

1. Check if both frontend and backend are running
2. Check browser console for errors (F12)
3. Check terminal for error messages
4. Verify data files exist in `frontend/public/`
5. Try refreshing browser (Ctrl+F5)

---

## ✅ You're All Set!

Your dashboard is running at: **http://localhost:5179**

Enjoy your analytics! 🚀
