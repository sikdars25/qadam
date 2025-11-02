#!/bin/bash
# Setup SSL Certificate for Backend VM
# This enables HTTPS access to the backend

set -e

echo "🔐 Setting up SSL Certificate for Backend VM..."

# Install Certbot (Let's Encrypt)
echo "📦 Installing Certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Note: Let's Encrypt requires a domain name
# For IP-only access, we'll use a self-signed certificate

echo "⚠️  Note: Let's Encrypt requires a domain name."
echo "Since we're using an IP address (130.107.48.166), we'll create a self-signed certificate."
echo ""
read -p "Do you have a domain name pointing to this VM? (y/n): " HAS_DOMAIN

if [ "$HAS_DOMAIN" = "y" ]; then
    read -p "Enter your domain name (e.g., api.qadam.com): " DOMAIN_NAME
    
    echo "🔐 Obtaining SSL certificate from Let's Encrypt..."
    sudo certbot --nginx -d $DOMAIN_NAME
    
    echo "✅ SSL certificate installed!"
    echo "Update your frontend .env.production to use: https://$DOMAIN_NAME"
else
    echo "🔐 Creating self-signed SSL certificate..."
    
    # Create directory for certificates
    sudo mkdir -p /etc/nginx/ssl
    
    # Generate self-signed certificate
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/nginx-selfsigned.key \
        -out /etc/nginx/ssl/nginx-selfsigned.crt \
        -subj "/C=IN/ST=State/L=City/O=Qadam/CN=130.107.48.166"
    
    # Create Diffie-Hellman group
    sudo openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048
    
    echo "✅ Self-signed certificate created!"
    
    # Update Nginx configuration
    echo "⚙️  Updating Nginx configuration for HTTPS..."
    
    sudo tee /etc/nginx/sites-available/qadam-backend > /dev/null << 'NGINX_EOF'
# HTTP - Redirect to HTTPS
server {
    listen 80 default_server;
    server_name _;
    return 301 https://$host$request_uri;
}

# HTTPS
server {
    listen 443 ssl default_server;
    server_name _;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;
    ssl_dhparam /etc/nginx/ssl/dhparam.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 10m;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

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
    
    echo ""
    echo "✅ SSL Setup Complete!"
    echo ""
    echo "⚠️  IMPORTANT: Self-signed certificates will show browser warnings!"
    echo ""
    echo "To avoid warnings, you need to:"
    echo "1. Get a domain name (e.g., from Namecheap, GoDaddy)"
    echo "2. Point the domain to 130.107.48.166"
    echo "3. Run this script again and choose 'y' for domain"
    echo ""
    echo "For now, users will need to accept the security warning in their browser."
    echo ""
    echo "Test HTTPS access:"
    echo "  curl -k https://130.107.48.166/api/health"
    echo ""
fi

# Open HTTPS port in firewall (if UFW is enabled)
if sudo ufw status | grep -q "Status: active"; then
    echo "🔥 Opening HTTPS port in firewall..."
    sudo ufw allow 443/tcp
    sudo ufw reload
fi

echo ""
echo "✅ SSL setup complete!"
echo ""
echo "Next steps:"
echo "1. Update frontend .env.production to use https://130.107.48.166"
echo "2. Rebuild and redeploy frontend"
echo "3. Test the application"
