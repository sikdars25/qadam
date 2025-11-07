@echo off
echo ========================================
echo OCR Libraries Check
echo ========================================
echo.

REM Check if venv exists
if not exist venv (
    echo ERROR: Virtual environment not found
    echo Please create venv first: python -m venv venv
    pause
    exit /b 1
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo ========================================
echo Python Environment
echo ========================================
python --version
echo.
echo Python location:
where python
echo.

echo ========================================
echo Installed Packages
echo ========================================
pip list | findstr /i "flask easyocr pillow numpy opencv pymupdf torch"
echo.

echo ========================================
echo Running Library Check Script
echo ========================================
python check_ocr_libraries.py
echo.

pause
