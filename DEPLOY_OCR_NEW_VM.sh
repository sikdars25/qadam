#!/bin/bash

# OCR Service Deployment Script for New VM
# Run this on the new OCR VM (20.151.72.185)

set -e  # Exit on error

echo "🚀 Deploying OCR Service from Git"
echo "=================================="
echo ""

# 1. Update system
echo "1️⃣ Updating system packages..."
sudo apt update
sudo apt upgrade -y

# 2. Install dependencies
echo ""
echo "2️⃣ Installing dependencies..."
sudo apt install -y python3-pip python3-venv nginx git curl

# 3. Create directory and clone repository
echo ""
echo "3️⃣ Setting up OCR service directory..."
sudo mkdir -p /opt/qadam-ocr
sudo chown qadamuser:qadamuser /opt/qadam-ocr
cd /opt/qadam-ocr

# 4. Clone repository
echo ""
echo "4️⃣ Cloning repository..."
if [ -d ".git" ]; then
    echo "   Repository already exists, pulling latest changes..."
    git pull origin qadam-ocr
else
    echo "   Cloning fresh repository..."
    git clone -b qadam-ocr https://github.com/sikdars25/qadam.git .
fi

# Navigate to OCR folder
cd ocr

# 5. Create Python virtual environment
echo ""
echo "5️⃣ Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 6. Install Python dependencies
echo ""
echo "6️⃣ Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# 7. Test OCR service
echo ""
echo "7️⃣ Testing OCR service..."
python -c "import easyocr; print('✅ EasyOCR imported successfully')" || echo "⚠️ EasyOCR import failed"

# 8. Create systemd service
echo ""
echo "8️⃣ Creating systemd service..."
sudo tee /etc/systemd/system/qadam-ocr.service > /dev/null <<EOF
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
EOF

# 9. Configure Nginx
echo ""
echo "9️⃣ Configuring Nginx..."
sudo tee /etc/nginx/sites-available/qadam-ocr > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
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
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/qadam-ocr /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo ""
echo "🔍 Testing Nginx configuration..."
sudo nginx -t

# 10. Enable and start services
echo ""
echo "🔄 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable qadam-ocr
sudo systemctl start qadam-ocr
sudo systemctl restart nginx

# 11. Wait for service to start
echo ""
echo "⏳ Waiting for OCR service to start..."
sleep 5

# 12. Check service status
echo ""
echo "📊 Service Status:"
echo "=================="
sudo systemctl status qadam-ocr --no-pager -l

echo ""
echo "📊 Nginx Status:"
echo "================"
sudo systemctl status nginx --no-pager -l

# 13. Test endpoints
echo ""
echo "🧪 Testing OCR endpoints..."
echo ""
echo "Test 1: Direct service (port 8000):"
curl -s http://localhost:8000/api/health | jq '.' || echo "❌ Direct service test failed"

echo ""
echo "Test 2: Through Nginx (port 80):"
curl -s http://localhost/api/health | jq '.' || echo "❌ Nginx proxy test failed"

# 14. Get private IP
echo ""
echo "📍 VM Network Information:"
echo "=========================="
PRIVATE_IP=$(ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | cut -d'/' -f1 | head -1)
echo "Private IP: $PRIVATE_IP"
echo "Public IP: 20.151.72.185"

# 15. Final instructions
echo ""
echo "✅ OCR Service Deployment Complete!"
echo "===================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Update Proxy VM configuration:"
echo "   ssh azureuser@130.107.48.166"
echo "   cd /opt/qadam-backend/proxy"
echo "   nano .env"
echo "   # Change: OCR_SERVICE_URL=http://$PRIVATE_IP"
echo "   sudo systemctl restart qadam-backend"
echo ""
echo "2. Test connectivity from Proxy VM:"
echo "   ping $PRIVATE_IP"
echo "   curl http://$PRIVATE_IP/api/health"
echo ""
echo "3. Monitor logs:"
echo "   sudo journalctl -u qadam-ocr -f"
echo "   sudo tail -f /var/log/nginx/qadam-ocr-error.log"
echo ""
echo "🎉 OCR service is ready!"
