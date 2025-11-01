#!/bin/bash
set -e

echo "🚀 Starting OCR Service Deployment..."

# Navigate to repository root
cd /opt/qadam-ocr

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git fetch origin backend-ocr
git reset --hard origin/backend-ocr

# Navigate to ocr directory
cd ocr

# Create/activate virtual environment
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install flask gunicorn
pip install -r requirements.txt

# Setup systemd service
echo "⚙️  Configuring systemd service..."
sudo cp qadam-ocr.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable qadam-ocr
sudo systemctl restart qadam-ocr

# Setup Nginx
echo "🌐 Configuring Nginx..."
sudo cp nginx-ocr.conf /etc/nginx/sites-available/qadam-ocr
sudo ln -sf /etc/nginx/sites-available/qadam-ocr /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "✅ Deployment complete!"
echo "🔍 Service status:"
sudo systemctl status qadam-ocr --no-pager
echo ""
echo "🌐 OCR Service is running!"
