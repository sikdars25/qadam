@echo off
echo ========================================
echo Starting Academic Portal Frontend
echo ========================================
echo.

cd frontend

echo Checking if node_modules exists...
if not exist node_modules (
    echo Installing dependencies...
    npm install
) else (
    echo Dependencies already installed.
)

echo.
echo Starting React development server on http://localhost:3000
echo.
npm start

pause
