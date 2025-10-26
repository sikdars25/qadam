@echo off
REM Force Push Monorepo Structure to GitHub

echo ========================================
echo   Force Push Monorepo to GitHub
echo ========================================
echo.

echo WARNING: This will OVERWRITE the remote repository!
echo.
echo Current situation:
echo   - Remote has backend files in root
echo   - Local has monorepo structure (backend/ and frontend/ folders)
echo.
echo This will:
echo   1. Add all monorepo files
echo   2. Commit everything
echo   3. Force push to GitHub (overwrites remote)
echo.

set /p CONFIRM="Are you sure? This will replace remote content! (yes/no): "
if /i not "%CONFIRM%"=="yes" (
    echo Cancelled
    pause
    exit /b 0
)

echo.
echo ========================================
echo   Step 1: Add All Files
echo ========================================
echo.

echo Adding all files...
git add -A

if errorlevel 1 (
    echo [ERROR] Failed to add files
    pause
    exit /b 1
)

echo [OK] Files added

echo.
echo ========================================
echo   Step 2: Commit
echo ========================================
echo.

git commit -m "Initial commit: Monorepo structure with frontend and backend"

if errorlevel 1 (
    echo [WARNING] Nothing to commit or already committed
)

echo.
echo ========================================
echo   Step 3: Force Push
echo ========================================
echo.

echo Force pushing to GitHub...
echo This will overwrite the remote repository!
echo.

git push origin main --force

if errorlevel 1 (
    echo [ERROR] Push failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Success!
echo ========================================
echo.
echo Monorepo pushed to GitHub!
echo.
echo Structure:
echo   qadam/
echo   ├── .github/workflows/main_qadam-backend.yml
echo   ├── backend/
echo   └── frontend/
echo.
echo Next steps:
echo   1. Visit: https://github.com/sikdars25/qadam
echo   2. Verify monorepo structure
echo   3. Go to Actions tab
echo   4. Trigger workflow to test deployment
echo.

pause
