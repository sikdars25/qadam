# 🚨 URGENT: Deploy Proxy CORS Fix

## Problem

The frontend refactoring is complete and pushed, but the **proxy VM is still running old code** without CORS support for `/ocr/*` routes. This is why you're seeing:

```
Access to XMLHttpRequest at 'https://130.107.48.166/ocr/extract-text' 
from origin 'https://zealous-ocean-06e22b51e.3.azurestaticapps.net' 
has been blocked by CORS policy
```

## Solution

Deploy the CORS fix to the proxy VM **immediately**.

---

## Quick Deploy (Copy-Paste Commands)

### Step 1: SSH to Proxy VM

```bash
ssh qadamuser@130.107.48.166
```

### Step 2: Deploy CORS Fix

```bash
cd /opt/qadam-backend-proxy && \
git stash && \
git fetch origin && \
git checkout backend-proxy && \
git pull origin backend-proxy && \
sudo systemctl restart qadam-backend-proxy && \
sleep 3 && \
sudo systemctl status qadam-backend-proxy
```

### Step 3: Verify Deployment

```bash
# Check logs for CORS configuration
sudo journalctl -u qadam-backend-proxy -n 50 --no-pager | grep -A 5 "CORS Configuration"
```

**Expected output:**
```
==================================================
CORS Configuration:
Allowed Origins: ['https://zealous-ocean-06e22b51e.3.azurestaticapps.net', ...]
Supports Credentials: True
==================================================
```

---

## Detailed Step-by-Step

### 1. Connect to Proxy VM

```bash
ssh qadamuser@130.107.48.166
```

**Password:** [Your VM password]

### 2. Navigate to Project

```bash
cd /opt/qadam-backend-proxy
pwd  # Should show: /opt/qadam-backend-proxy
```

### 3. Check Current Status

```bash
git branch --show-current  # Should show: backend-proxy
git status
```

### 4. Stash Local Changes (if any)

```bash
git stash
```

### 5. Pull Latest Changes

```bash
git pull origin backend-proxy
```

**Expected output:**
```
remote: Enumerating objects: 7, done.
remote: Counting objects: 100% (7/7), done.
Updating a07cfa8..c71b010
Fast-forward
 proxy/app.py | 10 ++++++++++
 1 file changed, 10 insertions(+)
```

### 6. Verify Changes

```bash
# Check if CORS config includes /ocr/*
grep -A 15 "Configure CORS" proxy/app.py
```

**Should show:**
```python
# Configure CORS with specific settings for Azure
CORS(app, 
     resources={
         r"/api/*": {...},
         r"/ocr/*": {...},           # ← This should be present
         r"/solve-question": {...}   # ← This should be present
     })
```

### 7. Restart Service

```bash
sudo systemctl restart qadam-backend-proxy
```

### 8. Check Service Status

```bash
sudo systemctl status qadam-backend-proxy
```

**Expected:**
```
● qadam-backend-proxy.service - Qadam Backend Proxy Service
   Active: active (running) since ...
```

### 9. Check Logs

```bash
sudo journalctl -u qadam-backend-proxy -n 100 --no-pager
```

**Look for:**
- ✅ "CORS Configuration:" message
- ✅ No Python errors
- ✅ Service started successfully

---

## Test CORS Fix

### Test 1: From Proxy VM

```bash
curl -X OPTIONS https://130.107.48.166/ocr/extract-text \
  -H "Origin: https://zealous-ocean-06e22b51e.3.azurestaticapps.net" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v 2>&1 | grep -i "access-control"
```

**Expected output:**
```
< Access-Control-Allow-Origin: https://zealous-ocean-06e22b51e.3.azurestaticapps.net
< Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
< Access-Control-Allow-Credentials: true
```

### Test 2: From Your Local Machine

