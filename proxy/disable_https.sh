#!/bin/bash
# Disable HTTPS and use HTTP only
# This removes SSL certificate errors

set -e

echo "🔄 Switching backend to HTTP only..."

# Update Nginx to HTTP only
echo "⚙️  Updating Nginx configuration..."

sudo tee /etc/nginx/sites-available/qadam-backend > /dev/null << 'NGINX_EOF'
server {
    listen 80 default_server;
    server_name _;

    # Increase timeouts and body size
    client_max_body_size 50M;
    client_body_timeout 300s;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Buffers
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
}
NGINX_EOF

# Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

# Reload Nginx
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

# Update systemd service to set BACKEND_HTTPS=false
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
Environment="BACKEND_HTTPS=false"
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

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Restart backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart qadam-backend

# Wait for service to start
sleep 3

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status qadam-backend --no-pager -l | head -15

echo ""
echo "✅ Backend switched to HTTP!"
echo ""
echo "Backend now accessible at: http://130.107.48.166"
echo ""
echo "🍪 Session cookies: SameSite=Lax, Secure=False"
echo ""
echo "🧪 Test:"
echo "  curl http://130.107.48.166/api/health"
