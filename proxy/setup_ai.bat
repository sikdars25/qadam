@echo off
echo ========================================
echo Installing AI Dependencies
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found!
    echo Please create one with: python -m venv venv
    pause
    exit /b 1
)

echo.
echo Installing lightweight AI packages...
echo.

REM Install AI dependencies
pip install groq==0.4.1
pip install scikit-learn==1.3.2
pip install numpy==1.24.3
pip install scipy==1.11.4
pip install nltk==3.8.1

echo.
echo ========================================
echo Testing AI Features
echo ========================================
echo.

REM Test imports
python -c "import groq; print('✅ Groq installed')"
python -c "import sklearn; print('✅ scikit-learn installed')"
python -c "import numpy; print('✅ NumPy installed')"
python -c "import scipy; print('✅ SciPy installed')"
python -c "import nltk; print('✅ NLTK installed')"

echo.
echo ========================================
echo Downloading NLTK Data
echo ========================================
echo.

python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

echo.
echo ========================================
echo Testing AI Helper Functions
echo ========================================
echo.

python -c "from ai_helpers import check_ai_availability, get_ai_status_message; print(get_ai_status_message())"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Set GROQ_API_KEY in your .env file
echo    Get your key from: https://console.groq.com/
echo.
echo 2. Test the AI features:
echo    python test_ai.py
echo.
echo 3. Deploy to Azure:
echo    git add .
echo    git commit -m "Add lightweight AI dependencies"
echo    git push origin main
echo.

pause
