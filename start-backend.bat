@echo off
echo ========================================
echo Starting Academic Portal Backend
echo ========================================
echo.

cd backend

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo.
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Flask is not installed
    echo Please run: build-backend.bat
    pause
    exit /b 1
)

echo.
echo Checking .env file...
if not exist .env (
    echo WARNING: .env file not found
    echo Creating .env from example...
    if exist .env.example (
        copy .env.example .env >nul
        echo ✓ .env file created
    ) else (
        echo GROQ_API_KEY=your_groq_api_key_here > .env
        echo ✓ .env file created
    )
    echo IMPORTANT: Edit .env and add your GROQ_API_KEY
    echo.
)

echo.
echo Checking database...
if not exist academic.db (
    echo Initializing database...
    python database.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to initialize database
        pause
        exit /b 1
    )
    echo ✓ Database created
) else (
    echo ✓ Database exists
)

echo.
echo Running database migrations...
python migrate_database.py
if %errorlevel% neq 0 (
    echo WARNING: Migration had issues, but continuing...
)
echo ✓ Migrations complete

echo.
echo Creating required directories...
if not exist uploads mkdir uploads
if not exist textbooks mkdir textbooks
if not exist diagrams mkdir diagrams
if not exist vector_indices mkdir vector_indices

echo.
echo ========================================
echo Starting Flask Server
echo ========================================
echo.
echo Server URL: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Server failed to start
    echo Check the error messages above
    pause
    exit /b 1
)

pause
