# Complete OCR VM Deployment Guide

## 📍 VM Details
- **IP Address:** 130.107.48.145
- **Username:** qadamuser
- **Repository:** https://github.com/sikdars25/qadam.git
- **Branch:** backend-ocr
- **Folder:** ocr/
- **OCR Engine:** EasyOCR

---

## 🚀 Step-by-Step Deployment

### Step 1: SSH into the VM

```bash
ssh qadamuser@130.107.48.145
```

### Step 2: Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 3: Install Required System Dependencies

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    git \
    curl \
    wget \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0
```

**Why these packages?**
- `python3-venv`: For virtual environment
- `nginx`: Web server/reverse proxy
- `git`: To clone repository
- `libgl1-mesa-glx`, `libglib2.0-0`: Required by OpenCV (used by EasyOCR)

### Step 4: Create Application Directory

```bash
sudo mkdir -p /opt/qadam-ocr
sudo chown qadamuser:qadamuser /opt/qadam-ocr
cd /opt/qadam-ocr
```

### Step 5: Clone Repository

```bash
# Clone the backend-ocr branch
git clone -b backend-ocr https://github.com/sikdars25/qadam.git .

# Verify files
ls -la
# Should see: ocr/ folder

# Navigate to OCR folder
cd ocr
ls -la
# Should see: app.py, requirements.txt, README.md
```

### Step 6: Create Python Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Your prompt should change to: (venv) qadamuser@qadam-ocr-vm:/opt/qadam-ocr/ocr$

# Upgrade pip
pip install --upgrade pip
```

### Step 7: Install Python Dependencies

```bash
# Install all requirements
pip install -r requirements.txt
```

**⏱️ This will take 5-10 minutes** as it downloads:
- EasyOCR models (~100MB)
- PyTorch (~700MB)
- Other dependencies

**Expected output:**
```
Installing collected packages: torch, torchvision, easyocr, flask, ...
Successfully installed ...
```

### Step 8: Test Python Application

```bash
# Test imports
python -c "import easyocr; print('✅ EasyOCR installed')"
python -c "from app import app; print('✅ Flask app OK')"
python -c "import flask_cors; print('✅ Flask-CORS OK')"

# All should print success messages
```

### Step 9: Test Running the App Manually

```bash
# Run the app (this will initialize EasyOCR)
python app.py
```

**Expected output:**
```
📄 Initializing EasyOCR...
Downloading detection model...
Downloading recognition model...
✅ EasyOCR initialized successfully
 * Running on http://0.0.0.0:8000
```

**Leave this running** and open a **NEW terminal window** to test:

```bash
# In NEW terminal
ssh qadamuser@130.107.48.145

# Test health endpoint
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","service":"OCR Service (Flask on VM)","ocr_engine":"EasyOCR",...}
```

If you see the JSON response, **SUCCESS!** ✅

Press `Ctrl+C` in the first terminal to stop the app.

### Step 10: Create Systemd Service

Now let's set it up to run automatically.

```bash
# Create service file
sudo nano /etc/systemd/system/qadam-ocr.service
```

**Paste this content:**

```ini
[Unit]
Description=Qadam OCR Service (EasyOCR)
After=network.target

[Service]
Type=simple
User=qadamuser
WorkingDirectory=/opt/qadam-ocr/ocr
Environment="PATH=/opt/qadam-ocr/ocr/venv/bin"
ExecStart=/opt/qadam-ocr/ocr/venv/bin/gunicorn --workers 2 --timeout 300 --bind 127.0.0.1:8000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save and exit:**
- Press `Ctrl+O` (save)
- Press `Enter` (confirm)
- Press `Ctrl+X` (exit)

### Step 11: Enable and Start OCR Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable qadam-ocr

# Start the service
sudo systemctl start qadam-ocr

# Check status
sudo systemctl status qadam-ocr
```

**Expected output:**
```
● qadam-ocr.service - Qadam OCR Service (EasyOCR)
   Loaded: loaded (/etc/systemd/system/qadam-ocr.service; enabled)
   Active: active (running) since ...
```

**If status shows "failed":**
```bash
# Check logs
sudo journalctl -u qadam-ocr -n 50 --no-pager

# Common issues:
# - Path wrong: Check WorkingDirectory
# - Permissions: sudo chown -R qadamuser:qadamuser /opt/qadam-ocr
# - Missing packages: source venv/bin/activate && pip install -r requirements.txt
```

