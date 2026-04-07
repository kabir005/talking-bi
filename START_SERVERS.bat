@echo off
echo Starting Talking BI Application...
echo.

echo [1/2] Starting Backend Server...
start "Backend" cmd /k "cd talking-bi\backend && python main.py"
timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend Server...
start "Frontend" cmd /k "cd talking-bi\frontend && npm run dev"

echo.
echo ✅ Both servers are starting!
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit (servers will keep running)...
pause > nul
