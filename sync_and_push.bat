@echo off
REM Sync with GitHub and Push Changes

echo ========================================
echo   Sync and Push to GitHub
echo ========================================
echo.

echo This will:
echo   1. Stage workflow file
echo   2. Commit changes
echo   3. Pull from GitHub
echo   4. Push your changes
echo.

set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled
    pause
    exit /b 0
)

echo.
echo Staging workflow file...
git add .github/workflows/main_qadam-backend.yml

echo Committing...
git commit -m "Update: GitHub Actions workflow for monorepo"

echo.
echo Pulling from GitHub...
git pull origin main --allow-unrelated-histories --no-edit

if errorlevel 1 (
    echo [ERROR] Pull failed - check for conflicts
    pause
    exit /b 1
)

echo.
echo Pushing to GitHub...
git push origin main

if errorlevel 1 (
    echo [ERROR] Push failed
    pause
    exit /b 1
)

echo.
echo Success!
pause
