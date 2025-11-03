@echo off
echo ========================================
echo Refreshing Materialized Views Cache
echo ========================================
echo.

cd /d "%~dp0backend"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo.
echo Option 1: Python Script (Offline)
echo Option 2: API Endpoint (Backend must be running)
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Running Python script to refresh views...
    python -c "from app.db.materialized_views import create_all_materialized_views, refresh_all_materialized_views; create_all_materialized_views(); refresh_all_materialized_views(); print('Done!')"
    echo.
    echo Cache refreshed successfully!
) else if "%choice%"=="2" (
    echo.
    echo Calling API endpoint...
    curl -X POST http://localhost:8000/api/v1/aggregation/refresh-cache
    echo.
) else (
    echo Invalid choice!
)

echo.
pause
