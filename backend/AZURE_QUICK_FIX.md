# ⚡ Azure Deployment Quick Fix

## Error
```
getaddrinfo ENOTFOUND undefined.blob.core.windows.net
```

## Fix (2 minutes)

### 1. Create Storage Account
- Portal: https://portal.azure.com
- Create resource → Storage account
- Name: `qadamstorage` (unique)
- Resource group: `qadam-resources`
- Region: East US
- Click: Create

### 2. Get Connection String
- Go to storage account
- Access keys → Copy "Connection string"

### 3. Configure Function App
- Go to Function App: `qadam-backend`
- Configuration → New application setting
- Name: `AzureWebJobsStorage`
- Value: [Paste connection string]
- Save → Continue

### 4. Retry Deployment
- GitHub → Actions → Re-run jobs

## Done! ✅

Storage account is required for Azure Functions runtime.
