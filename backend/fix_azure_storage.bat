@echo off
REM Fix Azure Function Storage Configuration
REM This script configures the required AzureWebJobsStorage setting

echo ========================================
echo   Fix Azure Function Storage
echo ========================================
echo.

echo This script will configure the storage account for your Azure Function.
echo.

set FUNCTION_APP_NAME=qadam-backend
set RESOURCE_GROUP=qadam_bend_group

echo Function App: %FUNCTION_APP_NAME%
echo Resource Group: %RESOURCE_GROUP%
echo.

REM Check if Azure CLI is installed
where az >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Azure CLI not found!
    echo Please install Azure CLI from: https://aka.ms/installazurecliwindows
    pause
    exit /b 1
)

echo [OK] Azure CLI found
echo.

REM Login to Azure
echo Logging in to Azure...
az login

if errorlevel 1 (
    echo [ERROR] Azure login failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Step 1: Create Storage Account
echo ========================================
echo.

set STORAGE_ACCOUNT_NAME=qadamstorage%RANDOM%

echo Creating storage account: %STORAGE_ACCOUNT_NAME%
echo.

az storage account create ^
  --name %STORAGE_ACCOUNT_NAME% ^
  --resource-group %RESOURCE_GROUP% ^
  --location eastus ^
  --sku Standard_LRS

if errorlevel 1 (
    echo [ERROR] Failed to create storage account
    pause
    exit /b 1
)

echo [OK] Storage account created
echo.

REM Get storage connection string
echo Getting storage connection string...
for /f "delims=" %%i in ('az storage account show-connection-string --name %STORAGE_ACCOUNT_NAME% --resource-group %RESOURCE_GROUP% --query connectionString -o tsv') do set STORAGE_CONNECTION_STRING=%%i

echo.
echo ========================================
echo   Step 2: Configure Function App
echo ========================================
echo.

echo Setting AzureWebJobsStorage...
az functionapp config appsettings set ^
  --name %FUNCTION_APP_NAME% ^
  --resource-group %RESOURCE_GROUP% ^
  --settings AzureWebJobsStorage="%STORAGE_CONNECTION_STRING%"

if errorlevel 1 (
    echo [ERROR] Failed to set storage connection
    pause
    exit /b 1
)

echo [OK] Storage configured
echo.

echo ========================================
echo   Configuration Complete!
echo ========================================
echo.
echo Storage Account: %STORAGE_ACCOUNT_NAME%
echo Function App: %FUNCTION_APP_NAME%
echo.
echo Next steps:
echo   1. Retry GitHub Actions deployment
echo   2. Or deploy manually: func azure functionapp publish %FUNCTION_APP_NAME%
echo.

pause
