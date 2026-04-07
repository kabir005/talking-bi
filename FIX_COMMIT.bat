@echo off
echo ========================================
echo Fixing Git Commit - Removing Large Files
echo ========================================

echo.
echo Step 1: Remove models from git cache...
git rm -r --cached backend/models/

echo.
echo Step 2: Add updated .gitignore...
git add .gitignore

echo.
echo Step 3: Commit the fix...
git commit -m "Fix: Remove large model files from git"

echo.
echo ========================================
echo Fixed! Now you can push safely.
echo ========================================
echo.
echo Next step:
echo   git remote add origin https://github.com/kabir005/talking-bi.git
echo   git push -u origin main
echo.
pause
