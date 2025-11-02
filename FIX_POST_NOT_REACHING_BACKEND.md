# Fix POST Request Not Reaching Backend

## 🐛 Problem
POST request is created in frontend with JWT token and FormData, but never reaches the backend server.

**Symptoms:**
- ✅ OPTIONS preflight succeeds (204)
- ✅ Frontend creates POST request with JWT token
- ✅ FormData is properly formatted
- ❌ POST request never appears in backend logs
- ❌ Request times out or fails silently

## 🔍 Root Cause
The request is likely timing out or being blocked by Nginx before it reaches the Flask backend. This happens because:
1. Nginx default timeouts are too short (60s)
2. OCR processing takes 60-120+ seconds
3. Request is dropped before completion

## ✅ Solution

### Step 1: Update Nginx Configuration on Proxy VM

SSH into Proxy VM:
```bash
ssh azureuser@130.107.48.166
```

Edit Nginx config:
```bash
sudo nano /etc/nginx/sites-available/qadam-backend
```

Replace with this configuration:
```nginx
server {
    listen 80;
    server_name 130.107.48.166;
    
    # Increase max upload size for images and PDFs
    client_max_body_size 50M;
    client_body_buffer_size 10M;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # CORS headers
    add_header Access-Control-Allow-Origin "https://zealous-ocean-06e22b51e.3.azurestaticapps.net" always;
    add_header Access-Control-Allow-Credentials "true" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With, Cookie" always;
    
    # Handle OPTIONS preflight
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin "https://zealous-ocean-06e22b51e.3.azurestaticapps.net" always;
        add_header Access-Control-Allow-Credentials "true" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With, Cookie" always;
        add_header Content-Length 0;
        add_header Content-Type text/plain;
        return 204;
    }
    
    # Proxy to Flask backend
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        
        # Forward headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CRITICAL: Increase timeouts for OCR and AI operations
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Buffer settings for large uploads
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
    
    # Logs
    access_log /var/log/nginx/qadam-backend-access.log;
    error_log /var/log/nginx/qadam-backend-error.log warn;
}
```

### Step 2: Test Nginx Configuration

```bash
sudo nginx -t
```

Should show:
```
nginx: configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Step 3: Reload Nginx

```bash
sudo systemctl reload nginx
```

Or if reload doesn't work:
```bash
sudo systemctl restart nginx
```

### Step 4: Check Nginx Status

```bash
sudo systemctl status nginx
```

Should show:
```
● nginx.service - A high performance web server
   Active: active (running)
```

### Step 5: Check Gunicorn Timeout

Edit Gunicorn service:
```bash
sudo nano /etc/systemd/system/qadam-backend.service
```

Ensure timeout is set:
```ini
[Service]
ExecStart=/opt/qadam-backend/proxy/venv/bin/gunicorn \
    --workers 4 \
    --timeout 300 \
    --bind 127.0.0.1:5000 \
    app:app
```

Reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart qadam-backend
```

## 🔍 Verify Fix

### Test 1: Check Nginx Logs

```bash
# Watch access log
sudo tail -f /var/log/nginx/qadam-backend-access.log

# Watch error log
sudo tail -f /var/log/nginx/qadam-backend-error.log
```

### Test 2: Check Backend Logs

```bash
sudo journalctl -u qadam-backend -f
```

### Test 3: Test from Frontend

1. Open "Solve One Question" page
2. Paste an image
3. Select subject
4. Click "Solve Question"
5. Watch the logs - you should now see:

**Nginx log:**
```
OPTIONS /api/parse-single-question HTTP/1.1" 204
POST /api/parse-single-question HTTP/1.1" 200
```

**Backend log:**
```
📥 OPTIONS /api/parse-single-question
📥 POST /api/parse-single-question
✅ JWT auth: user_id=..., username=...
```

## 📊 Timeout Settings Summary

| Component | Timeout | Purpose |
|-----------|---------|---------|
| **Frontend (axios)** | 120s | Wait for backend response |
| **Nginx** | 300s | Wait for Flask to process |
| **Gunicorn** | 300s | Wait for Python to execute |
| **OCR Service** | 60-120s | Image processing time |

## 🆘 Still Not Working?

### Check Nginx Error Log

```bash
sudo tail -n 100 /var/log/nginx/qadam-backend-error.log
```

Look for:
- `upstream timed out`
- `connection refused`
- `no live upstreams`

### Check if Flask is Running

```bash
sudo systemctl status qadam-backend
curl http://localhost:5000/api/health
```

### Check Firewall

```bash
sudo ufw status
# Should allow port 80
```

### Test Direct Connection

```bash
# From Proxy VM, test Flask directly
curl -X POST http://localhost:5000/api/health
```

## 🎯 Quick Commands

```bash
# On Proxy VM (130.107.48.166)
sudo nano /etc/nginx/sites-available/qadam-backend  # Edit config
sudo nginx -t                                        # Test config
sudo systemctl reload nginx                          # Reload Nginx
sudo tail -f /var/log/nginx/qadam-backend-error.log # Watch errors
sudo journalctl -u qadam-backend -f                  # Watch backend logs
```

---

**After applying these changes, the POST request should reach the backend and OCR processing should complete successfully!**
