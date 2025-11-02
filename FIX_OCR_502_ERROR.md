# Fix OCR 502 Error

## 🐛 Problem
OCR service returning **502 Bad Gateway** error when trying to process images.

## 🔍 Diagnosis

The 502 error means:
- **Nginx is running** on OCR VM (otherwise you'd get connection refused)
- **OCR service (port 8000) is DOWN** or not responding
- Nginx can't proxy the request to the backend service

## ✅ Solution

### Step 1: SSH into OCR VM

```bash
ssh azureuser@4.229.225.140
```

### Step 2: Check OCR Service Status

```bash
sudo systemctl status qadam-ocr
```

**Expected output if running:**
```
● qadam-ocr.service - Qadam OCR Service
   Loaded: loaded (/etc/systemd/system/qadam-ocr.service; enabled)
   Active: active (running) since...
```

**If you see "inactive (dead)" or "failed"**, the service is down.

### Step 3: Check Service Logs

```bash
sudo journalctl -u qadam-ocr -n 100 --no-pager
```

Look for errors like:
- `ModuleNotFoundError` - Missing Python dependencies
- `Address already in use` - Port 8000 is taken
- `Permission denied` - File permission issues
- Memory errors - Out of memory

### Step 4: Start/Restart OCR Service

```bash
# Start the service
sudo systemctl start qadam-ocr

# Or restart if it's running but not responding
sudo systemctl restart qadam-ocr

# Check status again
sudo systemctl status qadam-ocr
```

### Step 5: Test OCR Service Directly

```bash
# Test health endpoint (bypass Nginx)
curl http://localhost:8000/api/health

# Should return:
# {"status": "healthy", "service": "OCR", ...}
```

### Step 6: Test Through Nginx

```bash
# Test through Nginx
curl http://localhost/api/health

# Should also return healthy status
```

### Step 7: Check Nginx Configuration

```bash
# Test Nginx config
sudo nginx -t

# If errors, check config file
sudo nano /etc/nginx/sites-available/qadam-ocr

# Restart Nginx if needed
sudo systemctl restart nginx
```

## 🔧 Common Issues & Fixes

### Issue 1: Service Won't Start

**Check Python environment:**
```bash
cd /opt/qadam-ocr
source venv/bin/activate
python -c "import paddleocr"
```

**If import fails, reinstall dependencies:**
```bash
cd /opt/qadam-ocr
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 2: Port 8000 Already in Use

**Find and kill the process:**
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
sudo systemctl start qadam-ocr
```

### Issue 3: Out of Memory

**Check memory usage:**
```bash
free -h
```

**If low memory, restart VM:**
```bash
sudo reboot
```

### Issue 4: Permission Issues

**Fix permissions:**
```bash
sudo chown -R azureuser:azureuser /opt/qadam-ocr
sudo chmod +x /opt/qadam-ocr/venv/bin/*
```

## 📊 Verify Fix

From **Proxy VM** (130.107.48.166):

```bash
# Download diagnostic script
cd /opt/qadam-backend
wget https://raw.githubusercontent.com/sikdars25/qadam/main/check_ocr_service.sh
chmod +x check_ocr_service.sh

# Run diagnostics
./check_ocr_service.sh
```

Or manually test:
```bash
curl http://4.229.225.140/api/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "OCR",
  "version": "1.0.0"
}
```

## 🚀 Permanent Fix

### Enable Auto-Restart on Failure

Edit service file:
```bash
sudo nano /etc/systemd/system/qadam-ocr.service
```

Add these lines in `[Service]` section:
```ini
Restart=always
RestartSec=10
```

Reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart qadam-ocr
```

### Monitor Service

```bash
# Watch logs in real-time
sudo journalctl -u qadam-ocr -f

# Check if service is enabled to start on boot
sudo systemctl is-enabled qadam-ocr
```

## 📝 Service File Reference

**Location:** `/etc/systemd/system/qadam-ocr.service`

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

## 🆘 Still Not Working?

1. **Check VM resources:**
   ```bash
   htop  # or top
   df -h  # disk space
   free -h  # memory
   ```

2. **Check firewall:**
   ```bash
   sudo ufw status
   # Should allow port 80 from Proxy VM
   ```

3. **Check network connectivity:**
   ```bash
   # From Proxy VM
   ping 4.229.225.140
   telnet 4.229.225.140 80
   ```

4. **Restart everything:**
   ```bash
   sudo systemctl restart qadam-ocr
   sudo systemctl restart nginx
   ```

## 📞 Quick Commands Summary

```bash
# On OCR VM (4.229.225.140)
sudo systemctl status qadam-ocr        # Check status
sudo systemctl start qadam-ocr         # Start service
sudo systemctl restart qadam-ocr       # Restart service
sudo journalctl -u qadam-ocr -f        # Watch logs
curl http://localhost:8000/api/health  # Test directly

# On Proxy VM (130.107.48.166)
curl http://4.229.225.140/api/health   # Test OCR service
```

---

**After fixing, test from the frontend by uploading an image in "Solve One Question" page.**
