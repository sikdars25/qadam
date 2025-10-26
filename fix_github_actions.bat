@echo off
REM Fix GitHub Actions for Monorepo

echo ========================================
echo   Fix GitHub Actions for Monorepo
echo ========================================
echo.

echo This will:
echo   1. Create .github/workflows/ in root
echo   2. Copy corrected main_qadam-backend.yml
echo   3. Remove old workflow from backend/
echo.

set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled
    pause
    exit /b 0
)

echo.
echo ========================================
echo   Step 1: Create Workflow Directory
echo ========================================
echo.

if not exist ".github\workflows" (
    mkdir .github\workflows
    echo [OK] Created .github\workflows\
) else (
    echo [OK] .github\workflows\ already exists
)

echo.
echo ========================================
echo   Step 2: Copy Workflow File
echo ========================================
echo.

if exist ".github\workflows\main_qadam-backend.yml" (
    echo [WARNING] backend-deploy.yml already exists
    set /p OVERWRITE="Overwrite? (y/n): "
    if /i not "%OVERWRITE%"=="y" (
        echo Skipped
        goto step3
    )
)

copy /Y ".github\workflows\main_qadam-backend.yml" ".github\workflows\main_qadam-backend.yml" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to copy workflow file
    echo.
    echo Please manually copy:
    echo   From: .github\workflows\backend-deploy.yml
    echo   To: .github\workflows\backend-deploy.yml
    echo.
    pause
    exit /b 1
)

echo [OK] Workflow file copied

:step3
echo.
echo ========================================
echo   Step 3: Remove Old Workflow
echo ========================================
echo.

if exist "backend\.github" (
    set /p REMOVE_OLD="Remove backend\.github folder? (y/n): "
    if /i "%REMOVE_OLD%"=="y" (
        rmdir /s /q "backend\.github"
        echo [OK] Removed backend\.github\
    ) else (
        echo [SKIPPED] Kept backend\.github\
    )
) else (
    echo [OK] No old workflow to remove
)

echo.
echo ========================================
echo   Step 4: Update Secrets (Manual)
echo ========================================
echo.

echo Please verify these secrets exist in GitHub:
echo.
echo   1. Go to: https://github.com/sikdars25/qadam/settings/secrets/actions
echo   2. Check for these secrets:
echo      - AZUREAPPSERVICE_CLIENTID_...
echo      - AZUREAPPSERVICE_TENANTID_...
echo      - AZUREAPPSERVICE_SUBSCRIPTIONID_...
echo.
echo   3. If missing, add them from Azure Portal
echo.

pause

echo.
echo ========================================
echo   Step 5: Commit and Push
echo ========================================
echo.

set /p COMMIT_NOW="Commit and push changes? (y/n): "
if /i not "%COMMIT_NOW%"=="y" (
    echo.
    echo Changes made but not committed.
    echo.
    echo To commit manually:
    echo   git add .github/workflows/backend-deploy.yml
    echo   git commit -m "Fix: Update GitHub Actions for monorepo"
    echo   git push origin main
    echo.
    pause
    exit /b 0
)

echo.
echo Adding files...
git add .github/workflows/main_qadam-backend.yml

echo Committing...
git commit -m "Fix: Update GitHub Actions for monorepo structure"

if errorlevel 1 (
    echo [ERROR] Commit failed
    pause
    exit /b 1
)

echo Pushing to GitHub...
git push origin main

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
echo GitHub Actions updated for monorepo structure.
echo.
echo Next steps:
echo   1. Go to: https://github.com/sikdars25/qadam/actions
echo   2. Trigger workflow manually or push backend changes
echo   3. Verify deployment succeeds
echo.
echo The workflow will now:
echo   - Only trigger on backend/** changes
echo   - Deploy from backend/ folder
echo   - Work correctly with monorepo
echo.

pause
