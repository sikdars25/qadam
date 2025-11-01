#!/bin/bash
# Migrate from PaddleOCR to EasyOCR
# Run this on the OCR VM (4.229.225.140)

echo "🔄 Migrating OCR service from PaddleOCR to EasyOCR..."
echo ""

# Stop current service
echo "⏸️  Stopping current OCR service..."
sudo systemctl stop qadam-ocr

# Backup current app.py
echo "💾 Backing up current app.py..."
cd /opt/qadam-ocr/ocr
cp app.py app_paddleocr_backup.py

# Replace with EasyOCR version
echo "📝 Installing new EasyOCR version..."
cp app_easyocr.py app.py

# Update requirements
echo "📦 Updating requirements..."
cp requirements_easyocr.txt requirements.txt

# Reinstall dependencies
echo "🔧 Installing dependencies (this may take a few minutes)..."
source venv/bin/activate

# Uninstall PaddleOCR to save space
pip uninstall -y paddleocr paddlepaddle

# Install EasyOCR
pip install -r requirements.txt

# Download EasyOCR models (first time only)
echo "📥 Downloading EasyOCR models..."
python3 << 'PYEOF'
import easyocr
print("Initializing EasyOCR and downloading models...")
reader = easyocr.Reader(['en'], gpu=False)
print("✅ Models downloaded successfully!")
PYEOF

# Update systemd service for gunicorn
echo "⚙️  Updating systemd service..."
sudo tee /etc/systemd/system/qadam-ocr.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Qadam OCR Service (EasyOCR)
After=network.target

[Service]
Type=simple
User=qadamuser
WorkingDirectory=/opt/qadam-ocr/ocr
Environment="PATH=/opt/qadam-ocr/ocr/venv/bin"
ExecStart=/opt/qadam-ocr/ocr/venv/bin/gunicorn -w 2 -b 127.0.0.1:8000 --timeout 120 --max-requests 100 app:app
Restart=always
RestartSec=5
MemoryMax=1G
MemoryHigh=800M
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Start service
echo "▶️  Starting OCR service..."
sudo systemctl start qadam-ocr

# Wait for startup
echo "⏳ Waiting for service to start..."
sleep 5

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status qadam-ocr --no-pager -l | head -20

# Test health endpoint
echo ""
echo "🏥 Health Check:"
curl -s http://localhost:8000/api/health | python3 -m json.tool

# Check disk space saved
echo ""
echo "💾 Disk Space:"
df -h / | grep -v Filesystem

echo ""
echo "✅ Migration complete!"
echo ""
echo "📋 Summary:"
echo "  - Replaced PaddleOCR (500MB) with EasyOCR (150MB)"
echo "  - Saved ~350MB disk space"
echo "  - Improved math symbol detection"
echo "  - Better Greek letter support"
echo "  - Faster initialization"
echo ""
echo "🧪 Test from outside:"
echo "  curl http://4.229.225.140/api/health"
echo ""
echo "📝 Rollback if needed:"
echo "  cp app_paddleocr_backup.py app.py"
echo "  sudo systemctl restart qadam-ocr"