```bash
curl -X OPTIONS https://130.107.48.166/ocr/extract-text \
  -H "Origin: https://zealous-ocean-06e22b51e.3.azurestaticapps.net" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

### Test 3: From Frontend

1. Open https://zealous-ocean-06e22b51e.3.azurestaticapps.net
2. Open browser DevTools (F12)
3. Go to Console tab
4. Paste an image (Ctrl+V)
5. Select subject
6. Click "Solve Question"
7. **Should work without CORS error!**

---

## Troubleshooting

### Issue 1: Service Won't Start

**Check logs:**
```bash
sudo journalctl -u qadam-backend-proxy -n 200 --no-pager
```

**Check for errors:**
```bash
sudo journalctl -u qadam-backend-proxy -n 200 --no-pager | grep -i error
```

**Common causes:**
- Syntax error in app.py
- Missing dependencies
- Port already in use

**Solution:**
```bash
# Test Python syntax
cd /opt/qadam-backend-proxy
source venv/bin/activate
python -m py_compile proxy/app.py
```

### Issue 2: Git Pull Fails

**Error:** "Your local changes would be overwritten"

**Solution:**
```bash
git stash
git pull origin backend-proxy
```

### Issue 3: CORS Still Not Working

**Check if changes are actually deployed:**
```bash
grep -n "r\"/ocr/\*\"" /opt/qadam-backend-proxy/proxy/app.py
```

**Should return a line number.** If not, the changes weren't pulled.

**Force pull:**
```bash
cd /opt/qadam-backend-proxy
git fetch origin
git reset --hard origin/backend-proxy
sudo systemctl restart qadam-backend-proxy
```

### Issue 4: Permission Denied

**If you get permission errors:**
```bash
# Check file ownership
ls -la /opt/qadam-backend-proxy/proxy/app.py

# Fix if needed
sudo chown -R qadamuser:qadamuser /opt/qadam-backend-proxy
```

---

## Verification Checklist

After deployment, verify:

- [ ] SSH to proxy VM successful
- [ ] Git pull completed without errors
- [ ] Changes visible in proxy/app.py
- [ ] Service restarted successfully
- [ ] Service status shows "active (running)"
- [ ] CORS configuration printed in logs
- [ ] curl test shows CORS headers
- [ ] Frontend can upload images
- [ ] No CORS errors in browser console
- [ ] OCR text extraction works
- [ ] Question solving works

---

## What Changed

### Before (Old Code):
```python
CORS(app, 
     resources={
         r"/api/*": {  # Only /api/* routes
             "origins": ALLOWED_ORIGINS,
             ...
         }
     })
```

### After (New Code):
```python
CORS(app, 
     resources={
         r"/api/*": {...},
         r"/ocr/*": {           # ← NEW: OCR routes
             "origins": ALLOWED_ORIGINS,
             ...
         },
         r"/solve-question": {  # ← NEW: Solve route
             "origins": ALLOWED_ORIGINS,
             ...
         }
     })
```

---

## Timeline

1. ✅ **Frontend refactored** - Pushed to main branch
2. ✅ **CORS fix coded** - Pushed to backend-proxy branch
3. ⏳ **Proxy VM deployment** - **NEEDS TO BE DONE NOW**
4. ⏳ **Testing** - After deployment

---

## Quick Reference

**Proxy VM IP:** 130.107.48.166  
**Branch:** backend-proxy  
**Commits:** c71b010, 9175ef3  
**Service:** qadam-backend-proxy  

**Deploy Command:**
```bash
ssh qadamuser@130.107.48.166 "cd /opt/qadam-backend-proxy && git pull origin backend-proxy && sudo systemctl restart qadam-backend-proxy"
```

---

## Summary

🚨 **The proxy VM needs to be updated RIGHT NOW** to fix the CORS issue.

The code is ready and pushed to GitHub. Just need to:
1. SSH to proxy VM
2. Pull latest changes
3. Restart service
4. Test

**Estimated time: 2-3 minutes** ⏱️

**After deployment, the frontend will work perfectly!** ✨
