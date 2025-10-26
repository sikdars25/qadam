@echo off
echo ========================================
echo Fixing Database - Adding Email Columns
echo ========================================
echo.

cd backend

echo Running database migration...
python migrate_database.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Migration failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Database Fixed Successfully!
echo ========================================
echo.
echo Next step: Restart your backend
echo Run: start-backend.bat
echo.
pause
