@echo off
REM Setup Monorepo Structure for Qadam

echo ========================================
echo   Setup Qadam Monorepo
echo ========================================
echo.

echo This will create a new repository structure:
echo   https://github.com/sikdars25/qadam
echo   ├── frontend/
echo   └── backend/
echo.

set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled
    pause
    exit /b 0
)

echo.
echo ========================================
echo   Step 1: Create New Repository
echo ========================================
echo.

echo Please create a new GitHub repository:
echo   1. Go to: https://github.com/new
echo   2. Repository name: qadam
echo   3. Add README file: YES
echo   4. Click Create repository
echo.
echo Press any key after creating the repository...
pause >nul

echo.
set /p REPO_URL="Enter the repository URL [https://github.com/sikdars25/qadam.git]: "
if "%REPO_URL%"=="" set REPO_URL=https://github.com/sikdars25/qadam.git

echo.
echo ========================================
echo   Step 2: Clone Repository
echo ========================================
echo.

cd ..
if exist qadam (
    echo [WARNING] qadam folder already exists
    set /p OVERWRITE="Delete and recreate? (y/n): "
    if /i "%OVERWRITE%"=="y" (
        rmdir /s /q qadam
    ) else (
        echo Cancelled
        pause
        exit /b 1
    )
)

echo Cloning repository...
git clone %REPO_URL%

if errorlevel 1 (
    echo [ERROR] Failed to clone repository
    pause
    exit /b 1
)

cd qadam

echo.
echo ========================================
echo   Step 3: Copy Frontend Code
echo ========================================
echo.

echo Creating frontend folder...
mkdir frontend

echo Copying frontend files...
xcopy ..\aqnamic\frontend\public frontend\public\ /E /I /Q
xcopy ..\aqnamic\frontend\src frontend\src\ /E /I /Q
copy ..\aqnamic\frontend\package.json frontend\
copy ..\aqnamic\frontend\package-lock.json frontend\ 2>nul
copy ..\aqnamic\frontend\.gitignore frontend\ 2>nul
copy ..\aqnamic\frontend\README.md frontend\ 2>nul

echo [OK] Frontend copied

echo.
echo ========================================
echo   Step 4: Copy Backend Code
echo ========================================
echo.

echo Creating backend folder...
mkdir backend

echo Copying backend files...
copy ..\aqnamic\backend\*.py backend\
copy ..\aqnamic\backend\*.txt backend\
copy ..\aqnamic\backend\*.bat backend\
copy ..\aqnamic\backend\*.md backend\
copy ..\aqnamic\backend\.env.example backend\
copy ..\aqnamic\backend\.gitignore backend\ 2>nul

echo [OK] Backend copied

echo.
echo ========================================
echo   Step 5: Create Root Files
echo ========================================
echo.

echo Creating .gitignore...
(
echo # Frontend
echo frontend/node_modules/
echo frontend/build/
echo frontend/.env.local
echo.
echo # Backend
echo backend/venv/
echo backend/__pycache__/
echo backend/.env
echo backend/*.pyc
echo backend/uploads/
echo backend/diagrams/
echo backend/textbooks/
echo backend/vector_db/
echo backend/vector_indices/
echo.
echo # IDE
echo .vscode/
echo .idea/
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
) > .gitignore

echo Creating README.md...
(
echo # Qadam - CBSE Academic Management System
echo.
echo Full-stack application for CBSE question paper management and AI-powered solutions.
echo.
echo ## Structure
echo.
echo - **frontend/** - React application
echo - **backend/** - Python Flask API
echo.
echo ## Quick Start
echo.
echo ### Frontend
echo ```bash
echo cd frontend
echo npm install
echo npm start
echo ```
echo.
echo ### Backend
echo ```bash
echo cd backend
echo python -m venv venv
echo venv\Scripts\activate
echo pip install -r requirements.txt
echo python app.py
echo ```
echo.
echo ## Features
echo.
echo - 📄 Question paper parsing with OCR
echo - 🤖 AI-powered solution generation
echo - 📚 Textbook integration with FAISS vector search
echo - 👥 User management and authentication
echo - 📊 Admin analytics dashboard
echo.
echo ## Tech Stack
echo.
echo **Frontend:** React, Axios, CSS
echo **Backend:** Python, Flask, MySQL, Groq AI, FAISS
echo **Deployment:** Azure Functions, Azure MySQL
echo.
echo ## Documentation
echo.
echo See individual README files in `frontend/` and `backend/` folders for detailed setup instructions.
) > README.md

echo [OK] Root files created

echo.
echo ========================================
echo   Step 6: Commit and Push
echo ========================================
echo.

git add .
git commit -m "Initial commit: Add frontend and backend to monorepo"

echo Pushing to GitHub...
git push origin main

if errorlevel 1 (
    echo [ERROR] Push failed
    echo.
    echo Try manually:
    echo   cd qadam
    echo   git push origin main
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Success!
echo ========================================
echo.
echo Monorepo created at:
echo   %REPO_URL%
echo.
echo Structure:
echo   qadam/
echo   ├── frontend/
echo   └── backend/
echo.
echo Next steps:
echo   1. Visit: %REPO_URL%
echo   2. Verify files are uploaded
echo   3. Archive old repositories (optional)
echo.

pause
