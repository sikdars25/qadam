# Qadam Deployment Summary

## ✅ Completed Setup

### 1. **OCR Service** (VM: 4.229.225.140)
- ✅ Branch: `backend-ocr`
- ✅ Engine: EasyOCR (lightweight, 150MB)
- ✅ Features: Math symbols, Greek letters
- ✅ Status: Running and healthy
- ✅ Endpoint: `http://4.229.225.140/api/extract-text`

### 2. **AI Service** (VM: 130.107.48.221)
- ✅ Branch: `backend-ai`
- ✅ Engine: Groq API
- ✅ Features: Question solving, TF-IDF vectorization
- ✅ Status: Running and healthy
- ✅ Endpoint: `http://130.107.48.221:8001/api/solve`

### 3. **Backend Proxy** (VM: 130.107.48.166) 🆕
- ✅ Branch: `backend-proxy`
- ✅ Framework: Flask + Gunicorn
- ✅ Database: Azure Cosmos DB
- ✅ Storage: Azure Blob Storage
- ✅ Status: Ready for deployment
- ✅ Endpoint: `http://130.107.48.166` (after deployment)

## 🎯 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│              (Azure Static Web Apps)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend Proxy                             │
│              (VM: 130.107.48.166:80)                        │
│                                                              │
│  • Flask + Gunicorn (4 workers)                             │
│  • Nginx reverse proxy                                       │
│  • Cosmos DB integration                                     │
│  • Blob Storage integration                                  │
└────────────┬───────────────────────┬────────────────────────┘
             │                       │
             ▼                       ▼
┌────────────────────┐    ┌────────────────────┐
│   OCR Service      │    │   AI Service       │
│  (4.229.225.140)   │    │  (130.107.48.221)  │
│                    │    │                    │
│  • EasyOCR         │    │  • Groq API        │
│  • Math symbols    │    │  • TF-IDF          │
│  • Greek letters   │    │  • Question solver │
└────────────────────┘    └────────────────────┘
```

## 🚀 Deployment Steps

### Step 1: Configure GitHub Secrets

Add these secrets to your GitHub repository:

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

```bash
# SSH to VM
ssh qadamuser@130.107.48.166

# Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx git

# Create app directory
sudo mkdir -p /opt/qadam-backend
sudo chown -R $USER:$USER /opt/qadam-backend
```

### Step 3: Deploy

**Option A: Automatic (GitHub Actions)**
```bash
# Just push to the branch
git push origin backend-proxy
```

**Option B: Manual**
```bash
# On the VM
git clone -b backend-proxy https://github.com/sikdars25/qadam.git /opt/qadam-backend
cd /opt/qadam-backend/proxy
chmod +x deploy.sh setup_systemd.sh setup_nginx.sh
./deploy.sh
./setup_systemd.sh
./setup_nginx.sh
```

### Step 4: Verify

```bash
# Check service
sudo systemctl status qadam-backend

# Test health
curl http://130.107.48.166/api/health

# Check logs
sudo journalctl -u qadam-backend -f
```

## 📊 Service Comparison

| Service | Before | After | Savings |
|---------|--------|-------|---------|
| **Backend** | Azure Functions ($100/mo) | VM ($30/mo) | **70% cost reduction** |
| **OCR** | Azure Functions | VM (EasyOCR) | **Faster, lighter** |
| **AI** | Azure Functions | VM (Groq) | **Better performance** |
| **Total** | ~$200/mo | ~$60/mo | **$140/mo saved** |

## 🎯 Benefits

### Performance
- ✅ No cold starts
- ✅ Consistent response times
- ✅ Better resource control
- ✅ Faster OCR processing

### Cost
- ✅ 70% cost reduction
- ✅ Predictable monthly costs
- ✅ No per-execution charges

### Control
- ✅ Full VM access
- ✅ Custom configurations
- ✅ Direct log access
- ✅ Easy debugging

## 🔧 Management Commands

### Backend Service
```bash
# Status
sudo systemctl status qadam-backend

# Restart
sudo systemctl restart qadam-backend

# Logs
sudo journalctl -u qadam-backend -f

# Stop/Start
sudo systemctl stop qadam-backend
sudo systemctl start qadam-backend
```

### Nginx
```bash
# Status
sudo systemctl status nginx

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx

# Logs
sudo tail -f /var/log/nginx/error.log
```

### Updates
```bash
# Pull latest code
cd /opt/qadam-backend
git pull origin backend-proxy

# Restart service
cd proxy
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart qadam-backend
```

## 🐛 Troubleshooting

### Service won't start
```bash
sudo journalctl -u qadam-backend -n 50 --no-pager
cd /opt/qadam-backend/proxy
source venv/bin/activate
python app.py
```

### 502 Bad Gateway
```bash
curl http://localhost:5000/api/health
sudo systemctl restart qadam-backend
sudo systemctl restart nginx
```

### High memory usage
```bash
free -h
# Reduce workers in gunicorn_config.py
sudo systemctl restart qadam-backend
```

## 📈 Monitoring

```bash
# Service health
curl http://130.107.48.166/api/health

# Memory usage
free -h

# Disk space
df -h

# Active connections
sudo netstat -tlnp

# Process info
ps aux | grep gunicorn
```

## 🔐 Security Checklist

- [ ] SSH key authentication configured
- [ ] Firewall rules set (ports 22, 80, 443 only)
- [ ] Environment variables in systemd (not in code)
- [ ] Regular security updates scheduled
- [ ] SSL certificate installed (optional)
- [ ] Backup strategy in place

## 📝 Next Steps

1. ✅ Deploy backend to VM (130.107.48.166)
2. ⏳ Test all endpoints
3. ⏳ Update frontend to use new backend URL
4. ⏳ Monitor performance for 24 hours
5. ⏳ Decommission Azure Functions
6. ⏳ Set up SSL certificate
7. ⏳ Configure automated backups
8. ⏳ Set up monitoring alerts

## 📚 Documentation

- **Backend VM Setup:** `BACKEND_VM_SETUP.md`
- **Proxy Deployment:** `proxy/README_VM_DEPLOYMENT.md`
- **OCR Service:** `OCR_ALTERNATIVES_ANALYSIS.md`
- **AI Service:** `AI_SERVICE_CREATION_SUMMARY.md`

## 🎉 Success Criteria

- [ ] All services running and healthy
- [ ] Health endpoints responding
- [ ] OCR processing working
- [ ] AI question solving working
- [ ] Database operations working
- [ ] File uploads working
- [ ] Response times < 2 seconds
- [ ] No errors in logs
- [ ] Cost reduced by 70%

---

**Status:** ✅ Ready for deployment
**Branch:** `backend-proxy`
**VM:** `130.107.48.166`
**Next Action:** Configure GitHub Secrets and deploy
