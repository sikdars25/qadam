# 🚨 IMMEDIATE FIX: Verify CORS Changes on Proxy VM

## Issue

You pulled the latest code, but CORS is still blocked. This means the changes in `proxy/app.py` might not be applied.

---

## Quick Verification & Fix

### Step 1: Verify Current Code on VM

Run this on the proxy VM:

```bash
cd /opt/qadam-backend/proxy
grep -n "r\"/ocr/\*\"" app.py
```

**Expected output:**
```
128:        r"/ocr/*": {
```

**If you see nothing**, the changes aren't there!

---

## Solution A: Force Update (Recommended)

```bash
cd /opt/qadam-backend/proxy
git fetch origin
git reset --hard origin/backend-proxy
sudo systemctl restart qadam-backend
sudo systemctl status qadam-backend
```

---

## Solution B: Check File Directly

```bash
cd /opt/qadam-backend/proxy
cat app.py | grep -A 15 "Configure CORS"
```

**Should show:**
```python
# Configure CORS with specific settings for Azure
CORS(app, 
     resources={
         r"/api/*": {
             "origins": ALLOWED_ORIGINS,
             "supports_credentials": True,
             "allow_credentials": True
         },
         r"/ocr/*": {                    # ← THIS MUST BE HERE
             "origins": ALLOWED_ORIGINS,
             "supports_credentials": True,
             "allow_credentials": True
         },
         r"/solve-question": {           # ← THIS MUST BE HERE
             "origins": ALLOWED_ORIGINS,
             "supports_credentials": True,
             "allow_credentials": True
         }
     },
```

---

## Solution C: Manual Edit (If git doesn't work)

If git commands fail, manually edit the file:

```bash
cd /opt/qadam-backend/proxy
nano app.py
```

Find this section (around line 120):

```python
# Configure CORS with specific settings for Azure
CORS(app, 
     resources={
         r"/api/*": {
             "origins": ALLOWED_ORIGINS,
             "supports_credentials": True,
             "allow_credentials": True
         }
     },
```

**Change it to:**

```python
# Configure CORS with specific settings for Azure
CORS(app, 
     resources={
         r"/api/*": {
             "origins": ALLOWED_ORIGINS,
             "supports_credentials": True,
             "allow_credentials": True
         },
         r"/ocr/*": {
             "origins": ALLOWED_ORIGINS,
             "supports_credentials": True,
             "allow_credentials": True
         },
         r"/solve-question": {
             "origins": ALLOWED_ORIGINS,
             "supports_credentials": True,
             "allow_credentials": True
         }
     },
```

Save (Ctrl+O, Enter, Ctrl+X) and restart:

```bash
sudo systemctl restart qadam-backend
```

---

## Verification After Fix

### 1. Check Service Logs

```bash
sudo journalctl -u qadam-backend -n 100 --no-pager | grep -i cors
```

**Should show:**
```
CORS Configuration:
Allowed Origins: ['https://zealous-ocean-06e22b51e.3.azurestaticapps.net', ...]
```

### 2. Test CORS with curl

```bash
curl -X OPTIONS http://localhost:5000/ocr/extract-text \
  -H "Origin: https://zealous-ocean-06e22b51e.3.azurestaticapps.net" \
  -H "Access-Control-Request-Method: POST" \
  -v 2>&1 | grep -i "access-control"
```

**Expected:**
```
< Access-Control-Allow-Origin: https://zealous-ocean-06e22b51e.3.azurestaticapps.net
< Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
< Access-Control-Allow-Credentials: true
```

### 3. Test from Internet

```bash
curl -X OPTIONS https://130.107.48.166/ocr/extract-text \
  -H "Origin: https://zealous-ocean-06e22b51e.3.azurestaticapps.net" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

---

## Common Issues

### Issue 1: Wrong Directory

**Problem:** You're in `/opt/qadam-backend/proxy` but the repo is elsewhere

**Check:**
```bash
pwd
ls -la app.py
```

**Fix:**
```bash
# Find the correct directory
find /opt -name "app.py" -path "*/proxy/*" 2>/dev/null
cd [correct_directory]
```

### Issue 2: File Permissions

**Problem:** Can't edit app.py

**Fix:**
```bash
sudo chown -R qadamuser:qadamuser /opt/qadam-backend
```

### Issue 3: Service Name Wrong

**Problem:** `qadam-backend` service doesn't exist

**Check:**
```bash
systemctl list-units --type=service | grep qadam
```

**Might be:**
- `qadam-backend-proxy`
- `qadam-proxy`
- `gunicorn`

**Use the correct name:**
```bash
sudo systemctl restart [correct-service-name]
```

---

## Debug: Check What's Running

```bash
# Check if Flask app is running
ps aux | grep python | grep app.py

# Check what's listening on port 5000
sudo netstat -tulpn | grep 5000

# Check service status
sudo systemctl status qadam-backend -l --no-pager

# Check recent logs
sudo journalctl -u qadam-backend -n 200 --no-pager
```

---

## Nuclear Option: Restart Everything

If nothing works:

```bash
cd /opt/qadam-backend/proxy
git fetch origin
git reset --hard origin/backend-proxy
sudo systemctl stop qadam-backend
sleep 2
sudo systemctl start qadam-backend
sleep 3
sudo systemctl status qadam-backend
sudo journalctl -u qadam-backend -n 50 --no-pager
```

---

## Expected Final State

After fix, you should see:

1. ✅ `app.py` contains `/ocr/*` and `/solve-question` in CORS config
2. ✅ Service running without errors
3. ✅ CORS headers in curl response
4. ✅ Frontend works without CORS error

---

## Quick Copy-Paste Commands

```bash
# Verify changes exist
cd /opt/qadam-backend/proxy && grep -n "r\"/ocr/\*\"" app.py

# If nothing shows, force update
cd /opt/qadam-backend/proxy && \
git fetch origin && \
git reset --hard origin/backend-proxy && \
sudo systemctl restart qadam-backend && \
sleep 3 && \
sudo systemctl status qadam-backend

# Test CORS
curl -X OPTIONS http://localhost:5000/ocr/extract-text \
  -H "Origin: https://zealous-ocean-06e22b51e.3.azurestaticapps.net" \
  -H "Access-Control-Request-Method: POST" \
  -v 2>&1 | grep "Access-Control"
```

---

## Summary

The git pull succeeded, but the actual code changes in `app.py` might not be applied. Use the commands above to:

1. Verify if changes are in `app.py`
2. Force update if needed
3. Restart service
4. Test CORS

**This should fix the CORS issue immediately!** 🚀
