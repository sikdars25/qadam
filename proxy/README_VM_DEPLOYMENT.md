# Qadam Backend Proxy - VM Deployment

This folder contains the Flask application for deploying the Qadam backend to an Azure VM.

## 🎯 Architecture

```
Frontend (Azure Static Web Apps)
    ↓
Backend Proxy (Azure VM: 130.107.48.166:80)
    ↓
├── AI Service (VM: 130.107.48.221:8001)
└── OCR Service (VM: 4.229.225.140:8000)
```

## 🚀 Quick Deployment

### Option 1: Automated (GitHub Actions)

1. **Set GitHub Secrets:**
   - `BACKEND_VM_HOST`: `130.107.48.166`
   - `BACKEND_VM_USERNAME`: Your VM username
   - `BACKEND_VM_SSH_KEY`: Your SSH private key
   - `COSMOS_ENDPOINT`: Cosmos DB endpoint
   - `COSMOS_KEY`: Cosmos DB key
   - `COSMOS_DATABASE`: Database name
   - `AZURE_STORAGE_CONNECTION_STRING`: Blob storage connection
   - `OCR_SERVICE_URL`: `http://4.229.225.140`
   - `AI_SERVICE_URL`: `http://130.107.48.221:8001`
   - `SECRET_KEY`: Flask secret key

2. **Push to backend-proxy branch:**
   ```bash
   git push origin backend-proxy
   ```

3. **GitHub Actions will automatically deploy!**

### Option 2: Manual Deployment

**On the VM (130.107.48.166):**

```bash
# SSH to VM
ssh user@130.107.48.166

# Clone repository
sudo mkdir -p /opt/qadam-backend
sudo chown -R $USER:$USER /opt/qadam-backend
git clone -b backend-proxy https://github.com/sikdars25/qadam.git /opt/qadam-backend
cd /opt/qadam-backend/proxy

# Run deployment scripts
chmod +x deploy.sh setup_systemd.sh setup_nginx.sh
./deploy.sh
./setup_systemd.sh
./setup_nginx.sh
```

## 📋 Environment Variables

Create a `.env` file in the proxy folder:

```bash
# Cosmos DB
COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com:443/
COSMOS_KEY=your-cosmos-key
COSMOS_DATABASE=qadam

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...

# External Services
OCR_SERVICE_URL=http://4.229.225.140
AI_SERVICE_URL=http://130.107.48.221:8001

# Flask
SECRET_KEY=your-secret-key
```

## 🔧 Service Management

```bash
# Check status
sudo systemctl status qadam-backend

# Restart service
sudo systemctl restart qadam-backend

# View logs
sudo journalctl -u qadam-backend -f

# Check Nginx
sudo systemctl status nginx
sudo nginx -t
```

## 🧪 Testing

```bash
# Health check (local)
curl http://localhost:5000/api/health

# Health check (external)
curl http://130.107.48.166/api/health

# Test OCR connection
curl http://localhost:5000/api/test-ocr

# Test AI connection
curl http://localhost:5000/api/test-ai
```

## 📊 Monitoring

```bash
# Watch logs in real-time
sudo journalctl -u qadam-backend -f

# Check memory usage
free -h
ps aux | grep gunicorn

# Check disk space
df -h

# Check active connections
sudo netstat -an | grep :5000 | wc -l
```

## 🐛 Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u qadam-backend -n 50 --no-pager

# Check Python errors
cd /opt/qadam-backend/proxy
source venv/bin/activate
python app.py
```

### 502 Bad Gateway

```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart both services
sudo systemctl restart qadam-backend
sudo systemctl restart nginx
```

### High memory usage

```bash
# Check memory
free -h

# Reduce workers in gunicorn_config.py
workers = 2  # Instead of 4

# Restart service
sudo systemctl restart qadam-backend
```

## 📦 Dependencies

- Python 3.8+
- Flask 2.3.3
- Gunicorn 21.2.0
- Azure Cosmos DB SDK
- Azure Blob Storage SDK
- Nginx

## 🔄 Updates

To update the application:

```bash
cd /opt/qadam-backend
git pull origin backend-proxy
cd proxy
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart qadam-backend
```

## 🔐 Security

- ✅ Environment variables stored in systemd service
- ✅ No credentials in code
- ✅ Nginx reverse proxy
- ✅ Memory limits configured
- ✅ Automatic restarts on failure

## 📈 Performance

- **Workers:** 4 (adjust based on CPU cores)
- **Timeout:** 300 seconds (for long OCR/AI operations)
- **Max requests per worker:** 1000 (prevents memory leaks)
- **Memory limit:** 4GB

## 🎯 Next Steps

1. ✅ Deploy to VM
2. ✅ Configure Nginx
3. ✅ Set up SSL (optional)
4. ✅ Configure monitoring
5. ✅ Set up backups
6. ✅ Update frontend to point to VM
