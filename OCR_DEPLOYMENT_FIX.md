# OCR Deployment Fix - Nov 1, 2025

## Error Analysis

**Error:** `Failed to deploy web package to App Service. Not Found (CODE: 404)`

**Root Cause:** Azure Function App `qadam-ocr` does not exist or publish profile is incorrect.

## Solution Options

### Option 1: Create Dedicated OCR Function App (Recommended)

#### Step 1: Create Azure Function App
```bash
# Via Azure Portal:
1. Go to Azure Portal → Create Resource → Function App
2. Settings:
   - Name: qadam-ocr
   - Runtime: Python
   - Version: 3.10
   - Region: (same as qadam-backend)
   - Plan: Consumption (Serverless)
```

#### Step 2: Download Publish Profile
```
1. Go to Azure Portal → qadam-ocr Function App
2. Click "Get publish profile" button (top menu)
3. Save the downloaded .PublishSettings file
```

#### Step 3: Add GitHub Secret
```
1. Go to: https://github.com/sikdars25/qadam/settings/secrets/actions
2. Click "New repository secret"
3. Name: AZURE_OCR_FUNCTIONAPP_PUBLISH_PROFILE
4. Value: Paste entire contents of .PublishSettings file
5. Click "Add secret"
```

#### Step 4: Trigger Deployment
```bash
# Make a small change to ocr folder and push to backend-ocr branch
git checkout backend-ocr
echo "# OCR Function" >> ocr/README.md
git add ocr/README.md
git commit -m "deploy: trigger OCR function deployment"
git push origin backend-ocr
```

### Option 2: Deploy OCR to Existing Backend Function App

If you don't want a separate function app, you can merge OCR into the main backend:

#### Step 1: Copy OCR function to main backend
```bash
git checkout main
cp -r ocr/* backend/
```

#### Step 2: Update backend requirements.txt
Add OCR dependencies to `backend/requirements.txt`:
```
paddleocr
paddlepaddle
opencv-python-headless
Pillow
```

#### Step 3: Deploy
The existing backend workflow will deploy it automatically.

## Current Workflow Configuration

### deploy-ocr-function.yml (Correct)
- ✅ Deploys from `ocr/` folder
- ✅ Uses correct path: `AZURE_FUNCTIONAPP_PACKAGE_PATH: 'ocr'`
- ❌ Requires secret: `AZURE_OCR_FUNCTIONAPP_PUBLISH_PROFILE`
- ❌ Requires Function App: `qadam-ocr` to exist

### backend-ocr_qadam-ocr.yml (Old - Should be deleted)
- ❌ Deploys from root (`.`) instead of `ocr/`
- ❌ Uses old secret format
- Should be removed

## Recommended Action

1. **Create `qadam-ocr` Function App** in Azure Portal
2. **Add publish profile** to GitHub Secrets
3. **Delete old workflow** `backend-ocr_qadam-ocr.yml`
4. **Keep** `deploy-ocr-function.yml`

## Verification

After setup, verify:
```bash
# Check Function App exists
curl https://qadam-ocr.azurewebsites.net/api/health

# Check deployment logs
# Go to: https://github.com/sikdars25/qadam/actions
```

## Alternative: Disable OCR Deployment

If OCR is not needed, you can disable the workflow:
```bash
git checkout backend-ocr
rm .github/workflows/deploy-ocr-function.yml
rm .github/workflows/backend-ocr_qadam-ocr.yml
git commit -m "chore: disable OCR deployment workflows"
git push origin backend-ocr
```
