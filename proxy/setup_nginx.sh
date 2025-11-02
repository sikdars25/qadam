#!/bin/bash
# Setup Nginx for Qadam Backend

set -e

echo "🌐 Setting up Nginx..."

# Create Nginx config
sudo tee /etc/nginx/sites-available/qadam-backend > /dev/null << 'EOF'
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
EOF

# Enable site
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/qadam-backend /etc/nginx/sites-enabled/

# Test Nginx config
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

# Reload Nginx
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

echo ""
echo "✅ Nginx setup complete!"
echo ""
echo "Test:"
echo "  curl http://localhost/api/health"
echo "  curl http://130.107.48.166/api/health"
