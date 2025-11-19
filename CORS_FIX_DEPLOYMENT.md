# CORS Fix Deployment Guide

## Problem Identified

**Error:**
```
Access to XMLHttpRequest at 'https://130.107.48.166/ocr/extract-text' 
from origin 'https://zealous-ocean-06e22b51e.3.azurestaticapps.net' 
has been blocked by CORS policy
```

**Root Cause:**
- Frontend calls `/ocr/extract-text` and `/solve-question` routes
- Proxy CORS was only configured for `/api/*` routes
- `/ocr/*` and `/solve-question` routes were missing from CORS config

---

## Architecture Flow

```
┌──────────────┐
│   Frontend   │ (Azure Static Web App)
│ zealous-ocean│
└──────┬───────┘
       │ POST /ocr/extract-text (image)
       │ POST /solve-question (text)
       ▼
┌──────────────┐
│  Proxy VM    │ (130.107.48.166)
│ backend-proxy│
└──────┬───────┘
       │ Forward to OCR
       ▼
┌──────────────┐
│   OCR VM     │ (Internal)
│  backend-ocr │
└──────────────┘
```

---

## Solution Applied

### Commit: `c71b010`
### Branch: `backend-proxy`

**File Modified:** `proxy/app.py`

**Changes:**
```python
# Before: Only /api/* routes had CORS
CORS(app, 
     resources={
         r"/api/*": {
             "origins": ALLOWED_ORIGINS,
             ...
         }
     })

# After: Added /ocr/* and /solve-question
CORS(app, 
     resources={
         r"/api/*": {...},
         r"/ocr/*": {...},      # NEW
         r"/solve-question": {...}  # NEW
     })
```

---

## Deployment Steps

### Step 1: SSH to Proxy VM

```bash
ssh qadamuser@130.107.48.166
```

### Step 2: Navigate to Project

```bash
cd /opt/qadam-backend-proxy
```

### Step 3: Pull Latest Changes

```bash
git pull origin backend-proxy
```

**Expected output:**
```
remote: Enumerating objects: 7, done.
remote: Counting objects: 100% (7/7), done.
remote: Compressing objects: 100% (4/4), done.
remote: Total 4 (delta 3), reused 0 (delta 0)
Unpacking objects: 100% (4/4), done.
From https://github.com/sikdars25/qadam
 * branch            backend-proxy -> FETCH_HEAD
   a07cfa8..c71b010  backend-proxy -> origin/backend-proxy
Updating a07cfa8..c71b010
Fast-forward
 proxy/app.py | 10 ++++++++++
 1 file changed, 10 insertions(+)
```

### Step 4: Restart Proxy Service

```bash
sudo systemctl restart qadam-backend-proxy
```

### Step 5: Verify Service is Running

```bash
sudo systemctl status qadam-backend-proxy
```

**Expected output:**
```
● qadam-backend-proxy.service - Qadam Backend Proxy Service
   Loaded: loaded (/etc/systemd/system/qadam-backend-proxy.service; enabled)
   Active: active (running) since ...
```

### Step 6: Check Logs

```bash
sudo journalctl -u qadam-backend-proxy -n 50 --no-pager
```

**Look for:**
```
==================================================
CORS Configuration:
Allowed Origins: ['https://zealous-ocean-06e22b51e.3.azurestaticapps.net', ...]
Supports Credentials: True
==================================================
```

---

## Testing

### Test 1: Check CORS Headers with curl

