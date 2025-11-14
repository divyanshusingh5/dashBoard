# Next Steps to Complete Dashboard v2.0

## 🎯 Current Status

**Phase 1 Complete**: Foundation, models, SQL queries (85% done)
**Next Phase**: API, Migration, Frontend

---

## 🚀 Critical Path to Working Dashboard

### Step 1: Create FastAPI Main App (30 minutes)

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import settings, check_database_connection
from app.db.models import Base
from app.core.database import engine

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    # Check database connection
    connected = await check_database_connection()
    if not connected:
        raise Exception("Database connection failed!")

@app.get("/")
def root():
    return {"message": "Claims Analytics Dashboard API", "version": settings.APP_VERSION}

@app.get("/health")
async def health():
    db_connected = await check_database_connection()
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database": settings.DATABASE_TYPE,
        "database_connected": db_connected
    }

# TODO: Add routers
# from app.api.endpoints import claims, aggregation
# app.include_router(claims.router, prefix=settings.API_V1_PREFIX)
# app.include_router(aggregation.router, prefix=settings.API_V1_PREFIX)
```

**Test it**:
```bash
cd backend
uvicorn app.main:app --reload

# Visit: http://localhost:8000/docs
# Should see Swagger UI with health endpoint
```

---

### Step 2: Create Migration Script (1 hour)

Create `backend/scripts/migrate_csv_to_db.py`:

```python
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.database import engine, get_session
from app.db.models import Claim, SSNB, Weight
from tqdm import tqdm

def migrate_claims(csv_path: str = "../data/dat.csv"):
    """Migrate claims from CSV to database."""
    print(f"Loading claims from {csv_path}...")
    df = pd.read_csv(csv_path)

    print(f"Found {len(df):,} claims")

    session = get_session()
    try:
        # Batch insert for performance
        batch_size = 1000
        for i in tqdm(range(0, len(df), batch_size)):
            batch = df.iloc[i:i+batch_size]
            claims = [Claim.from_dict(row.to_dict()) for _, row in batch.iterrows()]
            session.bulk_save_objects(claims)
            session.commit()

        print(f"✅ Migrated {len(df):,} claims successfully!")
    finally:
        session.close()

def migrate_ssnb(csv_path: str = "../data/SSNB.csv"):
    """Migrate SSNB data from CSV."""
    print(f"Loading SSNB data from {csv_path}...")
    df = pd.read_csv(csv_path)

    session = get_session()
    try:
        ssnb_records = [SSNB.from_dict(row.to_dict()) for _, row in df.iterrows()]
        session.bulk_save_objects(ssnb_records)
        session.commit()
        print(f"✅ Migrated {len(df):,} SSNB records!")
    finally:
        session.close()

def migrate_weights(csv_path: str = "../data/weights.csv"):
    """Migrate weights from CSV."""
    print(f"Loading weights from {csv_path}...")
    df = pd.read_csv(csv_path)

    session = get_session()
    try:
        weights = [Weight.from_dict(row.to_dict()) for _, row in df.iterrows()]
        session.bulk_save_objects(weights)
        session.commit()
        print(f"✅ Migrated {len(df):,} weights!")
    finally:
        session.close()

if __name__ == "__main__":
    migrate_claims()
    migrate_ssnb()
    migrate_weights()
    print("\n🎉 Migration complete!")
```

**Run it**:
```bash
python scripts/migrate_csv_to_db.py
```

---

### Step 3: Create Basic API Endpoints (2 hours)

Create `backend/app/api/endpoints/claims.py`:

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.db.models import Claim

router = APIRouter(prefix="/claims", tags=["claims"])

@router.get("/")
def get_claims(
    limit: int = Query(100, le=10000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get paginated claims."""
    query = db.query(Claim)
    total = query.count()
    claims = query.offset(offset).limit(limit).all()

    return {
        "data": [claim.to_dict() for claim in claims],
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db)):
    """Get overall KPIs."""
    from sqlalchemy import func

    stats = db.query(
        func.count(Claim.id).label('total_claims'),
        func.avg(Claim.DOLLARAMOUNTHIGH).label('avg_settlement'),
        func.avg(Claim.variance_pct).label('avg_variance')
    ).first()

    return {
        "total_claims": stats.total_claims,
        "avg_settlement": round(stats.avg_settlement, 2) if stats.avg_settlement else 0,
        "avg_variance": round(stats.avg_variance, 2) if stats.avg_variance else 0
    }
```

Create `backend/app/api/endpoints/__init__.py`:
```python
from . import claims

__all__ = ['claims']
```

Update `backend/app/main.py`:
```python
# Add after app initialization:
from app.api.endpoints import claims

app.include_router(claims.router, prefix=settings.API_V1_PREFIX)
```

**Test it**:
```bash
# Visit: http://localhost:8000/docs
# Try: GET /api/v1/claims
# Try: GET /api/v1/claims/kpis
```

---

