# Backend VM Setup Guide

## 🎯 Objective

Migrate the Qadam backend from Azure Functions to an Azure VM for better control, performance, and cost optimization.

## 📋 Prerequisites

- Azure VM: `130.107.48.166`
- SSH access to the VM
- GitHub repository access
- GitHub Secrets configured

## 🚀 Quick Start

### Step 1: Configure GitHub Secrets

Go to GitHub → Settings → Secrets and add:

```
BACKEND_VM_HOST=130.107.48.166
BACKEND_VM_USERNAME=qadamuser
BACKEND_VM_SSH_KEY=<your-ssh-private-key>
COSMOS_ENDPOINT=<your-cosmos-endpoint>
COSMOS_KEY=<your-cosmos-key>
COSMOS_DATABASE=qadam
AZURE_STORAGE_CONNECTION_STRING=<your-storage-connection>
OCR_SERVICE_URL=http://4.229.225.140
AI_SERVICE_URL=http://130.107.48.221:8001
SECRET_KEY=<generate-random-secret>
```

### Step 2: Prepare the VM

**SSH to the VM:**

```bash
ssh qadamuser@130.107.48.166
```

**Install dependencies:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Nginx
sudo apt install -y nginx

# Install Git
sudo apt install -y git

# Create app directory
sudo mkdir -p /opt/qadam-backend
sudo chown -R $USER:$USER /opt/qadam-backend
```

### Step 3: Deploy via GitHub Actions

**On your local machine:**

```bash
# Switch to backend-proxy branch
git checkout backend-proxy

# Push to trigger deployment
git push origin backend-proxy
```

GitHub Actions will automatically:
1. ✅ Clone the repository to the VM
2. ✅ Install Python dependencies
3. ✅ Create systemd service
4. ✅ Configure environment variables
5. ✅ Start the backend service

### Step 4: Configure Nginx

**On the VM:**

```bash
cd /opt/qadam-backend/proxy
chmod +x setup_nginx.sh
./setup_nginx.sh
```

### Step 5: Verify Deployment

```bash
# Check service status
sudo systemctl status qadam-backend

# Test health endpoint
curl http://localhost:5000/api/health
curl http://130.107.48.166/api/health

# Check logs
sudo journalctl -u qadam-backend -f
```

## 🔧 Manual Deployment (Alternative)

If GitHub Actions fails, deploy manually:

```bash
# SSH to VM
ssh qadamuser@130.107.48.166

# Clone repository
git clone -b backend-proxy https://github.com/sikdars25/qadam.git /opt/qadam-backend
cd /opt/qadam-backend/proxy

# Run deployment scripts
chmod +x deploy.sh setup_systemd.sh setup_nginx.sh
./deploy.sh

# Update .env file with your credentials
nano .env

# Setup systemd and Nginx
./setup_systemd.sh
./setup_nginx.sh
```

## 📊 Architecture

### Before (Azure Functions)
```
Frontend → Azure Functions (qadam-backend.azurewebsites.net)
           ├── OCR VM (4.229.225.140)
           └── AI VM (130.107.48.221)
```

### After (VM Deployment)
```
Frontend → Backend VM (130.107.48.166)
           ├── OCR VM (4.229.225.140)
           └── AI VM (130.107.48.221)
```

## ✅ Benefits

1. **Cost:** ~$30/month (VM) vs ~$100/month (Functions)
2. **Performance:** No cold starts, consistent response times
3. **Control:** Full control over environment and configuration
4. **Scalability:** Easy to scale vertically (upgrade VM size)
5. **Debugging:** Direct access to logs and processes

## 🔐 Security Checklist

- [ ] SSH key authentication (no password)
- [ ] Firewall configured (only ports 22, 80, 443)
- [ ] Environment variables in systemd (not in code)
- [ ] Regular security updates
- [ ] SSL certificate (optional, for HTTPS)

## 📈 Monitoring

```bash
# Service status
sudo systemctl status qadam-backend

# Real-time logs
sudo journalctl -u qadam-backend -f

# Memory usage
free -h
ps aux | grep gunicorn

# Disk space
df -h

# Network connections
sudo netstat -tlnp
```

## 🐛 Troubleshooting

### Issue: Service won't start

```bash
# Check logs
sudo journalctl -u qadam-backend -n 50 --no-pager

# Test manually
cd /opt/qadam-backend/proxy
source venv/bin/activate
python app.py
```

### Issue: 502 Bad Gateway

```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Check Nginx config
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart qadam-backend
sudo systemctl restart nginx
```

### Issue: GitHub Actions deployment fails

```bash
# Check GitHub Actions logs
# Verify GitHub Secrets are set correctly
# Ensure SSH key has correct permissions (600)
# Test SSH connection manually:
ssh -i ~/.ssh/id_rsa qadamuser@130.107.48.166
```

## 🔄 Updates

To update the backend:

```bash
# Option 1: Push to GitHub (automatic)
git push origin backend-proxy

# Option 2: Manual update on VM
cd /opt/qadam-backend
git pull origin backend-proxy
cd proxy
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart qadam-backend
```

## 📝 Next Steps

1. ✅ Deploy backend to VM
2. ✅ Update frontend to use new backend URL
3. ✅ Test all endpoints
4. ✅ Monitor performance
5. ✅ Decommission Azure Functions (after verification)
6. ⏳ Set up SSL certificate (optional)
7. ⏳ Configure automated backups
8. ⏳ Set up monitoring alerts

## 🎯 Success Criteria

- [ ] Backend service running on VM
- [ ] Health endpoint accessible
- [ ] OCR integration working
- [ ] AI integration working
- [ ] Database operations working
- [ ] File uploads working
- [ ] No errors in logs
- [ ] Response times < 2 seconds
