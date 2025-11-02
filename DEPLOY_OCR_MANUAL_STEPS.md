# Deploy OCR Service to New VM - Manual Steps

## New OCR VM Details
- Public IP: 20.151.72.185
- Username: qadamuser
- Repository: https://github.com/sikdars25/qadam.git
- Branch: qadam-ocr
- Folder: ocr/

## Deployment Steps

### Step 1: SSH into New VM
```bash
ssh qadamuser@20.151.72.185
```

### Step 2: Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### Step 3: Install Dependencies
```bash
sudo apt install -y python3-pip python3-venv nginx git curl jq
```

### Step 4: Clone Repository
```bash
sudo mkdir -p /opt/qadam-ocr
sudo chown qadamuser:qadamuser /opt/qadam-ocr
cd /opt/qadam-ocr
git clone -b qadam-ocr https://github.com/sikdars25/qadam.git .
cd ocr
```

### Step 5: Setup Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Create Systemd Service
```bash
sudo nano /etc/systemd/system/qadam-ocr.service
```

Paste and save.

### Step 7: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/qadam-ocr
```

### Step 8: Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable qadam-ocr
sudo systemctl start qadam-ocr
sudo systemctl restart nginx
```

### Step 9: Test
```bash
curl http://localhost/api/health
```

### Step 10: Get Private IP
```bash
ip addr show | grep "inet " | grep -v "127.0.0.1"
```
