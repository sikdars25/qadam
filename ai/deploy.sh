#!/bin/bash
set -e

echo "🚀 Starting AI Service Deployment..."

# Navigate to repository root
cd /opt/qadam-ai

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git fetch origin backend-ai
git reset --hard origin/backend-ai

# Navigate to ai directory
cd ai

# Create/activate virtual environment
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup systemd service
echo "⚙️  Configuring systemd service..."
sudo cp qadam-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable qadam-ai
sudo systemctl restart qadam-ai

# Setup Nginx
echo "🌐 Configuring Nginx..."
sudo cp nginx-ai.conf /etc/nginx/sites-available/qadam-ai
sudo ln -sf /etc/nginx/sites-available/qadam-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo "✅ Deployment complete!"
echo "🔍 Service status:"
sudo systemctl status qadam-ai --no-pager
echo ""
echo "🌐 AI Service is running!"
