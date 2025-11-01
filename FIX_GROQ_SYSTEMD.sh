#!/bin/bash
# Fix GROQ_API_KEY in systemd service
# Run this script on the AI VM (130.107.48.221)

echo "🔧 Fixing GROQ_API_KEY in systemd service..."

# Prompt for Groq API key
read -p "Enter your Groq API Key (starts with gsk_): " GROQ_KEY

if [[ ! $GROQ_KEY =~ ^gsk_ ]]; then
    echo "❌ Error: Key should start with 'gsk_'"
    exit 1
fi

# Stop the service
echo "⏸️  Stopping qadam-ai service..."
sudo systemctl stop qadam-ai

# Create the systemd service file with correct format
echo "📝 Creating systemd service file..."
sudo tee /etc/systemd/system/qadam-ai.service > /dev/null << EOF
[Unit]
Description=Qadam AI Service
After=network.target

[Service]
Type=simple
User=qadamuser
WorkingDirectory=/opt/qadam-ai/ai
Environment="GROQ_API_KEY=$GROQ_KEY"
ExecStart=/opt/qadam-ai/ai/venv/bin/python3 /opt/qadam-ai/ai/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Start the service
echo "▶️  Starting qadam-ai service..."
sudo systemctl start qadam-ai

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 3

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status qadam-ai --no-pager -l

# Check logs
echo ""
echo "📋 Recent Logs:"
sudo journalctl -u qadam-ai -n 10 --no-pager

# Test health endpoint
echo ""
echo "🏥 Health Check:"
curl -s http://localhost:8001/api/health | python3 -m json.tool

echo ""
echo "✅ Done! Check if groq_api is now true above."
