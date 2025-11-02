# Database Connection Fix Guide

## 🚨 Problem

"Failed to delete paper - database unavailable" error when trying to delete papers in Upload Resources screen.

## 🔍 Root Cause

The backend on the VM doesn't have Cosmos DB credentials configured. The systemd service isn't loading the `.env` file with database credentials.

## ✅ Solution

Configure environment variables so the backend can connect to Cosmos DB.

## 🚀 Quick Fix

### On Backend VM (130.107.48.166):

```bash
# SSH to VM
ssh qadamuser@130.107.48.166

# Navigate to directory
cd /opt/qadam-backend

# Pull latest changes
git pull origin backend-proxy

# Navigate to proxy folder
cd proxy

# Create .env file with your credentials
cp .env.example .env
nano .env
```

### Edit .env file:

```bash
# Cosmos DB Configuration
COSMOS_ENDPOINT=https://your-cosmos-account.documents.azure.com:443/
COSMOS_KEY=your-primary-key-here
COSMOS_DATABASE=qadam

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...

# External Services
OCR_SERVICE_URL=http://4.229.225.140
AI_SERVICE_URL=http://130.107.48.221:8001

# Flask Configuration
SECRET_KEY=your-random-secret-key-here
FLASK_ENV=production
BACKEND_HTTPS=true

# Frontend URL
FRONTEND_URL=https://zealous-ocean-06e22b51e.3.azurestaticapps.net
```

**Save and exit:** Ctrl+X, then Y, then Enter

### Run the fix:

```bash
# Make script executable
chmod +x fix_database.sh

# Run the fix
./fix_database.sh
```

## 📋 What the Fix Does

1. ✅ Checks if `.env` file exists
2. ✅ Updates systemd service to load `.env` file
3. ✅ Reloads systemd daemon
4. ✅ Restarts backend service
5. ✅ Shows service status

## 🔍 Get Your Cosmos DB Credentials

### From Azure Portal:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Cosmos DB account
3. Click **Keys** in the left menu
4. Copy:
   - **URI** → `COSMOS_ENDPOINT`
   - **PRIMARY KEY** → `COSMOS_KEY`

### From Azure CLI:

```bash
# Get endpoint
az cosmosdb show --name your-cosmos-account --resource-group your-rg --query documentEndpoint -o tsv

# Get key
az cosmosdb keys list --name your-cosmos-account --resource-group your-rg --query primaryMasterKey -o tsv
```

## 🧪 Verify Fix

### 1. Check Service Logs:

```bash
sudo journalctl -u qadam-backend -f
```

**Look for:**
```
✓ Connected to Cosmos DB: https://your-cosmos.documents.azure.com:443/
✓ Database 'qadam' ready
✓ Container 'uploaded_papers' ready
✓ Container 'parsed_questions' ready
✅ Cosmos DB enabled
```

### 2. Test from Frontend:

1. Go to **Upload Resources** screen
2. Try to **delete a paper**
3. Should work without "database unavailable" error

### 3. Check Database:

```bash
# Test health endpoint
curl -k https://localhost:5000/api/health

# Should show Cosmos DB is enabled
```

## 🐛 Troubleshooting

### Issue: "COSMOS_ENDPOINT not found"

**Solution:** Check .env file exists and has correct format

```bash
cd /opt/qadam-backend/proxy
cat .env | grep COSMOS
```

Should show your Cosmos DB settings.

### Issue: "Authentication failed"

**Solution:** Verify Cosmos DB key is correct

```bash
# Test connection manually
python3 << 'EOF'
from azure.cosmos import CosmosClient
import os
from dotenv import load_dotenv

load_dotenv()
endpoint = os.getenv('COSMOS_ENDPOINT')
key = os.getenv('COSMOS_KEY')

try:
    client = CosmosClient(endpoint, key)
    print(f"✅ Connected to: {endpoint}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
EOF
```

### Issue: "Container not found"

**Solution:** Initialize Cosmos DB containers

```bash
cd /opt/qadam-backend/proxy
source venv/bin/activate
python3 << 'EOF'
from cosmos_db import init_cosmos_db
init_cosmos_db()
EOF
```

### Issue: Service won't start

```bash
# Check service status
sudo systemctl status qadam-backend

# Check logs
sudo journalctl -u qadam-backend -n 50 --no-pager

# Verify .env file permissions
ls -la .env

# Should be readable by qadamuser
chmod 600 .env
chown qadamuser:qadamuser .env
```

## 📊 Alternative: Use Interactive Setup

If you prefer an interactive setup:

```bash
cd /opt/qadam-backend/proxy
chmod +x setup_env.sh
./setup_env.sh
```

This will prompt you for each credential and create the .env file automatically.

## 🔐 Security Notes

1. **Never commit .env file to git** (it's in .gitignore)
2. **Restrict file permissions:**
   ```bash
   chmod 600 .env
   chown qadamuser:qadamuser .env
   ```
3. **Use Azure Key Vault** for production (optional)

## 📝 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `COSMOS_ENDPOINT` | Cosmos DB endpoint URL | `https://qadam.documents.azure.com:443/` |
| `COSMOS_KEY` | Cosmos DB primary key | `your-64-char-key==` |
| `COSMOS_DATABASE` | Database name | `qadam` |
| `AZURE_STORAGE_CONNECTION_STRING` | Blob storage connection | `DefaultEndpointsProtocol=https;...` |
| `OCR_SERVICE_URL` | OCR VM URL | `http://4.229.225.140` |
| `AI_SERVICE_URL` | AI VM URL | `http://130.107.48.221:8001` |
| `SECRET_KEY` | Flask secret key | Random 32-byte hex string |
| `BACKEND_HTTPS` | Enable HTTPS mode | `true` |

## 🎯 Quick Commands

```bash
# On VM
cd /opt/qadam-backend
git pull origin backend-proxy
cd proxy

# Create .env file
cp .env.example .env
nano .env  # Add your credentials

# Run fix
chmod +x fix_database.sh
./fix_database.sh

# Check logs
sudo journalctl -u qadam-backend -f

# Test
curl -k https://localhost:5000/api/health
```

## ✅ Success Criteria

- [ ] `.env` file created with correct credentials
- [ ] Service starts without errors
- [ ] Logs show "Connected to Cosmos DB"
- [ ] Can delete papers from frontend
- [ ] No "database unavailable" errors

**After applying the fix, database operations should work!** 🎉
