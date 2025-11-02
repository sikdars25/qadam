# SSL Setup Guide - Fix Mixed Content Error

## 🚨 Problem

Your frontend is served over HTTPS, but the backend uses HTTP. Browsers block this "mixed content" for security.

**Error:**
```
Mixed Content: The page at 'https://zealous-ocean-06e22b51e.3.azurestaticapps.net/login' 
was loaded over HTTPS, but requested an insecure XMLHttpRequest endpoint 
'http://130.107.48.166/api/login'. This request has been blocked.
```

## ✅ Solution: Enable HTTPS on Backend VM

### Quick Setup (Self-Signed Certificate)

**On the Backend VM (130.107.48.166):**

```bash
# SSH to VM
ssh qadamuser@130.107.48.166

# Navigate to proxy folder
cd /opt/qadam-backend/proxy

# Make script executable
chmod +x setup_ssl.sh

# Run SSL setup
./setup_ssl.sh
```

The script will:
1. ✅ Create a self-signed SSL certificate
2. ✅ Configure Nginx for HTTPS
3. ✅ Redirect HTTP to HTTPS
4. ✅ Add security headers

### Manual Setup (If Script Fails)

```bash
# 1. Create SSL directory
sudo mkdir -p /etc/nginx/ssl

# 2. Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx-selfsigned.key \
    -out /etc/nginx/ssl/nginx-selfsigned.crt \
    -subj "/C=IN/ST=State/L=City/O=Qadam/CN=130.107.48.166"

# 3. Create Diffie-Hellman parameters
sudo openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

# 4. Update Nginx configuration
sudo nano /etc/nginx/sites-available/qadam-backend
```

**Nginx Configuration:**
```nginx
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
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Timeouts and body size
    client_max_body_size 50M;
    client_body_timeout 300s;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
}
```

```bash
# 5. Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx

# 6. Open HTTPS port in firewall
sudo ufw allow 443/tcp
sudo ufw reload
```

### Verify SSL Setup

```bash
# Test HTTPS endpoint (ignore certificate warning with -k)
curl -k https://130.107.48.166/api/health

# Should return:
# {"status":"healthy",...}
```

## 🔄 Update Frontend

The frontend has already been updated to use HTTPS:

```bash
# File: frontend/.env.production
REACT_APP_API_URL=https://130.107.48.166
```

Now rebuild and deploy:

```bash
cd frontend
npm run build
git add .
git commit -m "fix: enable HTTPS for backend"
git push origin main
```

## ⚠️ Self-Signed Certificate Warning

Users will see a browser warning because the certificate is self-signed. They need to:

1. Click "Advanced"
2. Click "Proceed to 130.107.48.166 (unsafe)"

This is normal for self-signed certificates.

## 🎯 Production Solution (Recommended)

For production, use a proper SSL certificate:

### Option 1: Get a Domain Name

1. **Buy a domain** (e.g., `api.qadam.com`)
2. **Point DNS** to `130.107.48.166`
3. **Use Let's Encrypt** (free SSL):

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d api.qadam.com

# Auto-renewal is configured automatically
```

### Option 2: Use Azure Application Gateway

1. Create Azure Application Gateway
2. Add SSL certificate
3. Point to backend VM
4. Update frontend to use Application Gateway URL

## 🧪 Testing Checklist

After SSL setup:

- [ ] HTTPS endpoint works: `curl -k https://130.107.48.166/api/health`
- [ ] HTTP redirects to HTTPS
- [ ] Frontend can connect to backend
- [ ] Login works
- [ ] File upload works
- [ ] No mixed content errors in browser console

## 🐛 Troubleshooting

### Issue: Certificate Error

**Browser shows:** "Your connection is not private"

**Solution:** This is expected with self-signed certificates. Click "Advanced" → "Proceed"

### Issue: Connection Refused

```bash
# Check if Nginx is listening on 443
sudo netstat -tlnp | grep :443

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

### Issue: Still Getting Mixed Content Error

1. **Clear browser cache**
2. **Hard refresh** (Ctrl + Shift + R)
3. **Check frontend .env.production** has `https://`
4. **Rebuild frontend** with new config

### Issue: CORS Error with HTTPS

Update backend CORS configuration in `proxy/app.py`:

```python
CORS(app, supports_credentials=True, origins=[
    'http://localhost:3000',
    'https://zealous-ocean-06e22b51e.3.azurestaticapps.net'
])
```

## 📊 Summary

| Step | Status |
|------|--------|
| SSL certificate created | ⏳ Run setup_ssl.sh |
| Nginx configured for HTTPS | ⏳ Run setup_ssl.sh |
| Frontend updated to HTTPS | ✅ Already done |
| Frontend rebuilt | ⏳ Run npm run build |
| Frontend deployed | ⏳ Push to GitHub |

## 🚀 Quick Commands

```bash
# On VM
cd /opt/qadam-backend/proxy
chmod +x setup_ssl.sh
./setup_ssl.sh

# On local machine
cd frontend
npm run build
git add .
git commit -m "fix: enable HTTPS"
git push origin main
```

**After these steps, the mixed content error will be resolved!** 🎉
