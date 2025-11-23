@echo off
REM Quick start script for local testing on Windows

echo Starting Longevity R&D Map Platform...

REM Initialize database
echo Initializing database...
python -c "from longevity_map.database.session import init_db; init_db()"

REM Start API server
echo Starting API server on http://localhost:8000...
start "API Server" cmd /k "python scripts/run_api.py"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start web server
echo Starting web interface on http://localhost:3000...
cd public
start "Web Server" cmd /k "python -m http.server 3000"

cd ..

echo.
echo Platform is running!
echo   API: http://localhost:8000
echo   Web: http://localhost:3000
echo.
echo Close the command windows to stop the servers
pause


