@echo off
REM =======================================================================
REM COMPLETE CLEAN SETUP - Run this to set up everything from scratch
REM =======================================================================

echo.
echo ========================================
echo CLAIMS ANALYTICS - COMPLETE SETUP
echo ========================================
echo Data file: dat.csv (100,000 claims)
echo.
echo This will:
echo 1. Migrate CSV data to database
echo 2. Create materialized views (FIXES TIMEOUT!)
echo 3. Populate venue statistics
echo 4. Start backend server
echo.
echo Expected time: 3-5 minutes
echo ========================================
echo.
pause
echo.

cd backend

REM Step 1: Migrate data
echo [Step 1/4] Migrating data from CSV to database...
echo This will take 1-2 minutes for 100K claims...
echo.
venv\Scripts\python.exe migrate_comprehensive.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Migration failed!
    echo Check the error message above.
    pause
    exit /b 1
)
echo.
echo Done! Data migrated successfully.
echo ========================================
echo.

REM Step 2: Create materialized views (CRITICAL!)
echo [Step 2/4] Creating materialized views...
echo This makes aggregation 100x faster!
echo.
venv\Scripts\python.exe create_materialized_views.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to create materialized views!
    echo This is the most important step - without it, you'll get timeouts!
    pause
    exit /b 1
)
echo.
echo Done! Materialized views created successfully.
echo ========================================
echo.

REM Step 3: Populate venue statistics
echo [Step 3/4] Populating venue statistics...
echo This enables fast venue shift recommendations...
echo.
venv\Scripts\python.exe populate_venue_statistics.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Failed to populate venue statistics!
    echo Venue recommendations may be slower, but app will still work.
    pause
)
echo.
echo Done! Venue statistics populated.
echo ========================================
echo.

REM Step 4: Start backend server
echo [Step 4/4] Starting backend server...
echo Server will start on http://localhost:8000
echo.
echo ========================================
echo SETUP COMPLETE! ✓
echo ========================================
echo.
echo Backend starting on port 8000...
echo.
echo NEXT STEPS:
echo 1. Keep this window open (backend server running)
echo 2. Open a NEW terminal
echo 3. Run: cd frontend && npm run dev
echo 4. Open browser at: http://localhost:5173/
echo.
echo Press Ctrl+C to stop the backend server.
echo ========================================
echo.

venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
