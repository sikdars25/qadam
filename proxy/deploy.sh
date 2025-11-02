#!/bin/bash
# Deploy Backend Proxy to Azure VM
# Run this script on the VM at 130.107.48.166

set -e

echo "🚀 Deploying Qadam Backend Proxy..."

# Configuration
APP_DIR="/opt/qadam-backend"
SERVICE_NAME="qadam-backend"
PORT=5000

# Create app directory if it doesn't exist
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

# Navigate to app directory
cd $APP_DIR

# Pull latest code (if git repo exists)
if [ -d ".git" ]; then
    echo "📥 Pulling latest code..."
    git pull origin backend-proxy
else
    echo "📥 Cloning repository..."
    git clone -b backend-proxy https://github.com/sikdars25/qadam.git .
fi

# Navigate to proxy folder
cd proxy

# Create virtual environment
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your credentials!"
fi

# Create gunicorn config
echo "⚙️  Creating gunicorn config..."
cat > gunicorn_config.py << 'EOF'
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 100
timeout = 300
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
loglevel = "info"
accesslog = "-"
errorlog = "-"
EOF

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your credentials"
echo "2. Run setup_systemd.sh to create the service"
echo "3. Run setup_nginx.sh to configure Nginx"
