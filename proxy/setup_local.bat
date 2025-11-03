@echo off
echo ========================================
echo Backend Proxy Service - Local Setup
echo ========================================
echo.

REM Check Python version
echo Step 1: Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.10 or 3.11
    pause
    exit /b 1
)
echo.

REM Create virtual environment
echo Step 2: Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created!
)
echo.

REM Activate virtual environment
echo Step 3: Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Step 4: Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install requirements
echo Step 5: Installing dependencies...
echo Installing with increased timeout (10 minutes per package)...
pip install --timeout 600 -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo.

REM Create .env file if it doesn't exist
echo Step 6: Checking environment configuration...
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env 2>nul || (
        echo Creating default .env file...
        (
            echo # Backend Proxy Configuration
            echo.
            echo # Flask
            echo FLASK_ENV=development
            echo FLASK_DEBUG=True
            echo SECRET_KEY=dev-secret-key-change-in-production
            echo.
            echo # Database
            echo DATABASE_URL=sqlite:///qadam.db
            echo.
            echo # API URLs
            echo OCR_SERVICE_URL=http://130.107.48.145
            echo AI_SERVICE_URL=http://130.107.48.221
            echo.
            echo # CORS
            echo FRONTEND_URL=http://localhost:3000
            echo.
            echo # JWT
            echo JWT_SECRET_KEY=your-secret-key-here
            echo JWT_ALGORITHM=HS256
            echo JWT_EXPIRATION_HOURS=24
        ) > .env
    )
    echo .env file created! Please update with your configuration.
) else (
    echo .env file already exists
)
echo.

REM Test imports
echo Step 7: Testing imports...
python -c "import flask; print('✅ Flask:', flask.__version__)"
python -c "import sqlalchemy; print('✅ SQLAlchemy: OK')"
python -c "import jwt; print('✅ PyJWT: OK')"
python -c "from app import app; print('✅ Flask app: OK')"
echo.

echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo To run the backend proxy service:
echo   1. Activate venv: venv\Scripts\activate.bat
echo   2. Run app: python app.py
echo   3. Test: curl http://localhost:5000/api/health
echo.
echo Press any key to start the backend service now...
pause > nul

echo.
echo Starting Backend Proxy service...
python app.py
