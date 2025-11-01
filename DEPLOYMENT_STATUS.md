# Deployment Status & Next Steps

## 🎯 Current Status

### ✅ Completed

1. **OCR Service on VM** (IP: TBD)
   - Flask app created
   - Deployment scripts ready
   - Systemd service configured
   - Status: **Needs deployment to VM**

2. **AI Service on VM** (IP: 130.107.48.221)
   - Flask app created
   - Deployment scripts ready
   - Systemd service configured
   - Status: **Needs deployment to VM**

3. **Backend Code Updated**
   - OCR client updated to call VM
   - AI client created to call VM
   - Code pushed to GitHub
   - Status: **Needs Azure deployment**

### 🔄 Pending Deployments

#### 1. Deploy Backend to Azure Functions

**Status:** Code is pushed but not deployed yet

**Action Required:**
The GitHub Actions workflow should deploy automatically. Check:
https://github.com/sikdars25/qadam/actions

**Manual Deploy (if needed):**
```bash
# Trigger deployment by making a small change
cd backend
echo "# Deployment trigger" >> .deploy-trigger
git add .deploy-trigger
git commit -m "deploy: trigger backend deployment"
git push origin main
```

#### 2. Deploy AI Service to VM (130.107.48.221)

**Status:** Ready to deploy

**Steps:**
```bash
# SSH to VM
ssh qadamuser@130.107.48.221

# Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx git build-essential python3-dev

# Setup application
sudo mkdir -p /opt/qadam-ai
sudo chown qadamuser:qadamuser /opt/qadam-ai
cd /opt/qadam-ai
git init
git remote add origin https://github.com/sikdars25/qadam.git
git fetch origin backend-ai
git checkout backend-ai

# Set Groq API Key
nano ai/qadam-ai.service
# Update: Environment="GROQ_API_KEY=your_actual_key"

# Deploy
chmod +x ai/deploy.sh
./ai/deploy.sh
```

#### 3. Deploy OCR Service to VM (IP: TBD)

**Status:** Ready to deploy (already deployed if you ran deploy.sh earlier)

**Verify:**
```bash
ssh qadamuser@<OCR_VM_IP>
sudo systemctl status qadam-ocr
curl http://<OCR_VM_IP>/api/health
```

### 🔧 Configuration Required

#### Backend Azure Functions

Set environment variables:
```bash
# OCR Service URL
az functionapp config appsettings set \
  --name qadam-backend \
  --resource-group qadam_bend_group \
  --settings OCR_SERVICE_URL=http://<OCR_VM_IP>

# AI Service URL
az functionapp config appsettings set \
  --name qadam-backend \
  --resource-group qadam_bend_group \
  --settings AI_SERVICE_URL=http://130.107.48.221
```

### ✅ Verification Steps

After all deployments:

**1. Test OCR Service:**
```bash
curl http://<OCR_VM_IP>/api/health
```

**2. Test AI Service:**
```bash
curl http://130.107.48.221/api/health
```

**3. Test Backend Integration:**
```bash
# Test OCR via backend
curl -X POST https://qadam-backend.azurewebsites.net/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{"question_text": "What is 2+2?", "subject": "Math"}'
```

### 📊 Architecture

```
┌─────────────┐
│   Frontend  │
│  (Static)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Backend (Azure)    │
│  qadam-backend      │
└──────┬──────┬───────┘
       │      │
       │      └──────────────┐
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│  OCR VM      │      │   AI VM      │
│  (Flask)     │      │  (Flask)     │
│  Port 8000   │      │  Port 8001   │
└──────────────┘      └──────┬───────┘
                             │
                             ▼
                      ┌──────────────┐
                      │  Groq API    │
                      │  (LLM)       │
                      └──────────────┘
```

### 🐛 Current Issue

**Error:** `Groq API not initialized. Please set GROQ_API_KEY.`

**Cause:** Backend deployment hasn't completed yet. The old code is still running.

**Solution:** Wait for GitHub Actions to deploy the new backend code, or trigger it manually.

### 📝 Next Immediate Steps

1. ✅ **Check backend deployment:** https://github.com/sikdars25/qadam/actions
2. 🔄 **Deploy AI service to VM:** Follow steps above for 130.107.48.221
3. 🔄 **Set environment variables:** Configure OCR_SERVICE_URL and AI_SERVICE_URL
4. ✅ **Test integration:** Verify all services are connected

---

**Last Updated:** November 1, 2025 8:34 PM IST
