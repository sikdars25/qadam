#!/bin/bash
# Setup Environment Variables for Backend VM
# This configures Cosmos DB, Blob Storage, and other credentials

set -e

echo "⚙️  Setting up environment variables..."
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Backing up..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Create .env file with prompts
echo "📝 Please provide the following credentials:"
echo ""

# Cosmos DB
read -p "Cosmos DB Endpoint (e.g., https://your-cosmos.documents.azure.com:443/): " COSMOS_ENDPOINT
read -p "Cosmos DB Key: " COSMOS_KEY
read -p "Cosmos DB Database Name [qadam]: " COSMOS_DATABASE
COSMOS_DATABASE=${COSMOS_DATABASE:-qadam}

echo ""

# Azure Storage
read -p "Azure Storage Connection String: " AZURE_STORAGE_CONNECTION_STRING

echo ""

# External Services
read -p "OCR Service URL [http://4.229.225.140]: " OCR_SERVICE_URL
OCR_SERVICE_URL=${OCR_SERVICE_URL:-http://4.229.225.140}

read -p "AI Service URL [http://130.107.48.221:8001]: " AI_SERVICE_URL
AI_SERVICE_URL=${AI_SERVICE_URL:-http://130.107.48.221:8001}

echo ""

# Flask Secret Key
read -p "Flask Secret Key (leave empty to generate random): " SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -hex 32)
    echo "Generated random secret key: $SECRET_KEY"
fi

echo ""

# Create .env file
cat > .env << EOF
# Cosmos DB Configuration
COSMOS_ENDPOINT=$COSMOS_ENDPOINT
COSMOS_KEY=$COSMOS_KEY
COSMOS_DATABASE=$COSMOS_DATABASE

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=$AZURE_STORAGE_CONNECTION_STRING

# External Services
OCR_SERVICE_URL=$OCR_SERVICE_URL
AI_SERVICE_URL=$AI_SERVICE_URL

# Flask Configuration
SECRET_KEY=$SECRET_KEY
FLASK_ENV=production
BACKEND_HTTPS=true

# Frontend URL (for CORS)
FRONTEND_URL=https://zealous-ocean-06e22b51e.3.azurestaticapps.net
EOF

echo "✅ .env file created successfully!"
echo ""

# Update systemd service to load .env file
echo "⚙️  Updating systemd service to use environment variables..."

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

echo "✅ Systemd service updated!"
echo ""

# Reload and restart
echo "🔄 Reloading systemd and restarting service..."
sudo systemctl daemon-reload
sudo systemctl restart qadam-backend

# Wait for service to start
sleep 3

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status qadam-backend --no-pager -l | head -15

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "🧪 Test the backend:"
echo "  curl -k https://localhost:5000/api/health"
echo ""
echo "📝 View logs:"
echo "  sudo journalctl -u qadam-backend -f"
echo ""
echo "⚠️  Security Note:"
echo "  The .env file contains sensitive credentials."
echo "  Make sure it's not committed to git (it's in .gitignore)"
