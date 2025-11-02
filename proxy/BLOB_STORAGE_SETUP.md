# Azure Blob Storage Setup Guide

## 🎯 Why Blob Storage?

Azure Function Apps have **ephemeral file systems** - uploaded files are deleted when the app restarts. Azure Blob Storage provides:

✅ **Persistent storage** - Files never get deleted  
✅ **Scalable** - Handle any number of files  
✅ **Fast** - Direct access from Azure  
✅ **Free tier** - 5 GB free storage  

## 📦 Step 1: Create Azure Storage Account

### Option A: Azure Portal (GUI)

1. Go to: https://portal.azure.com
2. Click **"Create a resource"**
3. Search for **"Storage account"**
4. Click **"Create"**

**Configuration:**
- **Subscription:** Your subscription
- **Resource Group:** Same as your Function App (e.g., `qadam-rg`)
- **Storage account name:** `qadamstorage` (must be globally unique, lowercase, no hyphens)
- **Region:** Same as Function App (e.g., `Central US`)
- **Performance:** Standard
- **Redundancy:** LRS (Locally-redundant storage) - cheapest option

5. Click **"Review + create"** → **"Create"**
6. Wait for deployment (~1 minute)

### Option B: Azure CLI (Command Line)

```bash
# Login to Azure
az login

# Create storage account
az storage account create \
  --name qadamstorage \
  --resource-group qadam-rg \
  --location centralus \
  --sku Standard_LRS

# Create blob container
az storage container create \
  --name qadam-uploads \
  --account-name qadamstorage \
  --public-access off
```

## 🔑 Step 2: Get Connection String

### Azure Portal:

1. Go to your Storage Account
2. Click **"Access keys"** (left sidebar)
3. Click **"Show"** next to **key1**
4. Copy the **"Connection string"**

It looks like:
```
DefaultEndpointsProtocol=https;AccountName=qadamstorage;AccountKey=xxxxx;EndpointSuffix=core.windows.net
```

### Azure CLI:

```bash
az storage account show-connection-string \
  --name qadamstorage \
  --resource-group qadam-rg
```

## ⚙️ Step 3: Configure Environment Variables

### Local Development (.env file):

Add to `backend/.env`:

```bash
# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=qadamstorage;AccountKey=xxxxx;EndpointSuffix=core.windows.net
BLOB_CONTAINER_NAME=qadam-uploads
```

### Azure Function App:

1. Go to: https://portal.azure.com
2. Navigate to: **Function App** → `qadam-backend`
3. Click: **Configuration** → **Application settings**
4. Click: **+ New application setting**

Add these two settings:

**Setting 1:**
- **Name:** `AZURE_STORAGE_CONNECTION_STRING`
- **Value:** (paste your connection string)

**Setting 2:**
- **Name:** `BLOB_CONTAINER_NAME`
- **Value:** `qadam-uploads`

5. Click **"Save"** → **"Continue"**

## 🧪 Step 4: Test Locally

```bash
cd backend

# Install new dependency
pip install azure-storage-blob==12.19.0

# Test blob storage
python -c "from blob_storage import check_blob_storage_available; check_blob_storage_available()"
```

Expected output:
```
✓ Blob storage is available
✓ Container 'qadam-uploads' already exists
✅ Azure Blob Storage enabled
```

## 🚀 Step 5: Deploy

```bash
git add .
git commit -m "Add Azure Blob Storage support"
git push origin main
```

## 📊 How It Works

### Before (Ephemeral Storage):
```
User uploads file → Saved to /home/site/wwwroot/uploads/
                  → ❌ Deleted on app restart
```

### After (Blob Storage):
```
User uploads file → Saved to Azure Blob Storage
                  → ✅ Persists forever
                  → Downloaded to temp when needed
```

## 🔧 File Flow

### Upload:
1. User uploads PDF/DOCX
2. Backend uploads to Blob Storage
3. Blob URL saved in Cosmos DB
4. File accessible anytime

### Processing:
1. Backend downloads blob to temp file
2. Processes file (OCR, parsing, etc.)
3. Deletes temp file
4. Original stays in Blob Storage

## 💰 Cost

**Free Tier:**
- 5 GB storage
- 20,000 read operations/month
- 2,000 write operations/month

**Typical Usage:**
- 1 PDF = ~2 MB
- 5 GB = ~2,500 PDFs
- Well within free tier!

## 🎯 Next Steps

After setup:

1. ✅ Create Storage Account
2. ✅ Get Connection String
3. ✅ Add to Azure Function App settings
4. ✅ Deploy code
5. ✅ Test file upload

Files will now persist forever! 🎉

## 🔍 Verify Setup

### Check if Blob Storage is working:

1. Upload a file through your app
2. Go to Azure Portal → Storage Account → Containers → `qadam-uploads`
3. You should see your uploaded file!

### Check logs:

```
✅ Azure Blob Storage enabled
✓ Container 'qadam-uploads' already exists
📤 Uploading to blob: papers/20251029_143022_test.pdf
✓ File uploaded successfully: https://qadamstorage.blob.core.windows.net/qadam-uploads/papers/20251029_143022_test.pdf
```

## ⚠️ Troubleshooting

### "AZURE_STORAGE_CONNECTION_STRING not configured"
- Make sure you added the connection string to Azure Function App settings
- Restart the Function App after adding settings

### "Container not found"
- The container is created automatically
- Check container name matches `BLOB_CONTAINER_NAME`

### "Authentication failed"
- Check connection string is correct
- Make sure you copied the entire string (it's long!)

## 📚 Additional Resources

- [Azure Blob Storage Docs](https://docs.microsoft.com/en-us/azure/storage/blobs/)
- [Python SDK Reference](https://docs.microsoft.com/en-us/python/api/azure-storage-blob/)
- [Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
