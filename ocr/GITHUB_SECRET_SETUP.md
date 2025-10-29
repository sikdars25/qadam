# GitHub Secret Setup for OCR Function App

## ❌ Error You're Seeing

```
Error: No credentials found. Add an Azure login action before this action.
```

This means the GitHub secret `AZURE_OCR_FUNCTIONAPP_PUBLISH_PROFILE` is not configured.

## ✅ Solution: Add Publish Profile as GitHub Secret

### Step 1: Create Azure Function App (if not exists)

**Option A: Azure Portal**
1. Go to https://portal.azure.com
2. Click **"Create a resource"**
3. Search for **"Function App"**
4. Fill in:
   - **Function App name:** `qadam-ocr`
   - **Runtime stack:** Python
   - **Version:** 3.10
   - **Region:** Central US (or your preferred region)
   - **Plan type:** Consumption (Serverless)
5. Click **"Review + Create"** → **"Create"**

**Option B: Azure CLI**
```bash
# Login to Azure
az login

# Create Function App
az functionapp create \
  --name qadam-ocr \
  --resource-group qadam-rg \
  --consumption-plan-location centralus \
  --runtime python \
  --runtime-version 3.10 \
  --functions-version 4 \
  --os-type Linux \
  --storage-account qadamstorage
```

### Step 2: Download Publish Profile

**Option A: Azure Portal**
1. Go to https://portal.azure.com
2. Navigate to **Function App** → **qadam-ocr**
3. Click **"Get publish profile"** (top menu bar)
4. Save the downloaded `.PublishSettings` file

**Option B: Azure CLI**
```bash
az functionapp deployment list-publishing-profiles \
  --name qadam-ocr \
  --resource-group qadam-rg \
  --xml > qadam-ocr.PublishSettings
```

### Step 3: Add GitHub Secret

1. Go to your GitHub repository: https://github.com/sikdars25/qadam
2. Click **"Settings"** (top menu)
3. Click **"Secrets and variables"** → **"Actions"** (left sidebar)
4. Click **"New repository secret"**
5. Fill in:
   - **Name:** `AZURE_OCR_FUNCTIONAPP_PUBLISH_PROFILE`
   - **Value:** Paste the **entire contents** of the `.PublishSettings` file
6. Click **"Add secret"**

### Step 4: Verify Secret is Set

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. You should see: `AZURE_OCR_FUNCTIONAPP_PUBLISH_PROFILE` in the list
3. ✅ Secret is configured!

### Step 5: Trigger Deployment

**Option A: Push to backend-ocr branch**
```bash
git checkout backend-ocr
# Make any change (or empty commit)
git commit --allow-empty -m "Trigger deployment"
git push origin backend-ocr
```

**Option B: Manual workflow dispatch**
1. Go to **Actions** tab in GitHub
2. Click **"Deploy OCR Function App"**
3. Click **"Run workflow"**
4. Select branch: `backend-ocr`
5. Click **"Run workflow"**

### Step 6: Monitor Deployment

1. Go to **Actions** tab
2. Click on the running workflow
3. Watch the deployment progress
4. ✅ Should see: "OCR Function App deployed successfully!"

## 🔍 Troubleshooting

### Secret not found error
- Make sure secret name is exactly: `AZURE_OCR_FUNCTIONAPP_PUBLISH_PROFILE`
- No typos, no extra spaces
- Secret must be in the repository where the workflow runs

### Invalid publish profile
- Download a fresh publish profile from Azure Portal
- Make sure you copied the **entire** file contents
- Check that the Function App name matches: `qadam-ocr`

### Function App doesn't exist
- Create the Function App first (Step 1)
- Make sure it's named exactly: `qadam-ocr`
- Verify it's in the correct resource group

## 📋 Quick Checklist

- [ ] Azure Function App `qadam-ocr` created
- [ ] Publish profile downloaded
- [ ] GitHub secret `AZURE_OCR_FUNCTIONAPP_PUBLISH_PROFILE` added
- [ ] Secret value contains full `.PublishSettings` file content
- [ ] Workflow triggered
- [ ] Deployment successful

## 🎯 Expected Result

After setup, when you push to `backend-ocr` branch:

```
✅ Publish profile found
✅ OCR Function App deployed successfully!
📦 Function App: qadam-ocr
🔗 URL: https://qadam-ocr.azurewebsites.net
```

## 📚 Related Documentation

- **Full Setup Guide:** `ocr/AZURE_SETUP.md`
- **API Documentation:** `ocr/README.md`
- **Workflow File:** `.github/workflows/deploy-ocr-function.yml`
