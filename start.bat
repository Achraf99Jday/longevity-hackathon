@echo off
echo ========================================
echo  Longevity R&D Map Platform
echo ========================================
echo.

REM Check if database has data
python -c "from longevity_map.database.session import SessionLocal; from longevity_map.models.problem import Problem; db = SessionLocal(); count = db.query(Problem).count(); db.close(); exit(0 if count > 0 else 1)" >nul 2>&1
if errorlevel 1 (
    echo [0/3] No data found. Adding sample data...
    python scripts/add_sample_data.py
    echo.
)

REM Start API server in new window
echo [1/2] Starting API server on http://localhost:8000...
start "API Server - Port 8000" cmd /k "python -m uvicorn longevity_map.api.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for API to start
echo Waiting for API to initialize...
timeout /t 5 /nobreak >nul

REM Start web server in new window (auto-finds available port)
echo [2/2] Starting web server (will find available port)...
start "Web Server" cmd /k "python scripts/start_web.py"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo  Both servers are running!
echo ========================================
echo   API: http://localhost:8000
echo   Web: Check the web server window for the URL (usually port 3000 or 3001)
echo.
echo   Open http://localhost:3000 in your browser
echo.
echo   Close the command windows to stop the servers
echo ========================================
pause

