# 🚀 OCR Service - Azure VM Deployment

## Current Status

✅ **All deployment files are ready in the `backend-ocr` branch!**

You are currently on the `backend-ocr` branch with all the necessary files to deploy the OCR service to an Azure VM.

---

## 📁 Available Files

### Deployment Files (in `ocr/` folder):
- ✅ `app.py` - Flask application wrapper
- ✅ `function_app.py` - Original Azure Functions code
- ✅ `deploy.sh` - Automated deployment script
- ✅ `qadam-ocr.service` - Systemd service configuration
- ✅ `nginx-ocr.conf` - Nginx reverse proxy configuration
- ✅ `requirements.txt` - Python dependencies

### Documentation:
- 📖 **`OCR_VM_QUICK_START.md`** ← **START HERE!** (5-step guide)
- 📖 `OCR_VM_DEPLOYMENT_GUIDE.md` (Complete documentation)
- 📖 `README.md` (Project overview)

### Automation:
- ⚙️ `.github/workflows/deploy-ocr-vm.yml` - GitHub Actions pipeline
- 🔧 `create-ocr-vm.sh` - VM creation script

---

## 🎯 Quick Start (3 Commands)

### 1. Create Azure VM
```bash
# Make script executable
chmod +x create-ocr-vm.sh

# Create VM (takes ~2 minutes)
./create-ocr-vm.sh
```

### 2. Setup GitHub Secrets
Go to: https://github.com/sikdars25/qadam/settings/secrets/actions

Add 3 secrets:
- `VM_HOST` = Your VM's public IP
- `VM_USERNAME` = `azureuser`
- `VM_SSH_KEY` = Your SSH private key (from `~/.ssh/id_rsa`)

### 3. Deploy
```bash
# The files are already pushed to backend-ocr branch
# Just trigger the workflow manually or make a change to ocr/ folder
git push origin backend-ocr
```

---

## 📚 Detailed Instructions

### Option 1: Quick Setup (Recommended)
👉 **Open `OCR_VM_QUICK_START.md`** for step-by-step instructions

### Option 2: Complete Guide
👉 **Open `OCR_VM_DEPLOYMENT_GUIDE.md`** for full documentation

---

## 🔍 What's Different from Azure Functions?

| Aspect | Azure Functions | Azure VM |
|--------|----------------|----------|
| **Package Size** | ❌ 450 MB (too large) | ✅ No limit |
| **Deployment** | ❌ Failed repeatedly | ✅ Works perfectly |
| **Cost** | 💰 $150+/month (Premium) | 💰 $30-40/month |
| **Control** | Limited | Full control |
| **Setup** | Complex | Simple |

---

## 🛠️ Architecture

```
GitHub (backend-ocr branch)
    ↓ (GitHub Actions)
Azure VM (Ubuntu 22.04)
    ↓ (Python + Flask)
OCR Service (Port 8000)
    ↓ (Nginx Reverse Proxy)
Public Access (Port 80)
```

---

## 📝 API Endpoints

Once deployed, your OCR service will be at: `http://<VM_IP>`

- `GET /api/health` - Health check
- `POST /api/extract-text` - Extract text from image
- `POST /api/extract-text-with-boxes` - Extract with bounding boxes
- `POST /api/extract-from-pdf` - Extract from PDF

---

## ✅ Checklist

Before you start:
- [ ] Have Azure account with active subscription
- [ ] Have Azure CLI installed (or use Azure Portal)
- [ ] Have SSH key pair (or will generate new one)
- [ ] Have GitHub account access to sikdars25/qadam

---

## 🆘 Need Help?

1. **Quick questions**: Check `OCR_VM_QUICK_START.md`
2. **Detailed info**: Check `OCR_VM_DEPLOYMENT_GUIDE.md`
3. **Troubleshooting**: See "Troubleshooting" section in the guides

---

## 🎉 Ready to Deploy?

**Next step**: Open `OCR_VM_QUICK_START.md` and follow the 5 steps!

---

## 💡 Why This Solution?

The original Azure Functions deployment failed because:
- PaddleOCR package is ~450 MB (too large for Consumption Plan)
- Azure Functions has strict size limits
- Remote build kept failing with "Malformed SCM_RUN_FROM_PACKAGE"

**Azure VM solution**:
- ✅ No package size limits
- ✅ Full control over environment
- ✅ Much cheaper than Functions Premium
- ✅ Simple deployment with GitHub Actions
- ✅ Production-ready with Nginx + Systemd

---

**Current Branch**: `backend-ocr`  
**Status**: Ready to deploy! 🚀
