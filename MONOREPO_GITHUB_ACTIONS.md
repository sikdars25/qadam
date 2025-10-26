# 🔧 GitHub Actions for Monorepo

## Problem

Azure Function deployment fails because GitHub Actions looks for Python code in the repository root, but in a monorepo structure, the code is in `backend/` folder.

---

## ✅ Solution: Update GitHub Actions Workflow

### Key Changes for Monorepo

**1. Set correct package path:**
```yaml
env:
  AZURE_FUNCTIONAPP_PACKAGE_PATH: 'backend'  # Point to backend folder
```

**2. Trigger only on backend changes:**
```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'  # Only run when backend files change
```

**3. Use working-directory for all backend operations:**
```yaml
- name: Install dependencies
  working-directory: ${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
  run: pip install -r requirements.txt
```

**4. Zip only backend folder:**
```yaml
- name: Zip artifact for deployment
  working-directory: ${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
  run: zip -r ../backend-release.zip . -x "venv/*" -x ".git/*"
```

---

## 📁 Workflow File Location

**For Monorepo:**
```
qadam/
├── .github/
│   └── workflows/
│       ├── backend-deploy.yml    # Backend deployment
│       └── frontend-deploy.yml   # Frontend deployment (if needed)
├── backend/
│   ├── app.py
│   └── requirements.txt
└── frontend/
    ├── src/
    └── package.json
```

**Important:** Workflows go in **root** `.github/workflows/`, not in `backend/.github/`

---

## 🚀 Complete Backend Workflow

```yaml
name: Build and deploy Python project to Azure Function App - qadam-backend

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'
  workflow_dispatch:

env:
  AZURE_FUNCTIONAPP_PACKAGE_PATH: 'backend'
  PYTHON_VERSION: '3.10'

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python version
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Create and start virtual environment
        working-directory: ${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
        run: |
          python -m venv venv
          source venv/bin/activate

      - name: Install dependencies
        working-directory: ${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Zip artifact for deployment
        working-directory: ${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
        run: zip -r ../backend-release.zip . -x "venv/*" -x ".git/*" -x "__pycache__/*" -x "*.pyc"

      - name: Upload artifact for deployment job
        uses: actions/upload-artifact@v4
        with:
          name: python-app
          path: backend-release.zip

  deploy:
    runs-on: ubuntu-latest
    needs: build
    permissions:
      id-token: write
      contents: read

    steps:
      - name: Download artifact from build job
        uses: actions/download-artifact@v4
        with:
          name: python-app

      - name: Unzip artifact for deployment
        run: |
          unzip backend-release.zip -d backend-deploy
          rm backend-release.zip
        
      - name: Login to Azure
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZUREAPPSERVICE_CLIENTID }}
          tenant-id: ${{ secrets.AZUREAPPSERVICE_TENANTID }}
          subscription-id: ${{ secrets.AZUREAPPSERVICE_SUBSCRIPTIONID }}

      - name: 'Deploy to Azure Functions'
        uses: Azure/functions-action@v1
        id: deploy-to-function
        with:
          app-name: 'qadam-backend'
          slot-name: 'Production'
          package: backend-deploy
```

---

## 🔑 Key Differences from Single Repo

| Aspect | Single Repo | Monorepo |
|--------|-------------|----------|
| **Package Path** | `.` (root) | `backend` |
| **Trigger Paths** | All files | `backend/**` only |
| **Working Directory** | Not needed | `working-directory: backend` |
| **Zip Command** | `zip release.zip ./*` | `zip -r ../backend-release.zip .` |
| **Workflow Location** | `.github/workflows/` | `.github/workflows/` (root) |

---

## 📋 Setup Steps

### 1. Create Workflow Directory

```bash
cd d:/AI/_Programs/CBSE/aqnamic
mkdir -p .github/workflows
```

### 2. Copy Workflow File

Copy the provided `backend-deploy.yml` to `.github/workflows/`

### 3. Update Secrets

Make sure these secrets exist in your GitHub repository:
- `AZUREAPPSERVICE_CLIENTID_...`
- `AZUREAPPSERVICE_TENANTID_...`
- `AZUREAPPSERVICE_SUBSCRIPTIONID_...`

### 4. Remove Old Workflow

If you have `backend/.github/workflows/`, delete it:
```bash
rm -rf backend/.github
```

### 5. Commit and Push

```bash
git add .github/workflows/backend-deploy.yml
git commit -m "Fix: Update GitHub Actions for monorepo structure"
git push origin main
```

---

## 🧪 Test Deployment

### Trigger Workflow

**Option 1: Push backend changes**
```bash
# Make any change in backend/
echo "# Test" >> backend/README.md
git add backend/README.md
git commit -m "Test: Trigger backend deployment"
git push origin main
```

**Option 2: Manual trigger**
1. Go to GitHub → Actions
2. Select "Build and deploy Python project to Azure Function App"
3. Click "Run workflow"

---

## ✅ Verify Deployment

### Check GitHub Actions

1. Go to: `https://github.com/sikdars25/qadam/actions`
2. Look for the workflow run
3. Check each step for success ✅

### Check Azure Function

1. Go to Azure Portal → Function App
2. Check "Deployment Center" → "Logs"
3. Verify successful deployment

---

## 🎯 Benefits of Path-Based Triggers

```yaml
paths:
  - 'backend/**'
```

**Benefits:**
- ✅ Only deploys when backend changes
- ✅ Saves GitHub Actions minutes
- ✅ Faster CI/CD (no unnecessary runs)
- ✅ Frontend changes don't trigger backend deployment

**Example:**
- Push to `frontend/src/App.js` → No backend deployment
- Push to `backend/app.py` → Backend deploys ✅

---

## 🔧 Troubleshooting

### Error: "No such file or directory: requirements.txt"

**Cause:** Workflow is looking in root, not backend folder

**Fix:** Add `working-directory: backend` to the step

### Error: "Module not found" in Azure

**Cause:** Dependencies not installed or wrong folder deployed

**Fix:** Verify zip contains `app.py` and all dependencies

### Workflow doesn't trigger

**Cause:** Changes not in `backend/**` path

**Fix:** Make sure you're editing files inside `backend/` folder

---

## 📦 What Gets Deployed

**Included:**
- ✅ All `.py` files
- ✅ `requirements.txt`
- ✅ Configuration files
- ✅ `function.json` (if using Azure Functions)

**Excluded:**
- ❌ `venv/` (virtual environment)
- ❌ `.git/` (git files)
- ❌ `__pycache__/` (Python cache)
- ❌ `*.pyc` (compiled Python)

---

## 🎉 Result

After setup:
- ✅ Backend deploys from `backend/` folder
- ✅ Only triggers on backend changes
- ✅ Clean, organized monorepo
- ✅ Separate workflows for frontend/backend

---

**File created:** `.github/workflows/backend-deploy.yml`

**Next:** Commit and push to test deployment! 🚀
