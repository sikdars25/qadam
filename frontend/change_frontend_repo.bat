@echo off
REM Change Frontend GitHub Repository

echo ========================================
echo   Change Frontend GitHub Repository
echo ========================================
echo.

echo Current repository:
git remote -v
echo.

echo Enter new GitHub repository URL
echo Example: https://github.com/username/new-repo-name.git
echo.

set /p NEW_REPO_URL="New repository URL: "

if "%NEW_REPO_URL%"=="" (
    echo [ERROR] No URL provided
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Changing Repository
echo ========================================
echo.

echo Old: https://github.com/sikdars25/qadam_frontend.git
echo New: %NEW_REPO_URL%
echo.

set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled
    pause
    exit /b 0
)

echo.
echo Updating remote URL...
git remote set-url origin %NEW_REPO_URL%

if errorlevel 1 (
    echo [ERROR] Failed to update remote
    pause
    exit /b 1
)

echo [OK] Remote updated
echo.

echo Verifying...
git remote -v
echo.

echo ========================================
echo   Push to New Repository
echo ========================================
echo.

set /p PUSH_NOW="Push to new repository now? (y/n): "
if /i not "%PUSH_NOW%"=="y" (
    echo.
    echo Remote changed successfully!
    echo.
    echo To push later, run:
    echo   git push -u origin main
    echo.
    pause
    exit /b 0
)

echo.
echo Pushing to new repository...
git push -u origin main

if errorlevel 1 (
    echo.
    echo [WARNING] Push failed. This might be because:
    echo   1. New repository doesn't exist yet
    echo   2. You don't have permission
    echo   3. Branch name is different (try: git push -u origin master)
    echo.
    echo Create the repository on GitHub first, then run:
    echo   git push -u origin main
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Success!
echo ========================================
echo.
echo Frontend repository changed to:
echo %NEW_REPO_URL%
echo.
echo All code and history preserved.
echo.

pause
