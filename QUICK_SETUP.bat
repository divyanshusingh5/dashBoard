@echo off
REM Quick Setup Script for New Data
REM Run this after putting new dat.csv in backend/

echo ========================================
echo CLAIMS ANALYTICS - QUICK SETUP
echo ========================================
echo.

cd backend

echo [1/6] Killing old servers...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo Done!
echo.

echo [2/6] Migrating data from CSV to database...
echo This may take 2-3 minutes for large files...
venv\Scripts\python.exe migrate_smart.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Migration failed!
    pause
    exit /b 1
)
echo Done!
echo.

echo [3/6] Creating materialized views (CRITICAL!)...
echo This makes aggregation 100x faster...
venv\Scripts\python.exe create_materialized_views.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create materialized views!
    pause
    exit /b 1
)
echo Done!
echo.

echo [4/6] Populating venue statistics...
echo This enables fast venue shift recommendations...
venv\Scripts\python.exe populate_venue_statistics.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to populate venue statistics!
    pause
    exit /b 1
)
echo Done!
echo.

echo [5/6] Clearing Python cache...
powershell -Command "Get-ChildItem -Include __pycache__,*.pyc -Recurse -Force | Remove-Item -Force -Recurse" >nul 2>&1
echo Done!
echo.

echo [6/6] Starting backend server...
echo Server will start on http://localhost:8000
echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo Backend starting... (keep this window open)
echo Open a new terminal and run: cd frontend && npm run dev
echo Then open browser at: http://localhost:5173/
echo.
echo Press Ctrl+C to stop the backend server.
echo ========================================
echo.

venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
