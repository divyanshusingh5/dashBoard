@echo off
echo ========================================
echo Starting Backend Server (Port 8000)
echo ========================================
echo.

cd /d "%~dp0backend"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if database exists
if not exist "app\db\claims_analytics.db" (
    echo.
    echo WARNING: Database not found!
    echo Please run migration first: python migrate_csv_to_sqlite.py
    echo.
    pause
    exit /b 1
)

echo.
echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/api/v1/docs
echo.
echo Press CTRL+C to stop the server
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