```bash
# Test preflight request for /ocr/extract-text
curl -X OPTIONS https://130.107.48.166/ocr/extract-text \
  -H "Origin: https://zealous-ocean-06e22b51e.3.azurestaticapps.net" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

**Expected headers in response:**
```
< Access-Control-Allow-Origin: https://zealous-ocean-06e22b51e.3.azurestaticapps.net
< Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
< Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With, Cookie
< Access-Control-Allow-Credentials: true
```

### Test 2: Check from Browser Console

Open https://zealous-ocean-06e22b51e.3.azurestaticapps.net and run:

```javascript
// Test CORS preflight
fetch('https://130.107.48.166/ocr/extract-text', {
  method: 'OPTIONS',
  headers: {
    'Origin': window.location.origin,
    'Access-Control-Request-Method': 'POST',
    'Access-Control-Request-Headers': 'Content-Type'
  }
})
.then(response => {
  console.log('✅ CORS Status:', response.status);
  console.log('✅ CORS Headers:', [...response.headers.entries()]);
})
.catch(error => console.error('❌ CORS Error:', error));
```

### Test 3: Test Actual Image Upload

Use the QuestionSolver page:
1. Paste an image (Ctrl+V)
2. Select subject
3. Click "Solve Question"
4. Check browser console for errors

**Expected:**
- No CORS errors
- Image uploaded successfully
- OCR text extracted
- Solution displayed

---

## Routes Now Accessible

### 1. `/ocr/extract-text`
- **Method:** POST
- **Purpose:** Extract text from question images
- **Flow:** Frontend → Proxy → OCR Service

### 2. `/solve-question`
- **Method:** POST
- **Purpose:** Solve questions using AI
- **Flow:** Frontend → Proxy → AI Service

### 3. `/api/*` (existing)
- **Methods:** GET, POST, PUT, DELETE
- **Purpose:** All other API endpoints
- **Examples:** /api/login, /api/papers, /api/textbooks

---

## Verification Checklist

- [ ] SSH to proxy VM successful
- [ ] Git pull completed without errors
- [ ] Service restarted successfully
- [ ] Service status shows "active (running)"
- [ ] CORS configuration printed in logs
- [ ] Preflight OPTIONS request returns 200/204
- [ ] CORS headers present in response
- [ ] Frontend can upload images without CORS error
- [ ] OCR text extraction works
- [ ] Question solving works

---

## Troubleshooting

### Issue 1: Service won't start

**Check logs:**
```bash
sudo journalctl -u qadam-backend-proxy -n 100 --no-pager
```

**Common causes:**
- Syntax error in app.py
- Missing dependencies
- Port already in use

**Solution:**
```bash
# Check Python syntax
cd /opt/qadam-backend-proxy
source venv/bin/activate
python -m py_compile proxy/app.py
```

### Issue 2: CORS still blocked

**Check if origin is in allowed list:**
```bash
grep "ALLOWED_ORIGINS" /opt/qadam-backend-proxy/proxy/app.py
```

**Should include:**
```python
'https://zealous-ocean-06e22b51e.3.azurestaticapps.net',
```

### Issue 3: 404 on /ocr/extract-text

**Check if route exists:**
```bash
grep -n "extract-text" /opt/qadam-backend-proxy/proxy/app.py
```

**Check if OCR client is configured:**
```bash
grep -n "ocr_client" /opt/qadam-backend-proxy/proxy/app.py
```

---

## Rollback (if needed)

```bash
cd /opt/qadam-backend-proxy
git log --oneline -n 5
git checkout a07cfa8  # Previous commit
sudo systemctl restart qadam-backend-proxy
```

---

## Summary

✅ **CORS configuration updated** for `/ocr/*` and `/solve-question`  
✅ **Committed to backend-proxy branch** (commit `c71b010`)  
✅ **Pushed to GitHub**  
⏳ **Ready for deployment** to proxy VM  

**After deployment, the frontend will be able to:**
1. Upload question images
2. Get OCR text extraction
3. Solve questions with AI
4. All without CORS errors!

---

## Quick Deploy Command

```bash
ssh qadamuser@130.107.48.166 "cd /opt/qadam-backend-proxy && git pull origin backend-proxy && sudo systemctl restart qadam-backend-proxy && sudo systemctl status qadam-backend-proxy"
```

---

## Contact

For issues during deployment:
- Check logs: `sudo journalctl -u qadam-backend-proxy -f`
- Verify CORS: Test with curl commands above
- Check service: `sudo systemctl status qadam-backend-proxy`