### Step 12: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/qadam-ocr
```

**Paste this content:**

```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Long timeouts for OCR processing
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        
        proxy_buffering off;
    }
    
    client_max_body_size 20M;
    
    access_log /var/log/nginx/qadam-ocr-access.log;
    error_log /var/log/nginx/qadam-ocr-error.log;
}
```

**Save and exit:** Ctrl+O, Enter, Ctrl+X

### Step 13: Enable Nginx Site

```bash
# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Enable OCR site
sudo ln -s /etc/nginx/sites-available/qadam-ocr /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t
```

**Expected output:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

**If test fails:**
- Check for typos in config file
- Ensure no duplicate `server` blocks
- Run: `sudo nginx -t` to see exact error

### Step 14: Start Nginx

```bash
# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

**Expected output:**
```
● nginx.service - A high performance web server
   Active: active (running)
```

### Step 15: Test Complete Setup

```bash
# Test through Nginx (port 80)
curl http://localhost/api/health

# Expected response:
# {"status":"healthy","service":"OCR Service (Flask on VM)","ocr_engine":"EasyOCR",...}
```

**If you get 502 Bad Gateway:**
```bash
# Check if OCR service is running
sudo systemctl status qadam-ocr

# Check Nginx error log
sudo tail -f /var/log/nginx/qadam-ocr-error.log

# Check OCR service log
sudo journalctl -u qadam-ocr -f
```

### Step 16: Get Private IP Address

```bash
# Get the private IP (for Proxy VM to connect)
ip addr show | grep "inet " | grep -v "127.0.0.1"
```

**Example output:**
```
inet 10.0.1.5/24 brd 10.0.1.255 scope global eth0
```

**Your private IP is:** `10.0.1.5` (note this down!)

### Step 17: Test from Outside (Optional)

```bash
# From your local machine
curl http://130.107.48.145/api/health

# Should return the same JSON response
```

---

## ✅ Verification Checklist

- [ ] System packages installed
- [ ] Repository cloned from backend-ocr branch
- [ ] Virtual environment created
- [ ] Python dependencies installed
- [ ] EasyOCR initializes without errors
- [ ] Flask app runs manually
- [ ] Systemd service created and running
- [ ] Nginx configured and running
- [ ] Health endpoint returns 200 OK
- [ ] Private IP noted for Proxy VM config

---

## 🔧 Useful Commands

### Check Service Status
```bash
sudo systemctl status qadam-ocr
sudo systemctl status nginx
```

### View Logs
```bash
# OCR service logs
sudo journalctl -u qadam-ocr -f

# Nginx access log
sudo tail -f /var/log/nginx/qadam-ocr-access.log

# Nginx error log
sudo tail -f /var/log/nginx/qadam-ocr-error.log
```

### Restart Services
```bash
sudo systemctl restart qadam-ocr
sudo systemctl restart nginx
```

### Update Code
```bash
cd /opt/qadam-ocr
git pull origin backend-ocr
cd ocr
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart qadam-ocr
```

---

## 🎯 Next Steps

After OCR VM is running:

1. **Update Proxy VM** with new OCR IP:
   ```bash
   ssh azureuser@130.107.48.166
   cd /opt/qadam-backend/proxy
   nano .env
   # Update: OCR_SERVICE_URL=http://10.0.1.5  (use your private IP)
   sudo systemctl restart qadam-backend
   ```

2. **Test connectivity from Proxy VM:**
   ```bash
   ping 10.0.1.5
   curl http://10.0.1.5/api/health
   ```

3. **Test from frontend:**
   - Upload an image in "Solve One Question"
   - Should now work without 502 errors!

---

## 🆘 Troubleshooting

### OCR Service Won't Start

```bash
# Check detailed error
sudo journalctl -u qadam-ocr -n 100 --no-pager

# Common fixes:
sudo chown -R qadamuser:qadamuser /opt/qadam-ocr
cd /opt/qadam-ocr/ocr
source venv/bin/activate
pip install -r requirements.txt
```

### Nginx 502 Error

```bash
# Check if OCR service is listening
sudo netstat -tlnp | grep 8000

# Should show gunicorn on port 8000
# If not, restart OCR service
sudo systemctl restart qadam-ocr
```

### EasyOCR Import Error

```bash
cd /opt/qadam-ocr/ocr
source venv/bin/activate
pip install --upgrade easyocr torch torchvision
```

### Out of Memory

```bash
# Check memory usage
free -h

# If low, reduce gunicorn workers
sudo nano /etc/systemd/system/qadam-ocr.service
# Change: --workers 2 to --workers 1
sudo systemctl daemon-reload
sudo systemctl restart qadam-ocr
```

---

## 🎉 Success!

Your OCR VM is now fully deployed and ready to process images! 🚀
