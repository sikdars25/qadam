@echo off
echo ============================================
echo Starting MySQL Server Locally
echo ============================================
echo.

REM Check if MySQL is installed
where mysql >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ MySQL not found in PATH
    echo.
    echo Please install MySQL or add it to your PATH:
    echo 1. Download from: https://dev.mysql.com/downloads/installer/
    echo 2. Or add MySQL bin folder to PATH
    echo    Example: C:\Program Files\MySQL\MySQL Server 8.0\bin
    echo.
    pause
    exit /b 1
)

echo ✅ MySQL found in PATH
echo.

REM Try to start MySQL service
echo Starting MySQL service...
net start MySQL80
if %ERRORLEVEL% EQU 0 (
    echo ✅ MySQL service started successfully
) else (
    echo ⚠️ Could not start MySQL service automatically
    echo.
    echo Try one of these methods:
    echo.
    echo Method 1: Windows Services
    echo   1. Press Win+R
    echo   2. Type: services.msc
    echo   3. Find "MySQL80" or "MySQL"
    echo   4. Right-click → Start
    echo.
    echo Method 2: Command Line (as Administrator)
    echo   net start MySQL80
    echo.
    echo Method 3: MySQL Workbench
    echo   Open MySQL Workbench and start the server
    echo.
)

echo.
echo ============================================
echo Testing MySQL Connection
echo ============================================
echo.

REM Test MySQL connection
echo Testing connection to localhost:3306...
mysql -h localhost -u root -p -e "SELECT 'MySQL is running!' AS status;"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ MySQL is running and accessible!
    echo.
    echo ============================================
    echo Next Steps:
    echo ============================================
    echo.
    echo 1. Check your .env file has correct MySQL credentials
    echo 2. Run: python database.py (to initialize database)
    echo 3. Run: python app.py (to start Flask backend)
    echo.
) else (
    echo.
    echo ❌ Could not connect to MySQL
    echo.
    echo Please check:
    echo 1. MySQL service is running
    echo 2. Root password is correct
    echo 3. MySQL is listening on port 3306
    echo.
)

pause
