# 🔧 Fix: Azure Function Deployment Error

## Error

```
Error: getaddrinfo ENOTFOUND undefined.blob.core.windows.net
Warning: Neither AzureWebJobsStorage nor AzureWebJobsStorage__accountName exist
```

## Root Cause

Azure Functions requires a **Storage Account** for its runtime, but the `AzureWebJobsStorage` setting is not configured.

---

## ✅ Solution: Configure Storage Account

### Option 1: Using Azure Portal (Easiest)

#### Step 1: Create Storage Account

1. Go to **Azure Portal**: https://portal.azure.com
2. Click **Create a resource** → **Storage account**
3. Configure:
   - **Resource group:** `qadam-resources`
   - **Storage account name:** `qadamstorage` (must be globally unique)
   - **Region:** Same as Function App (e.g., East US)
   - **Performance:** Standard
   - **Redundancy:** LRS (Locally-redundant storage)
4. Click **Review + Create** → **Create**

#### Step 2: Get Connection String

1. Go to your new storage account
2. Click **Access keys** (left menu)
3. Copy **Connection string** from key1

#### Step 3: Configure Function App

1. Go to **Function App** → `qadam-backend`
2. Click **Configuration** (left menu)
3. Click **+ New application setting**
4. Add:
   - **Name:** `AzureWebJobsStorage`
   - **Value:** [Paste connection string from Step 2]
5. Click **OK** → **Save**
6. Click **Continue** to restart

---

### Option 2: Using Azure CLI (Automated)

Run the automated script:

```bash
fix_azure_storage.bat
```

This will:
1. Create a storage account
2. Get the connection string
3. Configure the Function App
4. Restart the app

---

### Option 3: Manual Azure CLI Commands

```bash
# Login
az login

# Create storage account
az storage account create \
  --name qadamstorage12345 \
  --resource-group qadam-resources \
  --location eastus \
  --sku Standard_LRS

# Get connection string
az storage account show-connection-string \
  --name qadamstorage12345 \
  --resource-group qadam-resources \
  --query connectionString -o tsv

# Configure Function App (replace CONNECTION_STRING with output from above)
az functionapp config appsettings set \
  --name qadam-backend \
  --resource-group qadam-resources \
  --settings AzureWebJobsStorage="CONNECTION_STRING"
```

---

## ✅ Verify Configuration

### Check in Azure Portal

1. Go to **Function App** → `qadam-backend`
2. Click **Configuration**
3. Look for **`AzureWebJobsStorage`** in Application settings
4. Should show: `DefaultEndpointsProtocol=https;AccountName=...`

### Retry Deployment

After configuring storage:

1. Go to **GitHub** → Your repository
2. Click **Actions** tab
3. Click **Re-run all jobs** on the failed workflow

---

## 📋 Complete Configuration Checklist

After fixing storage, ensure these settings exist in Function App:

### Required Settings:

- ✅ `AzureWebJobsStorage` - Storage connection string
- ✅ `MYSQL_HOST` - Azure MySQL hostname
- ✅ `MYSQL_USER` - MySQL username
- ✅ `MYSQL_PASSWORD` - MySQL password
- ✅ `MYSQL_DATABASE` - Database name
- ✅ `GROQ_API_KEY` - Groq API key
- ✅ `FUNCTIONS_WORKER_RUNTIME` - `python`
- ✅ `PYTHON_VERSION` - `3.10`

### Optional Settings:

- `SENDGRID_API_KEY` - For email functionality
- `SENDGRID_FROM_EMAIL` - Sender email

---

## 🎯 Quick Fix Steps

```bash
# 1. Create storage account in Azure Portal
# Name: qadamstorage (or any unique name)
# Copy connection string

# 2. Add to Function App Configuration
# Setting: AzureWebJobsStorage
# Value: [Paste connection string]

# 3. Save and restart Function App

# 4. Retry GitHub Actions deployment
```

---

## 🔍 Why This Happens

Azure Functions on **Consumption Plan** requires a storage account for:
- Function execution state
- Trigger management
- Logging and monitoring
- Deployment packages (when using WEBSITE_RUN_FROM_PACKAGE)

Without it, the deployment fails because it can't store the deployment package.

---

## 💡 Alternative: Use Existing Storage

If you already have a storage account:

1. Go to existing storage account
2. Get connection string
3. Add to Function App as `AzureWebJobsStorage`

---

## ✅ After Fix

Once configured, your deployment should succeed:

```
✓ Successfully acquired app settings
✓ Detected function app language: Python
✓ Will archive into package
✓ Deployment successful!
```

---

**Run:** `fix_azure_storage.bat` for automated setup! 🚀
