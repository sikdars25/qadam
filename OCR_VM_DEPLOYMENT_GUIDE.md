# OCR Service - Azure VM Deployment Guide

## Why Azure VM Instead of Azure Functions?

**Problem**: PaddleOCR package is too large (~450 MB) for Azure Functions Consumption Plan
**Solution**: Deploy as a standalone Flask/FastAPI service on Azure VM

## Architecture

```
GitHub (backend-ocr branch)
    ↓
GitHub Actions Pipeline
    ↓
Azure VM (Ubuntu)
    ↓
Flask/FastAPI Service (Port 8000)
    ↓
Nginx Reverse Proxy (Port 80/443)
```

---

## Step 1: Create Azure VM

### Option A: Using Azure Portal

1. **Go to Azure Portal**: https://portal.azure.com
2. **Create Virtual Machine**:
   - Click "Create a resource" → "Virtual Machine"
   
3. **Basic Settings**:
   - **Subscription**: Your subscription
   - **Resource Group**: Create new or use existing (e.g., `rg-qadam`)
   - **VM Name**: `vm-qadam-ocr`
   - **Region**: Same as your other resources (e.g., East US)
   - **Image**: Ubuntu Server 22.04 LTS
   - **Size**: Standard_B2s (2 vCPUs, 4 GB RAM) - Minimum recommended
   - **Authentication**: SSH public key
   - **Username**: `azureuser`
   - **SSH Key**: Generate new or use existing

4. **Networking**:
   - **Virtual Network**: Create new or use existing
   - **Public IP**: Yes (create new)
   - **Inbound Ports**: 
     - SSH (22)
     - HTTP (80)
     - HTTPS (443)
     - Custom (8000) - for direct API access

5. **Review + Create** → Click "Create"

### Option B: Using Azure CLI

```bash
# Login to Azure
az login

# Create resource group (if not exists)
az group create --name rg-qadam --location eastus

# Create VM
az vm create \
  --resource-group rg-qadam \
  --name vm-qadam-ocr \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard

# Open ports
az vm open-port --resource-group rg-qadam --name vm-qadam-ocr --port 80 --priority 1000
az vm open-port --resource-group rg-qadam --name vm-qadam-ocr --port 443 --priority 1001
az vm open-port --resource-group rg-qadam --name vm-qadam-ocr --port 8000 --priority 1002

# Get public IP
az vm show --resource-group rg-qadam --name vm-qadam-ocr --show-details --query publicIps -o tsv
```

---

## Step 2: Initial VM Setup (Manual - One Time)

### Connect to VM

```bash
# Get the public IP from Azure Portal or CLI
ssh azureuser@<VM_PUBLIC_IP>
```

### Install Required Software

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install -y python3.10 python3.10-venv python3-pip

# Install Nginx
sudo apt install -y nginx

# Install Git
sudo apt install -y git

# Install system dependencies for OpenCV and PaddleOCR
sudo apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev

# Create application directory
sudo mkdir -p /opt/qadam-ocr
sudo chown azureuser:azureuser /opt/qadam-ocr
```

---

## Step 3: Setup GitHub Actions Deployment

### Create GitHub Secrets

Go to: https://github.com/sikdars25/qadam/settings/secrets/actions

Add these secrets:

1. **VM_HOST**: Your VM's public IP address
2. **VM_USERNAME**: `azureuser`
3. **VM_SSH_KEY**: Your private SSH key (the one that matches the public key on the VM)

To get your SSH private key:
```bash
# On your local machine (Windows)
cat ~/.ssh/id_rsa
# Copy the entire output including -----BEGIN and -----END lines
```

---

## Step 4: Create Deployment Files

### 4.1 Create Flask App Wrapper

Create `ocr/app.py`:

```python
"""
OCR Service - Flask Application
Runs the Azure Function App as a standalone Flask service
"""

from flask import Flask, request, jsonify
from function_app import (
    health_check,
    extract_text,
    extract_text_with_boxes,
    extract_from_pdf
)
import azure.functions as func

app = Flask(__name__)

def azure_func_to_flask(azure_func):
    """Convert Azure Function to Flask route"""
    def wrapper():
        # Create mock Azure Functions request
        req = func.HttpRequest(
            method=request.method,
            url=request.url,
            headers=dict(request.headers),
            body=request.get_data()
        )
        
        # Call Azure Function
        response = azure_func(req)
        
        # Convert Azure Functions response to Flask response
        return (
            response.get_body(),
            response.status_code,
            {'Content-Type': response.headers.get('Content-Type', 'application/json')}
        )
    return wrapper

# Health check
@app.route('/api/health', methods=['GET'])
def health():
    return azure_func_to_flask(health_check)()

# Extract text
@app.route('/api/extract-text', methods=['POST'])
def extract():
    return azure_func_to_flask(extract_text)()

# Extract with boxes
@app.route('/api/extract-text-with-boxes', methods=['POST'])
def extract_boxes():
    return azure_func_to_flask(extract_text_with_boxes)()

# Extract from PDF
@app.route('/api/extract-from-pdf', methods=['POST'])
def extract_pdf():
    return azure_func_to_flask(extract_from_pdf)()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

### 4.2 Create Systemd Service

Create `ocr/qadam-ocr.service`:

```ini
[Unit]
Description=Qadam OCR Service
After=network.target

[Service]
Type=simple
User=azureuser
WorkingDirectory=/opt/qadam-ocr
Environment="PATH=/opt/qadam-ocr/venv/bin"
ExecStart=/opt/qadam-ocr/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4.3 Create Nginx Configuration

Create `ocr/nginx-ocr.conf`:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for OCR processing
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        
        # Increase body size for image uploads
        client_max_body_size 50M;
    }
}
```

