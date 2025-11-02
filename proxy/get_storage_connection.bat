@echo off
REM Get Storage Account Connection String

echo ========================================
echo   Get Storage Connection String
echo ========================================
echo.

set /p STORAGE_NAME="Enter storage account name [qadamstorage]: "
if "%STORAGE_NAME%"=="" set STORAGE_NAME=qadamstorage

set /p RESOURCE_GROUP="Enter resource group [qadam-resources]: "
if "%RESOURCE_GROUP%"=="" set RESOURCE_GROUP=qadam-resources

echo.
echo Storage Account: %STORAGE_NAME%
echo Resource Group: %RESOURCE_GROUP%
echo.

REM Check if Azure CLI is installed
where az >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Azure CLI not found!
    echo.
    echo Please install from: https://aka.ms/installazurecliwindows
    echo.
    echo Or get connection string manually:
    echo   1. Go to Azure Portal
    echo   2. Open storage account: %STORAGE_NAME%
    echo   3. Click "Access keys" in left menu
    echo   4. Under key1, click "Show" next to Connection string
    echo   5. Click Copy button
    echo.
    pause
    exit /b 1
)

echo Logging in to Azure...
az login

if errorlevel 1 (
    echo [ERROR] Login failed
    pause
    exit /b 1
)

echo.
echo Getting connection string...
echo.
echo ========================================

az storage account show-connection-string ^
  --name %STORAGE_NAME% ^
  --resource-group %RESOURCE_GROUP% ^
  --query connectionString ^
  -o tsv

echo ========================================
echo.
echo Copy the connection string above.
echo.
echo Next steps:
echo   1. Go to Azure Portal
echo   2. Open Function App: qadam-backend
echo   3. Click Configuration
echo   4. Add new setting:
echo      Name: AzureWebJobsStorage
echo      Value: [Paste connection string]
echo   5. Save
echo.

pause
