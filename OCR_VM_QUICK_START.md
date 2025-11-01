# OCR Azure VM - Quick Start Guide

## 🚀 Quick Setup (5 Steps)

### Step 1: Create Azure VM

**Option A: Using the script (Recommended)**
```bash
# Make script executable
chmod +x create-ocr-vm.sh

# Run script
./create-ocr-vm.sh
```

**Option B: Manual via Azure Portal**
- Go to https://portal.azure.com
- Create VM → Ubuntu 22.04 LTS
- Size: Standard_B2s (2 vCPUs, 4 GB RAM)
- Open ports: 22, 80, 443, 8000

---

### Step 2: Setup GitHub Secrets

Go to: https://github.com/sikdars25/qadam/settings/secrets/actions

Add 3 secrets:

1. **VM_HOST**: `<Your VM Public IP>`
2. **VM_USERNAME**: `azureuser`
3. **VM_SSH_KEY**: 
   ```bash
   # Get your SSH private key
   cat ~/.ssh/id_rsa
   # Copy entire output including BEGIN/END lines
   ```

---

### Step 3: Initial VM Setup

```bash
# SSH to your VM
ssh azureuser@<VM_PUBLIC_IP>

# Run setup commands
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.10 python3.10-venv python3-pip nginx git
sudo apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev

# Create app directory
sudo mkdir -p /opt/qadam-ocr
sudo chown azureuser:azureuser /opt/qadam-ocr

# Clone repository
cd /opt/qadam-ocr
git init
git remote add origin https://github.com/sikdars25/qadam.git
git fetch origin backend-ocr
git checkout backend-ocr

# Run first deployment
chmod +x deploy.sh
./deploy.sh
```

---

### Step 4: Push Deployment Files

```bash
# On your local machine
cd d:\AI\_Programs\CBSE\aqnamic
git checkout backend-ocr
git push origin backend-ocr
```

This will trigger GitHub Actions to deploy automatically!

---

### Step 5: Verify Deployment

```bash
# Check service status
curl http://<VM_PUBLIC_IP>/api/health

# Should return:
# {"status": "healthy", "service": "OCR Service"}
```

---

## 📝 API Endpoints

Once deployed, your OCR service will be available at:

**Base URL**: `http://<VM_PUBLIC_IP>`

### Endpoints:

1. **Health Check**
   ```bash
   GET /api/health
   ```

2. **Extract Text from Image**
   ```bash
   POST /api/extract-text
   Content-Type: multipart/form-data
   Body: image file
   ```

3. **Extract Text with Bounding Boxes**
   ```bash
   POST /api/extract-text-with-boxes
   Content-Type: multipart/form-data
   Body: image file
   ```

4. **Extract Text from PDF**
   ```bash
   POST /api/extract-from-pdf
   Content-Type: multipart/form-data
   Body: PDF file
   ```

---

## 🔧 Troubleshooting

### Service not starting?
```bash
ssh azureuser@<VM_PUBLIC_IP>
sudo systemctl status qadam-ocr
sudo journalctl -u qadam-ocr -f
```

### Nginx issues?
```bash
sudo nginx -t
sudo systemctl restart nginx
sudo tail -f /var/log/nginx/error.log
```

### Redeploy manually
```bash
ssh azureuser@<VM_PUBLIC_IP>
cd /opt/qadam-ocr
./deploy.sh
```

---

## 💰 Cost

**Standard_B2s VM**: ~$30-40/month
- Much cheaper than Azure Functions Premium
- No package size limits
- Full control over environment

---

## 🎯 Next Steps

1. ✅ Update frontend to use VM URL
2. ✅ Setup custom domain (optional)
3. ✅ Add SSL certificate (optional)
4. ✅ Setup monitoring (optional)

---

## 📚 Full Documentation

See `OCR_VM_DEPLOYMENT_GUIDE.md` for complete documentation.
