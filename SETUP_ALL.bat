@echo off
echo ========================================
echo TALKING BI - Complete Setup
echo ========================================

echo.
echo Step 1: Installing Backend Dependencies...
echo ========================================
cd backend
call install_dependencies.bat
cd ..

echo.
echo Step 2: Installing Frontend Dependencies...
echo ========================================
cd frontend
call npm install
cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application:
echo 1. Backend: cd backend ^&^& python start_server.py
echo 2. Frontend: cd frontend ^&^& npm run dev
echo.
pause
