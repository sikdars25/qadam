@echo off
REM Setup Git Remote for Monorepo

echo ========================================
echo   Setup Git Remote
echo ========================================
echo.

echo Current branch:
git branch
echo.

echo Current remotes:
git remote -v
echo.

echo You need to add the GitHub repository as remote.
echo.
echo Enter your GitHub repository URL:
echo Example: https://github.com/sikdars25/qadam.git
echo.

set /p REPO_URL="Repository URL: "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL provided
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Adding Remote
echo ========================================
echo.

echo Adding remote 'origin'...
git remote add origin %REPO_URL%

if errorlevel 1 (
    echo [WARNING] Remote 'origin' might already exist
    echo Updating remote URL...
    git remote set-url origin %REPO_URL%
    
    if errorlevel 1 (
        echo [ERROR] Failed to set remote
        pause
        exit /b 1
    )
)

echo [OK] Remote added/updated

echo.
echo Verifying remote...
git remote -v

echo.
echo ========================================
echo   Push to GitHub
echo ========================================
echo.

echo Your branch is: main
echo Remote is: %REPO_URL%
echo.

set /p PUSH_NOW="Push to GitHub now? (y/n): "
if /i not "%PUSH_NOW%"=="y" (
    echo.
    echo Remote configured. To push later, run:
    echo   git push -u origin main
    echo.
    pause
    exit /b 0
)

echo.
echo Pushing to GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo [ERROR] Push failed
    echo.
    echo Possible reasons:
    echo   1. Repository doesn't exist on GitHub
    echo   2. Authentication failed
    echo   3. No permission to push
    echo.
    echo Please:
    echo   1. Create repository on GitHub: https://github.com/new
    echo   2. Repository name: qadam
    echo   3. Then run this script again
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Success!
echo ========================================
echo.
echo Code pushed to: %REPO_URL%
echo Branch: main
echo.
echo Next steps:
echo   1. Visit: %REPO_URL%
echo   2. Verify files are uploaded
echo   3. Go to Actions tab to see workflow
echo.

pause
