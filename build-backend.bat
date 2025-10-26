@echo off
echo ========================================
echo Building Academic Portal Backend
echo ========================================
echo.

cd backend

echo Step 1: Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo.
echo Step 2: Creating virtual environment (optional)...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo Virtual environment already exists
)

echo.
echo Step 3: Installing basic dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install basic dependencies
    pause
    exit /b 1
)

echo.
echo Step 4: Installing AI dependencies...
pip install -r requirements-ai.txt
if %errorlevel% neq 0 (
    echo WARNING: Failed to install AI dependencies
    echo You can install them later with: install_ai_features.bat
)

echo.
echo Step 5: Checking for .env file...
if not exist .env (
    echo WARNING: .env file not found
    echo Creating .env from example...
    if exist .env.example (
        copy .env.example .env
        echo ✓ .env file created
        echo IMPORTANT: Edit .env and add your GROQ_API_KEY
    ) else (
        echo Creating new .env file...
        echo GROQ_API_KEY=your_groq_api_key_here > .env
        echo ✓ .env file created
        echo IMPORTANT: Edit .env and add your GROQ_API_KEY
    )
) else (
    echo ✓ .env file exists
)

echo.
echo Step 6: Initializing database...
if not exist academic.db (
    echo Creating database...
    python database.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to initialize database
        pause
        exit /b 1
    )
    echo ✓ Database created
) else (
    echo Database already exists, running migrations...
    python database.py
    echo ✓ Database updated
)

echo.
echo Step 7: Creating required directories...
if not exist uploads mkdir uploads
if not exist textbooks mkdir textbooks
if not exist diagrams mkdir diagrams
if not exist vector_indices mkdir vector_indices
echo ✓ Directories created

echo.
echo Step 8: Verifying installation...
python -c "import flask; print('✓ Flask')"
python -c "import fitz; print('✓ PyMuPDF')"
python -c "from flask_cors import CORS; print('✓ Flask-CORS')"

echo.
echo Checking AI dependencies (optional)...
python -c "import faiss; print('✓ FAISS')" 2>nul || echo ⚠ FAISS not installed (run install_ai_features.bat)
python -c "import groq; print('✓ Groq')" 2>nul || echo ⚠ Groq not installed (run install_ai_features.bat)
python -c "from sentence_transformers import SentenceTransformer; print('✓ Sentence Transformers')" 2>nul || echo ⚠ Sentence Transformers not installed (run install_ai_features.bat)

echo.
echo ========================================
echo Backend Build Complete!
echo ========================================
echo.
echo Your backend is ready to run!
echo.
echo IMPORTANT: Make sure to edit .env file with your GROQ_API_KEY
echo Get one free at: https://console.groq.com
echo.
echo Optional installations:
echo - AI features: install_ai_features.bat
echo - OCR support: install_ocr.bat
echo.
echo ========================================
echo Starting Backend Server...
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
