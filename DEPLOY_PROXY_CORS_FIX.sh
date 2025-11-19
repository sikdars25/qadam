#!/bin/bash
# Deploy CORS Fix to Proxy VM
# Run this script on the proxy VM to apply the CORS fix

set -e  # Exit on error

echo "=================================================="
echo "🚀 Deploying CORS Fix to Proxy VM"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -d "/opt/qadam-backend-proxy" ]; then
    echo "❌ Error: /opt/qadam-backend-proxy directory not found"
    echo "   Are you on the proxy VM?"
    exit 1
fi

cd /opt/qadam-backend-proxy

echo "📂 Current directory: $(pwd)"
echo "🌿 Current branch: $(git branch --show-current)"
echo ""

# Stash any local changes
echo "💾 Stashing local changes (if any)..."
git stash

# Fetch latest changes
echo "📥 Fetching latest changes from GitHub..."
git fetch origin

# Checkout backend-proxy branch
echo "🔄 Checking out backend-proxy branch..."
git checkout backend-proxy

# Pull latest changes
echo "⬇️  Pulling latest changes..."
git pull origin backend-proxy

echo ""
echo "✅ Code updated successfully!"
echo ""
echo "📋 Recent commits:"
git log --oneline -n 3
echo ""

# Check if service exists
if ! systemctl list-unit-files | grep -q "qadam-backend-proxy.service"; then
    echo "❌ Error: qadam-backend-proxy.service not found"
    echo "   Please check systemd service configuration"
    exit 1
fi

# Restart the service
echo "🔄 Restarting qadam-backend-proxy service..."
sudo systemctl restart qadam-backend-proxy

# Wait a moment for service to start
sleep 3

# Check service status
echo ""
echo "📊 Service Status:"
sudo systemctl status qadam-backend-proxy --no-pager -l

echo ""
echo "=================================================="
echo "✅ Deployment Complete!"
echo "=================================================="
echo ""
echo "📝 Next Steps:"
echo "1. Check logs: sudo journalctl -u qadam-backend-proxy -n 50 --no-pager"
echo "2. Test CORS: curl -X OPTIONS https://130.107.48.166/ocr/extract-text -H 'Origin: https://zealous-ocean-06e22b51e.3.azurestaticapps.net' -v"
echo "3. Test from frontend: Upload an image and check for CORS errors"
echo ""
