#!/bin/bash
# Complete OCR Service Fix - Run on OCR VM (4.229.225.140)
# This script fixes all common OCR issues

set -e  # Exit on error

echo "🔧 Complete OCR Service Fix"
echo "================================"
echo ""

# Check if we're on the right machine
if [ ! -d "/opt/qadam-ocr" ]; then
    echo "❌ Error: /opt/qadam-ocr not found"
    echo "Are you on the OCR VM (4.229.225.140)?"
    exit 1
fi

cd /opt/qadam-ocr

# Step 1: Stop everything
echo "⏸️  Step 1: Stopping services..."
sudo systemctl stop qadam-ocr 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true
sleep 2

# Step 2: Pull latest code
echo "📥 Step 2: Pulling latest code..."
git fetch origin backend-ocr
git checkout backend-ocr
git pull origin backend-ocr

# Step 3: Setup virtual environment
echo "🐍 Step 3: Setting up Python environment..."
cd ocr

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Step 4: Install dependencies
echo "📦 Step 4: Installing dependencies..."
pip install --upgrade pip setuptools wheel

# Check if we should use EasyOCR or PaddleOCR
if [ -f "app_easyocr.py" ]; then
    echo "✅ Using EasyOCR (lightweight)"
    cp app_easyocr.py app.py
    
    # Install EasyOCR dependencies (Python 3.12 compatible)
    pip install flask==3.0.0 flask-cors==4.0.0
    pip install easyocr==1.7.0
    pip install "pillow>=10.0.0" "numpy>=1.26.0"
    pip install gunicorn==21.2.0
    
    # Download EasyOCR models
    echo "📥 Downloading EasyOCR models (may take 2-3 minutes)..."
    python3 << 'PYEOF'
import easyocr
import os
os.makedirs('./models', exist_ok=True)
print("Initializing EasyOCR...")
reader = easyocr.Reader(['en'], gpu=False, model_storage_directory='./models')
print("✅ EasyOCR models ready!")
PYEOF
else
    echo "⚠️  Using PaddleOCR (fallback)"
    pip install flask==3.0.0 flask-cors==4.0.0
    pip install paddleocr==2.8.1
    pip install "pillow>=10.0.0" "numpy>=1.26.0"
    pip install gunicorn==21.2.0
fi

# Step 5: Create gunicorn config
echo "⚙️  Step 5: Creating gunicorn config..."
cat > gunicorn_config.py << 'GUNICORN_EOF'
bind = "127.0.0.1:8000"
workers = 2
worker_class = "sync"
worker_connections = 10
timeout = 120
keepalive = 5
max_requests = 100
max_requests_jitter = 10
loglevel = "info"
accesslog = "-"
errorlog = "-"
GUNICORN_EOF

# Step 6: Update systemd service
echo "🔧 Step 6: Configuring systemd service..."
sudo tee /etc/systemd/system/qadam-ocr.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Qadam OCR Service
After=network.target

[Service]
Type=simple
User=qadamuser
WorkingDirectory=/opt/qadam-ocr/ocr
Environment="PATH=/opt/qadam-ocr/ocr/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/qadam-ocr/ocr/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always
RestartSec=5
MemoryMax=2G
MemoryHigh=1.5G
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Step 7: Configure Nginx
echo "🌐 Step 7: Configuring Nginx..."
sudo tee /etc/nginx/sites-available/qadam-ocr > /dev/null << 'NGINX_EOF'
server {
    listen 80 default_server;
    server_name _;

    # Increase timeouts for OCR processing
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # Buffers
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
}
NGINX_EOF

# Enable site
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/qadam-ocr /etc/nginx/sites-enabled/

# Test Nginx config
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

# Step 8: Reload and start services
echo "🔄 Step 8: Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable qadam-ocr
sudo systemctl enable nginx

sudo systemctl start nginx
sudo systemctl start qadam-ocr

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Step 9: Verify
echo ""
echo "================================"
echo "📊 Service Status"
echo "================================"
echo ""

echo "1. Systemd Service:"
sudo systemctl status qadam-ocr --no-pager -l | head -15

echo ""
echo "2. Nginx Status:"
sudo systemctl status nginx --no-pager -l | head -10

echo ""
echo "3. Port 8000 Listening:"
sudo netstat -tlnp | grep 8000 || echo "⚠️  Port 8000 not listening!"

echo ""
echo "4. Health Check (local):"
curl -s http://localhost:8000/api/health | python3 -m json.tool || echo "❌ Local health check failed"

echo ""
echo "5. Health Check (external):"
curl -s http://$(hostname -I | awk '{print $1}')/api/health | python3 -m json.tool || echo "❌ External health check failed"

echo ""
echo "================================"
echo "📋 Recent Logs"
echo "================================"
sudo journalctl -u qadam-ocr -n 20 --no-pager

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "🧪 Test Commands:"
echo "  curl http://4.229.225.140/api/health"
echo ""
echo "📊 Monitor Logs:"
echo "  sudo journalctl -u qadam-ocr -f"
echo ""
echo "🔄 Restart Service:"
echo "  sudo systemctl restart qadam-ocr"
echo ""
