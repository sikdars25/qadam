# Azure OCR Function App Setup Guide

## 🎯 Quick Setup (5 minutes)

### Step 1: Create Azure Function App

```bash
# Login to Azure
az login

# Create Function App for OCR
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

### Step 2: Get Publish Profile

**Option A: Azure Portal**
1. Go to https://portal.azure.com
2. Navigate to Function App → `qadam-ocr`
3. Click **"Get publish profile"** (top menu)
4. Download the `.PublishSettings` file

**Option B: Azure CLI**
```bash
az functionapp deployment list-publishing-profiles \
  --name qadam-ocr \
  --resource-group qadam-rg \
  --xml > qadam-ocr.PublishSettings
```

### Step 3: Add GitHub Secret

1. Go to: https://github.com/YOUR_USERNAME/qadam/settings/secrets/actions
2. Click **"New repository secret"**
3. **Name:** `AZURE_OCR_FUNCTIONAPP_PUBLISH_PROFILE`
4. **Value:** Paste entire contents of `.PublishSettings` file
5. Click **"Add secret"**

### Step 4: Configure CORS

**Azure Portal:**
1. Go to Function App → `qadam-ocr`
2. Click **"CORS"** (left sidebar under API)
3. Add allowed origins:
   - `http://localhost:3000` (for local development)
   - `https://your-app.azurestaticapps.net` (your frontend URL)
   - `https://qadam-backend.azurewebsites.net` (main backend)
4. Click **"Save"**

**Azure CLI:**
```bash
az functionapp cors add \
  --name qadam-ocr \
  --resource-group qadam-rg \
  --allowed-origins \
    "http://localhost:3000" \
    "https://your-app.azurestaticapps.net" \
    "https://qadam-backend.azurewebsites.net"
```

### Step 5: Configure Environment Variables

**Azure Portal:**
1. Go to Function App → `qadam-ocr`
2. Click **"Configuration"** → **"Application settings"**
3. Add these settings:

| Name | Value |
|------|-------|
| `FRONTEND_URL` | `https://your-app.azurestaticapps.net` |
| `DEFAULT_OCR_LANGUAGE` | `en` |

4. Click **"Save"** → **"Continue"**

**Azure CLI:**
```bash
az functionapp config appsettings set \
  --name qadam-ocr \
  --resource-group qadam-rg \
  --settings \
    FRONTEND_URL="https://your-app.azurestaticapps.net" \
    DEFAULT_OCR_LANGUAGE="en"
```

### Step 6: Deploy

The GitHub Action will automatically deploy when you push changes to the `ocr/` folder:

```bash
# Already done - code is pushed!
# GitHub Actions will deploy automatically when ocr/ folder changes
```

Check deployment status:
- Go to: https://github.com/YOUR_USERNAME/qadam/actions
- Look for "Deploy OCR Function App" workflow

### Step 7: Update Main Backend

Add OCR service URL to main backend configuration:

**Azure Portal (Main Backend):**
1. Go to Function App → `qadam-backend`
2. Click **"Configuration"** → **"Application settings"**
3. Add:
   - **Name:** `OCR_SERVICE_URL`
   - **Value:** `https://qadam-ocr.azurewebsites.net`
4. Click **"Save"**

**Local (.env):**
```bash
OCR_SERVICE_URL=https://qadam-ocr.azurewebsites.net
```

### Step 8: Test

```bash
# Test health endpoint
curl https://qadam-ocr.azurewebsites.net/api/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "OCR Function App",
#   "ocr_engine": "PaddleOCR"
# }
```

## ✅ Verification Checklist

- [ ] Function App created (`qadam-ocr`)
- [ ] Publish profile added to GitHub secrets
- [ ] CORS configured
- [ ] Environment variables set
- [ ] GitHub Action deployed successfully
- [ ] Health endpoint returns 200
- [ ] Main backend has `OCR_SERVICE_URL` configured

## 🎯 Usage from Main Backend

```python
from ocr_client import ocr_image, ocr_pdf

# OCR an image
result = ocr_image(image_file, language='en')
if result['success']:
    text = result['text']
    confidence = result['confidence']

# OCR a PDF
result = ocr_pdf(pdf_file, language='en')
if result['success']:
    full_text = result['text']
    pages = result['pages']
```

## 🐛 Troubleshooting

### GitHub Action fails
- Check if `AZURE_OCR_FUNCTIONAPP_PUBLISH_PROFILE` secret is set correctly
- Verify publish profile is for `qadam-ocr` (not `qadam-backend`)

### CORS errors
- Add your frontend URL to CORS settings
- Include both http://localhost:3000 and production URL

### OCR service not responding
- Check Function App logs in Azure Portal
- Verify Function App is running (not stopped)
- First request takes 10-15 seconds (cold start)

### "Module not found" errors
- Wait for deployment to complete (~5 minutes)
- Check GitHub Actions for deployment errors
- Verify requirements.txt is correct

## 💰 Cost Estimate

**Azure Function App (Consumption Plan):**
- First 1 million executions: **FREE**
- 400,000 GB-s memory: **FREE**

**Typical Usage:**
- 1000 OCR requests/month
- ~5 seconds per request
- ~1 GB memory per request

**Total: $0/month** (well within free tier!)

## 📊 Performance

- **Cold Start:** 10-15 seconds (first request after idle)
- **Warm Start:** 1-2 seconds
- **OCR Processing:** 2-5 seconds per image
- **PDF Processing:** 3-6 seconds per page

**Tip:** Keep function warm with periodic health checks:
```bash
# Cron job every 5 minutes
*/5 * * * * curl https://qadam-ocr.azurewebsites.net/api/health
```

## 🔗 Useful Links

- **Function App:** https://portal.azure.com/#resource/subscriptions/.../resourceGroups/qadam-rg/providers/Microsoft.Web/sites/qadam-ocr
- **GitHub Actions:** https://github.com/YOUR_USERNAME/qadam/actions
- **Logs:** Function App → Log stream (in Azure Portal)
- **Metrics:** Function App → Metrics

## 🎉 Done!

Your OCR Function App is now deployed and ready to use! 🚀
