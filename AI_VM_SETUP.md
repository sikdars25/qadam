# AI Service - Azure VM Deployment Guide

## 🎯 Overview

Deploy the AI service (question solving, text generation, semantic search) from the `backend-ai` branch to Azure VM at **130.107.48.221**.

## 📋 Prerequisites

- Azure VM with Ubuntu 24.04
- Public IP: **130.107.48.221**
- SSH access configured
- User: `qadamuser`
- Groq API Key

## 🚀 Quick Start

### 1. SSH to VM

```bash
ssh qadamuser@130.107.48.221
```

### 2. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and required packages
sudo apt install -y python3 python3-venv python3-pip nginx git

# Install Python build dependencies
sudo apt install -y build-essential python3-dev
```

### 3. Create Application Directory

```bash
# Create directory
sudo mkdir -p /opt/qadam-ai
sudo chown qadamuser:qadamuser /opt/qadam-ai

# Clone repository
cd /opt/qadam-ai
git init
git remote add origin https://github.com/sikdars25/qadam.git
git fetch origin backend-ai
git checkout backend-ai
```

### 4. Set Environment Variables

```bash
# Create environment file
sudo nano /etc/environment

# Add this line (replace with your actual Groq API key):
GROQ_API_KEY=your_groq_api_key_here

# Reload environment
source /etc/environment
```

Or set it in the systemd service file directly (more secure):

```bash
# Edit the service file after deployment
sudo nano /etc/systemd/system/qadam-ai.service

# Update the Environment line:
Environment="GROQ_API_KEY=your_actual_api_key"
```

### 5. Run Deployment Script

```bash
cd /opt/qadam-ai
chmod +x ai/deploy.sh
./ai/deploy.sh
```

## 🔧 Manual Deployment Steps

If the script fails, follow these manual steps:

### 1. Setup Python Environment

```bash
cd /opt/qadam-ai/ai
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Setup Systemd Service

```bash
sudo cp qadam-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable qadam-ai
sudo systemctl start qadam-ai
```

### 3. Setup Nginx

```bash
sudo cp nginx-ai.conf /etc/nginx/sites-available/qadam-ai
sudo ln -sf /etc/nginx/sites-available/qadam-ai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

## ✅ Verify Deployment

### Check Service Status

```bash
sudo systemctl status qadam-ai
```

### Check Logs

```bash
sudo journalctl -u qadam-ai -f
```

### Test API

```bash
# Health check
curl http://130.107.48.221/api/health

# Should return:
# {
#   "status": "healthy",
#   "service": "AI Service (Flask on VM)",
#   "features": {...}
# }
```

### Test Question Solving

```bash
curl -X POST http://130.107.48.221/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "What is the capital of France?",
    "subject": "Geography"
  }'
```

## 📝 API Endpoints

All endpoints are available at `http://130.107.48.221`

- `GET /api/health` - Health check
- `POST /api/solve-question` - Solve academic questions
- `POST /api/generate-text` - Generate text with Groq
- `POST /api/semantic-search` - Semantic search on documents
- `POST /api/parse-questions` - Parse questions from text
- `POST /api/map-to-chapters` - Map questions to chapters

## 🔄 Update Deployment

To update the service with new code:

```bash
ssh qadamuser@130.107.48.221
cd /opt/qadam-ai
./ai/deploy.sh
```

## 🐛 Troubleshooting

### Service not starting?

```bash
sudo systemctl status qadam-ai
sudo journalctl -u qadam-ai -n 50
```

### Nginx issues?

```bash
sudo nginx -t
sudo systemctl restart nginx
sudo tail -f /var/log/nginx/error.log
```

### Python import errors?

```bash
cd /opt/qadam-ai/ai
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart qadam-ai
```

### Groq API errors?

Check if GROQ_API_KEY is set:
```bash
sudo systemctl show qadam-ai | grep GROQ_API_KEY
```

## 🔐 Security Notes

- The Groq API key is stored in the systemd service file
- Nginx is configured to allow CORS for development
- For production, restrict CORS to specific domains
- Consider using HTTPS with Let's Encrypt

## 📊 Monitoring

```bash
# View real-time logs
sudo journalctl -u qadam-ai -f

# Check resource usage
htop

# Check network connections
sudo netstat -tulpn | grep 8001
```

## 🎉 Success!

Your AI service should now be running at:
- **URL**: http://130.107.48.221
- **Health**: http://130.107.48.221/api/health
- **Port**: 8001 (proxied through Nginx on port 80)
