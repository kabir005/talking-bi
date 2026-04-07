@echo off
echo ========================================
echo Fixing NumPy Compatibility Issue
echo ========================================
echo.
echo The issue: faiss-cpu requires NumPy 1.x but you have NumPy 2.x
echo Solution: Downgrading NumPy to version 1.26.4
echo.

pip uninstall numpy -y
pip install "numpy<2.0.0"

echo.
echo ========================================
echo NumPy Fixed!
echo ========================================
echo.
echo Now restart the backend server:
echo python start_server.py
echo.
pause
