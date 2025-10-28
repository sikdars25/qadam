@echo off
REM Migrate Cosmos DB Data from Local to Azure
REM Make sure you have set Azure Cosmos DB credentials in .env file

echo ========================================
echo Cosmos DB Migration: Local to Azure
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create .env file with Azure Cosmos DB credentials:
    echo   COSMOS_ENDPOINT=https://your-account.documents.azure.com:443/
    echo   COSMOS_KEY=your_primary_key_here
    echo   COSMOS_DATABASE=qadam
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found
    echo Using system Python...
)

echo.
echo Checking dependencies...
echo.

REM Check if azure-cosmos is installed
python -c "import azure.cosmos" 2>nul
if errorlevel 1 (
    echo azure-cosmos package not found. Installing...
    pip install azure-cosmos==4.5.1
    if errorlevel 1 (
        echo ERROR: Failed to install azure-cosmos
        echo Please run: pip install azure-cosmos==4.5.1
        pause
        exit /b 1
    )
    echo azure-cosmos installed successfully!
) else (
    echo azure-cosmos package found!
)

echo.
echo Running migration script...
echo.

python migrate_local_to_azure_cosmos.py

echo.
echo ========================================
echo Migration script completed
echo ========================================
echo.
pause