### Step 4: Create Materialized Views (30 minutes)

Create `backend/scripts/create_materialized_views.py`:

```python
from sqlalchemy import text
from app.core.database import engine
from app.utils.query_loader import query_loader

def create_views():
    """Create all materialized views."""
    print("Creating materialized views...")

    # Load the SQL
    sql = query_loader.load_ddl("create_materialized_views.sql")

    with engine.connect() as conn:
        # Execute the SQL
        conn.execute(text(sql))
        conn.commit()

    print("✅ Materialized views created!")

if __name__ == "__main__":
    create_views()
```

**Run it**:
```bash
python scripts/create_materialized_views.py
```

---

### Step 5: Frontend Setup (1 hour)

Create `frontend/package.json`:

```json
{
  "name": "claims-dashboard-frontend",
  "version": "2.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.1",
    "@tanstack/react-query": "^5.17.9",
    "axios": "^1.6.5",
    "recharts": "^2.10.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.11"
  }
}
```

Create `frontend/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

Create `frontend/src/App.tsx`:

```typescript
import { useEffect, useState } from 'react'
import axios from 'axios'

function App() {
  const [kpis, setKpis] = useState<any>(null)

  useEffect(() => {
    axios.get('/api/v1/claims/kpis')
      .then(res => setKpis(res.data))
      .catch(err => console.error(err))
  }, [])

  return (
    <div style={{ padding: '20px' }}>
      <h1>Claims Analytics Dashboard v2.0</h1>
      {kpis ? (
        <div>
          <p>Total Claims: {kpis.total_claims?.toLocaleString()}</p>
          <p>Avg Settlement: ${kpis.avg_settlement?.toLocaleString()}</p>
          <p>Avg Variance: {kpis.avg_variance?.toFixed(2)}%</p>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  )
}

export default App
```

Create `frontend/src/main.tsx`:

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

Create `frontend/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Claims Dashboard v2.0</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**Run it**:
```bash
cd frontend
npm install
npm run dev

# Visit: http://localhost:5173
```

---

## 📋 Complete Checklist

### Phase 2 - Minimum Viable Product
- [ ] Create `backend/app/main.py` - FastAPI app
- [ ] Create `backend/scripts/migrate_csv_to_db.py` - Data migration
- [ ] Run migration to populate database
- [ ] Create `backend/scripts/create_materialized_views.py` - View creation
- [ ] Create `backend/app/api/endpoints/claims.py` - Basic endpoints
- [ ] Test API with Swagger UI
- [ ] Create `frontend/package.json` - Frontend config
- [ ] Create `frontend/src/App.tsx` - Basic UI
- [ ] Install frontend dependencies
- [ ] Test end-to-end: Backend → Database → Frontend

**Estimated Time**: 4-6 hours
**Result**: Working dashboard showing KPIs

---

## 🎯 Priority Order

### Must Have (MVP):
1. ✅ FastAPI main app
2. ✅ Data migration script
3. ✅ `/claims` and `/kpis` endpoints
4. ✅ Basic React frontend showing KPIs
5. ✅ Materialized views creation

### Should Have (Full Features):
6. Aggregation endpoints
7. Filters and pagination
8. All 7 dashboard tabs
9. Chart components
10. Recalibration features

### Nice to Have (Polish):
11. Tests
12. Docker setup
13. CI/CD
14. Documentation updates

---

## 💡 Quick Wins

### Win 1: Health Check (5 min)
Already done! Just start the server:
```bash
uvicorn app.main:app --reload
curl http://localhost:8000/health
```

### Win 2: Database Tables (5 min)
```bash
cd backend
sqlite3 app/db/claims_analytics.db < app/db/queries/ddl/sqlite/create_tables.sql
sqlite3 app/db/claims_analytics.db ".tables"
```

### Win 3: Test Models (5 min)
```python
from app.db.models import Claim
claim = Claim(CLAIMID=123, DOLLARAMOUNTHIGH=50000)
print(claim.to_dict())
```

---

## 📞 Getting Help

### If Stuck:
1. Check `IMPLEMENTATION_SUMMARY.md` - What's already built
2. Check `QUICKSTART.md` - Setup instructions
3. Check `README.md` - Full documentation
4. Check `.env.example` - Configuration options

### Common Issues:
- **Import errors**: Make sure `PYTHONPATH=.` is set
- **Database not found**: Run `create_tables.sql` first
- **Port in use**: Kill process on port 8000/5173
- **Dependencies**: Run `pip install -r requirements.txt`

---

## 🎉 Success Criteria

### You'll know it's working when:
✅ Backend starts without errors
✅ `/health` endpoint returns `{"status": "healthy"}`
✅ `/api/v1/claims` returns claim data
✅ Frontend shows KPIs from backend
✅ Data flows: Database → API → Frontend

---

**Next Session**: Start with Step 1 (FastAPI main.py) and work through sequentially!

Good luck! 🚀