### 4.4 Create Deployment Script

Create `ocr/deploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Starting OCR Service Deployment..."

# Navigate to app directory
cd /opt/qadam-ocr

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git fetch origin backend-ocr
git reset --hard origin/backend-ocr

# Create/activate virtual environment
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3.10 -m venv venv
fi
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install flask gunicorn
pip install -r requirements.txt

# Setup systemd service
echo "⚙️  Configuring systemd service..."
sudo cp qadam-ocr.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable qadam-ocr
sudo systemctl restart qadam-ocr

# Setup Nginx
echo "🌐 Configuring Nginx..."
sudo cp nginx-ocr.conf /etc/nginx/sites-available/qadam-ocr
sudo ln -sf /etc/nginx/sites-available/qadam-ocr /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "✅ Deployment complete!"
echo "🔍 Service status:"
sudo systemctl status qadam-ocr --no-pager
echo ""
echo "🌐 OCR Service is running at: http://$(curl -s ifconfig.me)"
```

---

## Step 5: Create GitHub Actions Workflow

Create `.github/workflows/deploy-ocr-vm.yml`:

```yaml
name: Deploy OCR to Azure VM

on:
  push:
    branches:
      - backend-ocr
    paths:
      - 'ocr/**'
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.VM_SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.VM_HOST }} >> ~/.ssh/known_hosts

      - name: Initial setup (first time only)
        run: |
          ssh ${{ secrets.VM_USERNAME }}@${{ secrets.VM_HOST }} << 'EOF'
            if [ ! -d "/opt/qadam-ocr/.git" ]; then
              echo "🔧 First time setup..."
              cd /opt/qadam-ocr
              git init
              git remote add origin https://github.com/sikdars25/qadam.git
              git fetch origin backend-ocr
              git checkout backend-ocr
            fi
          EOF

      - name: Deploy to VM
        run: |
          ssh ${{ secrets.VM_USERNAME }}@${{ secrets.VM_HOST }} << 'EOF'
            cd /opt/qadam-ocr
            chmod +x deploy.sh
            ./deploy.sh
          EOF

      - name: Health check
        run: |
          sleep 10
          curl -f http://${{ secrets.VM_HOST }}/api/health || exit 1
          echo "✅ OCR Service is healthy!"

      - name: Deployment summary
        run: |
          echo "🎉 Deployment successful!"
          echo "📍 OCR Service URL: http://${{ secrets.VM_HOST }}"
          echo "🔍 Health Check: http://${{ secrets.VM_HOST }}/api/health"
```

---

## Step 6: Deploy!

### 6.1 Add deployment files to repository

```bash
# On your local machine
cd d:\AI\_Programs\CBSE\aqnamic
git checkout backend-ocr

# Create the new files (app.py, deploy.sh, etc.)
# Then commit
git add ocr/app.py ocr/deploy.sh ocr/qadam-ocr.service ocr/nginx-ocr.conf
git add .github/workflows/deploy-ocr-vm.yml
git commit -m "feat: add Azure VM deployment for OCR service"
git push origin backend-ocr
```

### 6.2 First Time Manual Setup on VM

```bash
# SSH to VM
ssh azureuser@<VM_PUBLIC_IP>

# Clone repository
cd /opt/qadam-ocr
git init
git remote add origin https://github.com/sikdars25/qadam.git
git fetch origin backend-ocr
git checkout backend-ocr

# Make deploy script executable
chmod +x deploy.sh

# Run first deployment
./deploy.sh
```

### 6.3 Verify Deployment

```bash
# Check service status
sudo systemctl status qadam-ocr

# Check logs
sudo journalctl -u qadam-ocr -f

# Test API
curl http://<VM_PUBLIC_IP>/api/health
```

---

## Step 7: Update Frontend to Use VM

Update your frontend to point to the VM instead of Azure Functions:

```javascript
// In your frontend config
const OCR_API_URL = 'http://<VM_PUBLIC_IP>/api';

// Or use environment variable
const OCR_API_URL = process.env.REACT_APP_OCR_API_URL || 'http://<VM_PUBLIC_IP>/api';
```

---

## Monitoring & Maintenance

### View Logs
```bash
# Service logs
sudo journalctl -u qadam-ocr -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Service
```bash
sudo systemctl restart qadam-ocr
sudo systemctl restart nginx
```

### Update Service
Just push to `backend-ocr` branch - GitHub Actions will auto-deploy!

---

## Cost Estimate

**Standard_B2s VM**: ~$30-40/month
- 2 vCPUs
- 4 GB RAM
- Sufficient for OCR workload

**vs Azure Functions Premium**: ~$150+/month

**Savings**: ~$110/month! 💰

---

## Next Steps

1. ✅ Create Azure VM
2. ✅ Setup GitHub Secrets
3. ✅ Create deployment files
4. ✅ Push to backend-ocr branch
5. ✅ Watch GitHub Actions deploy
6. ✅ Update frontend configuration
7. ✅ Test OCR endpoints

---

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u qadam-ocr -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8000

# Restart service
sudo systemctl restart qadam-ocr
```

### Nginx errors
```bash
# Test config
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log
```

### Python dependencies
```bash
cd /opt/qadam-ocr
source venv/bin/activate
pip install -r requirements.txt
```
