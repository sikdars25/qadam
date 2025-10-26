@echo off
REM Commit and Push GitHub Actions Workflow

echo ========================================
echo   Commit GitHub Actions Workflow
echo ========================================
echo.

echo Current status:
echo   - Workflow file: .github/workflows/main_qadam-backend.yml
echo   - Status: Ready to commit
echo.

echo This workflow is already configured for monorepo:
echo   ✅ Package path: backend
echo   ✅ Trigger paths: backend/**
echo   ✅ Working directory: backend
echo   ✅ Deployment: backend-deploy
echo.

set /p CONFIRM="Commit and push workflow? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled
    pause
    exit /b 0
)

echo.
echo ========================================
echo   Adding Files
echo ========================================
echo.

echo Adding workflow file...
git add .github/workflows/main_qadam-backend.yml

echo Adding documentation...
git add WORKFLOW_VERIFICATION.md
git add MONOREPO_GITHUB_ACTIONS.md

if errorlevel 1 (
    echo [ERROR] Failed to add files
    pause
    exit /b 1
)

echo [OK] Files added

echo.
echo ========================================
echo   Committing
echo ========================================
echo.

git commit -m "Add: GitHub Actions workflow for backend deployment (monorepo structure)"

if errorlevel 1 (
    echo [ERROR] Commit failed
    pause
    exit /b 1
)

echo [OK] Committed

echo.
echo ========================================
echo   Pushing to GitHub
echo ========================================
echo.

git push origin main

if errorlevel 1 (
    echo.
    echo [WARNING] Push to 'main' failed. Trying 'master'...
    git push origin master
    
    if errorlevel 1 (
        echo [ERROR] Push failed
        echo.
        echo Please check:
        echo   1. Remote repository URL is correct
        echo   2. You have push permissions
        echo   3. Branch name is correct (main or master)
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Pushed to GitHub

echo.
echo ========================================
echo   Success!
echo ========================================
echo.
echo Workflow deployed to GitHub!
echo.
echo Next steps:
echo   1. Go to: https://github.com/sikdars25/qadam/actions
echo   2. Click "Run workflow" to test deployment
echo   3. Or push a change to backend/ folder
echo.
echo To test:
echo   echo # Test ^>^> backend/README.md
echo   git add backend/README.md
echo   git commit -m "Test: Trigger deployment"
echo   git push origin main
echo.

pause
