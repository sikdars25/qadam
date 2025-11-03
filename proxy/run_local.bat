@echo off
echo ========================================
echo Starting Backend Proxy Service (Local)
echo ========================================
echo.

REM Check if venv exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup_local.bat first
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Creating default .env file...
    (
        echo # Backend Proxy Configuration
        echo FLASK_ENV=development
        echo FLASK_DEBUG=True
        echo SECRET_KEY=dev-secret-key
        echo DATABASE_URL=sqlite:///qadam.db
        echo OCR_SERVICE_URL=http://130.107.48.145
        echo AI_SERVICE_URL=http://130.107.48.221
        echo FRONTEND_URL=http://localhost:3000
        echo JWT_SECRET_KEY=your-secret-key-here
        echo JWT_ALGORITHM=HS256
        echo JWT_EXPIRATION_HOURS=24
    ) > .env
)

REM Run the app
echo Starting Flask application...
echo.
echo Backend Proxy will be available at:
echo   http://localhost:5000/api/health
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
