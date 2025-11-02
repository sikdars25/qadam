#!/bin/bash
# Setup systemd service for Qadam Backend

set -e

echo "⚙️  Setting up systemd service..."

# Create systemd service file
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

# Enable service
echo "✅ Enabling service..."
sudo systemctl enable qadam-backend

# Start service
echo "▶️  Starting service..."
sudo systemctl start qadam-backend

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status qadam-backend --no-pager -l | head -20

echo ""
echo "✅ Systemd service setup complete!"
echo ""
echo "Commands:"
echo "  sudo systemctl status qadam-backend"
echo "  sudo systemctl restart qadam-backend"
echo "  sudo journalctl -u qadam-backend -f"
