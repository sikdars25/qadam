#!/bin/bash
# Fix authentication issues - Update session cookie configuration

set -e

echo "🔧 Fixing authentication issues..."

# Update systemd service to include BACKEND_HTTPS environment variable
echo "⚙️  Updating systemd service..."
sudo tee /etc/systemd/system/qadam-backend.service > /dev/null << 'EOF'
[Unit]
Description=Qadam Backend Service
After=network.target

[Service]
Type=simple
User=qadamuser
WorkingDirectory=/opt/qadam-backend/proxy
Environment="PATH=/opt/qadam-backend/proxy/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="BACKEND_HTTPS=true"
ExecStart=/opt/qadam-backend/proxy/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always
RestartSec=5
MemoryMax=4G
MemoryHigh=3G
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

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
echo "✅ Authentication fix applied!"
echo ""
echo "The backend now uses:"
echo "  - SameSite=None (allows cross-origin cookies)"
echo "  - Secure=True (requires HTTPS)"
echo "  - HttpOnly=True (security)"
echo ""
echo "Test authentication:"
echo "  1. Clear browser cookies"
echo "  2. Login again"
echo "  3. Try accessing Question Bank or deleting papers"
echo ""
echo "Check logs:"
echo "  sudo journalctl -u qadam-backend -f"
