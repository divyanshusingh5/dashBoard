@echo off
echo ========================================
echo Starting Frontend Dev Server (Port 5173)
echo ========================================
echo.

cd /d "%~dp0frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo.
    echo Installing dependencies...
    call npm install
    echo.
)

echo.
echo Starting frontend dev server...
echo Frontend will be available at: http://localhost:5173
echo.
echo Press CTRL+C to stop the server
echo.

call npm run dev

pause
