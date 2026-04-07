@echo off
echo ================================================================================
echo                    TALKING BI - RESTART SCRIPT
echo ================================================================================
echo.
echo This will restart both backend and frontend servers.
echo Make sure to close any existing terminals running the servers first!
echo.
pause

echo.
echo Starting Backend Server...
echo ================================================================================
cd backend
start cmd /k "python main.py"

timeout /t 5

echo.
echo Starting Frontend Server...
echo ================================================================================
cd ..\frontend
start cmd /k "npm run dev"

echo.
echo ================================================================================
echo Both servers are starting in separate windows!
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo NEXT STEPS:
echo 1. Wait for both servers to start (check the new windows)
echo 2. Go to http://localhost:5173/datasets
echo 3. DELETE old dataset
echo 4. RE-UPLOAD your CSV file
echo 5. Generate new dashboard
echo ================================================================================
pause
