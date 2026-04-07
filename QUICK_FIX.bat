@echo off
echo ========================================
echo TALKING BI - Quick Fix
echo ========================================
echo.
echo Fixing NumPy compatibility issue...
echo.

cd backend

echo Step 1: Downgrading NumPy to 1.x...
pip uninstall numpy -y
pip install "numpy<2.0.0"

echo.
echo Step 2: Reinstalling faiss-cpu...
pip install --force-reinstall faiss-cpu

echo.
echo Step 3: Reinstalling chromadb...
pip install --force-reinstall chromadb

echo.
echo ========================================
echo Fix Complete!
echo ========================================
echo.
echo Now start the servers:
echo.
echo Terminal 1 - Backend:
echo   cd backend
echo   python start_server.py
echo.
echo Terminal 2 - Frontend:
echo   cd frontend
echo   npm run dev
echo.
pause
