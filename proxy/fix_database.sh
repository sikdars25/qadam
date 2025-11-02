#!/bin/bash
# Fix Database Connection - Load environment variables from .env file

set -e

echo "🔧 Fixing database connection..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "Please create .env file with your Cosmos DB credentials:"
    echo ""
    cat << 'EXAMPLE_EOF'
# Example .env file:
COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com:443/
COSMOS_KEY=your-cosmos-key-here
COSMOS_DATABASE=qadam
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
OCR_SERVICE_URL=http://4.229.225.140
AI_SERVICE_URL=http://130.107.48.221:8001
SECRET_KEY=your-secret-key-here
BACKEND_HTTPS=true
EXAMPLE_EOF
    echo ""
    echo "You can copy from .env.example and fill in your values:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

echo "✅ Found .env file"

# Update systemd service to load .env file
echo "⚙️  Updating systemd service..."

sudo tee /etc/systemd/system/qadam-backend.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Qadam Backend Service
After=network.target

[Service]
Type=simple
User=qadamuser
WorkingDirectory=/opt/qadam-backend/proxy
Environment="PATH=/opt/qadam-backend/proxy/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/opt/qadam-backend/proxy/.env
ExecStart=/opt/qadam-backend/proxy/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always
RestartSec=5
MemoryMax=4G
MemoryHigh=3G
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

echo "✅ Systemd service updated to load .env file"

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Restart service
echo "🔄 Restarting backend service..."
sudo systemctl restart qadam-backend

# Wait for service to start
sleep 3

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status qadam-backend --no-pager -l | head -15

echo ""
echo "✅ Database fix applied!"
echo ""
echo "The backend now loads environment variables from .env file"
echo ""
echo "🧪 Test database connection:"
echo "  1. Try deleting a paper from frontend"
echo "  2. Check logs: sudo journalctl -u qadam-backend -f"
echo ""
echo "Expected log output:"
echo "  ✓ Connected to Cosmos DB: https://..."
echo "  ✓ Database 'qadam' ready"
echo ""
echo "If you see connection errors, check your .env file credentials"
