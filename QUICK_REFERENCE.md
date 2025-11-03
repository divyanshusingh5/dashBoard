# Quick Reference Guide - SQLite Backend

## Starting the Application

### Backend
```bash
cd backend
venv\Scripts\python.exe run.py
```

### Frontend
```bash
cd frontend
npm run dev
```

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Claims Endpoints
```
GET  /claims/claims              # Paginated claims
GET  /claims/kpis                # Dashboard KPIs
GET  /claims/filters             # Available filter options
GET  /claims/stats               # Statistical summary
```

### Analytics Endpoints (NEW!)
```
GET  /analytics/deviation-analysis                    # High variance cases
GET  /analytics/adjuster-performance                  # Adjuster metrics
GET  /analytics/adjuster-recommendations/{claim_id}   # Get recommendations
GET  /analytics/injury-benchmarks                     # Benchmark statistics
GET  /analytics/variance-drivers                      # Key variance factors
GET  /analytics/bad-combinations                      # Problem combinations
```

### Recalibration Endpoints
```
POST /recalibration/recalibrate        # Recalibrate with new weights
POST /recalibration/optimize           # Optimize weights
POST /recalibration/sensitivity-analysis  # Analyze sensitivity
GET  /recalibration/default-weights    # Get default weights
```

---

## Common Commands

### Check Backend Health
```bash
curl http://localhost:8000/health
```

### Get Top Adjusters
```bash
curl "http://localhost:8000/api/v1/analytics/adjuster-performance?min_cases=5"
```

### Get Recommendations for Claim
```bash
curl "http://localhost:8000/api/v1/analytics/adjuster-recommendations/CLM-2025-000001"
```

### Get Bad Combinations
```bash
curl "http://localhost:8000/api/v1/analytics/bad-combinations?min_variance_pct=20"
```

---

## Database

### Location
```
backend/app/db/claims_analytics.db
```

### Contents
```
Claims:  1,000 rows
Weights: 51 factors
Size:    1.2 MB
```

### Verify Database
```bash
cd backend
venv\Scripts\python.exe -c "from app.db.schema import *; engine = get_engine(); session = get_session(engine); print(f'Claims: {session.query(Claim).count()}'); print(f'Weights: {session.query(Weight).count()}')"
```

---

## Re-run Migration

If you update CSV files:

```bash
cd backend
venv\Scripts\python.exe migrate_csv_to_sqlite.py
```

This will:
1. Clear existing database
2. Import all claims from dat.csv
3. Import all weights from weights.csv
4. Create optimized indexes
5. Analyze tables for query optimization

---

## Troubleshooting

### Backend won't start
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Database errors
```bash
# Delete and recreate database
rm backend/app/db/claims_analytics.db
cd backend
venv\Scripts\python.exe migrate_csv_to_sqlite.py
```

### Port already in use
```bash
# Find process on port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /F /PID <PID>
```

---

## Performance Tips

### For Large Datasets (100K+ rows)
1. Use pagination for queries
2. Apply filters to reduce result set
3. Use aggregated cache table
4. Consider connection pooling

### Query Optimization
```python
# Use filters
await data_service.get_paginated_claims(
    page=1,
    page_size=100,
    filters={
        'injury_group': ['Spinal'],
        'min_variance': 15
    }
)

# Use sorting
await data_service.get_paginated_claims(
    sort_by='variance_pct',
    sort_order='desc'
)
```

---

## File Structure

```
dashBoard/
├── backend/
│   ├── app/
│   │   ├── db/
│   │   │   ├── schema.py                  # Database models
│   │   │   └── claims_analytics.db        # SQLite database
│   │   ├── api/
│   │   │   └── endpoints/
│   │   │       ├── claims.py              # Claims API
│   │   │       ├── recalibration.py       # Weight API
│   │   │       └── analytics.py           # Analytics API (NEW)
│   │   └── services/
│   │       ├── data_service.py            # CSV service
│   │       └── data_service_sqlite.py     # SQLite service (ACTIVE)
│   ├── migrate_csv_to_sqlite.py           # Migration script
│   ├── run.py                             # Start server
│   └── requirements.txt                   # Dependencies
│
├── frontend/
│   ├── public/
│   │   ├── dat.csv                        # Source data
│   │   └── weights.csv                    # Weight factors
│   └── src/
│       ├── api/                           # API clients
│       ├── components/                    # React components
│       └── pages/                         # Dashboard pages
│
└── Documentation/
    ├── SQLITE_MIGRATION_COMPLETE.md       # Full migration guide
    ├── QUICK_REFERENCE.md                 # This file
    ├── HOW_TO_RUN.md                      # Running instructions
    └── ANALYSIS_FEATURES.md               # Feature documentation
```

---

## Quick Tests

### Test All Endpoints
```bash
# Health
curl http://localhost:8000/health

# Claims
curl "http://localhost:8000/api/v1/claims/claims?page=1&page_size=5"

# KPIs
curl "http://localhost:8000/api/v1/claims/kpis"

# Adjuster Performance
curl "http://localhost:8000/api/v1/analytics/adjuster-performance"

# Deviation Analysis
curl "http://localhost:8000/api/v1/analytics/deviation-analysis?limit=10"

# Bad Combinations
curl "http://localhost:8000/api/v1/analytics/bad-combinations"
```

---

## Dependencies

### Backend (Python)
```
fastapi
uvicorn[standard]
pydantic
pandas
numpy
sqlalchemy>=2.0.0
scipy
tqdm
```

### Frontend (Node.js)
```
react
typescript
vite
tailwindcss
recharts
axios
```

---

## API Documentation

Interactive API documentation available at:
```
http://localhost:8000/api/v1/docs
```

Features:
- Try out endpoints
- See request/response schemas
- Download OpenAPI spec
- Test authentication

---

## Support

For issues or questions:
1. Check logs in terminal
2. Review `SQLITE_MIGRATION_COMPLETE.md`
3. Check API docs at `/api/v1/docs`
4. Verify database with verification command above

---

**Status: Running** ✅
**Backend:** http://localhost:8000
**Frontend:** http://localhost:5179
**API Docs:** http://localhost:8000/api/v1/docs
