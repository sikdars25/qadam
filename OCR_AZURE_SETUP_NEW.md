# OCR Azure Function App Setup - New Deployment

## Issue
Created a new Azure Function App from `sikdars25/qadam/tree/backend-ocr/ocr` but GitHub Actions is not deploying.

## Solution

### Step 1: Download Publish Profile from New Function App

1. Go to Azure Portal: https://portal.azure.com
2. Navigate to your **new OCR Function App** (the one you just created)
3. Click **"Get publish profile"** button in the top menu
4. Save the downloaded `.PublishSettings` file

### Step 2: Update GitHub Secret

The workflow is looking for: `AZUREAPPSERVICE_PUBLISHPROFILE_06EB36677E9548B3B49251A055043C0E`

**Option A: Update Existing Secret** (Recommended)
1. Go to: https://github.com/sikdars25/qadam/settings/secrets/actions
2. Find: `AZUREAPPSERVICE_PUBLISHPROFILE_06EB36677E9548B3B49251A055043C0E`
3. Click **"Update"**
4. Paste the contents of the NEW publish profile
5. Click **"Update secret"**

**Option B: Create New Secret and Update Workflow**
1. Go to: https://github.com/sikdars25/qadam/settings/secrets/actions
2. Click **"New repository secret"**
3. Name: `AZURE_OCR_PUBLISHPROFILE_NEW`
4. Value: Paste entire contents of `.PublishSettings` file
5. Click **"Add secret"**
6. Update workflow file to use new secret name

### Step 3: Verify Function App Name

Make sure your new Function App is named: **`qadam-ocr`**

If it has a different name, you need to update the workflow:
- Edit `.github/workflows/backend-ocr_qadam-ocr.yml`
- Change `app-name: 'qadam-ocr'` to your actual Function App name

### Step 4: Trigger Deployment

After updating the secret, trigger a new deployment:

```bash
# Make a small change to trigger workflow
git checkout backend-ocr
echo "# Deployment trigger" >> ocr/README.md
git add ocr/README.md
git commit -m "deploy: trigger OCR deployment with new Function App"
git push origin backend-ocr
```

Or use **workflow_dispatch** (manual trigger):
1. Go to: https://github.com/sikdars25/qadam/actions
2. Click on "Build and deploy Python project to Azure Function App - qadam-ocr"
3. Click **"Run workflow"** button
4. Select branch: `backend-ocr`
5. Click **"Run workflow"**

### Step 5: Monitor Deployment

Watch the deployment:
- https://github.com/sikdars25/qadam/actions

### Step 6: Verify Deployment

After successful deployment, test:
```bash
curl https://your-function-app-name.azurewebsites.net/api/health
```

## Common Issues

### Issue 1: Workflow Not Triggering
**Cause**: Publish profile secret not set or incorrect
**Fix**: Update the secret with the new Function App's publish profile

### Issue 2: 404 Error During Deployment
**Cause**: Function App name mismatch
**Fix**: Ensure workflow `app-name` matches your actual Function App name

### Issue 3: Build Fails
**Cause**: Dependencies issue
**Fix**: Check that `ocr/requirements.txt` is correct

## Current Workflow Configuration

- **Workflow File**: `.github/workflows/backend-ocr_qadam-ocr.yml`
- **Trigger**: Push to `backend-ocr` branch
- **Secret**: `AZUREAPPSERVICE_PUBLISHPROFILE_06EB36677E9548B3B49251A055043C0E`
- **Function App**: `qadam-ocr`
- **Package Path**: `ocr/`

## Quick Checklist

- [ ] New Azure Function App created
- [ ] Downloaded publish profile from new Function App
- [ ] Updated GitHub secret with new publish profile
- [ ] Function App name matches workflow (`qadam-ocr`)
- [ ] Triggered new deployment
- [ ] Monitored GitHub Actions
- [ ] Verified deployment successful
