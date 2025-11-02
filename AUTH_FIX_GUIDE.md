# Authentication Fix Guide

## 🚨 Problem

"Error 401: User not authenticated" appears in:
- Question Bank screen
- Upload Resources screen (when deleting papers)

## 🔍 Root Cause

The backend session cookies were not configured correctly for cross-origin requests between:
- **Frontend:** `https://zealous-ocean-06e22b51e.3.azurestaticapps.net` (HTTPS)
- **Backend:** `https://130.107.48.166` (HTTPS)

For cookies to work across origins with HTTPS, they must have:
- `SameSite=None` (allows cross-origin)
- `Secure=True` (requires HTTPS)
- `HttpOnly=True` (security)

## ✅ Solution Applied

### Changes Made

1. **Updated `proxy/app.py`:**
   - Added `BACKEND_HTTPS` environment variable check
   - Set `SameSite=None` and `Secure=True` when HTTPS is enabled
   - Maintains flexibility for HTTP/HTTPS environments

2. **Updated `proxy/setup_systemd.sh`:**
   - Added `Environment="BACKEND_HTTPS=true"` to systemd service
   - Ensures backend knows it's running with HTTPS

3. **Created `proxy/fix_auth.sh`:**
   - Quick fix script to update existing deployments
   - Updates systemd service and restarts backend

## 🚀 Apply the Fix

### On the Backend VM (130.107.48.166):

```bash
# SSH to VM
ssh qadamuser@130.107.48.166

# Navigate to directory
cd /opt/qadam-backend

# Pull latest changes
git pull origin backend-proxy

# Navigate to proxy folder
cd proxy

# Make script executable
chmod +x fix_auth.sh

# Run the fix
./fix_auth.sh
```

### What the Script Does:

1. ✅ Updates systemd service with `BACKEND_HTTPS=true`
2. ✅ Reloads systemd daemon
3. ✅ Restarts backend service
4. ✅ Shows service status

### Expected Output:

```
🔧 Fixing authentication issues...
⚙️  Updating systemd service...
🔄 Reloading systemd...
🔄 Restarting backend service...

📊 Service Status:
● qadam-backend.service - Qadam Backend Service
   Active: active (running)
   
✅ Authentication fix applied!

The backend now uses:
  - SameSite=None (allows cross-origin cookies)
  - Secure=True (requires HTTPS)
  - HttpOnly=True (security)
```

## 🧪 Testing

After applying the fix:

### 1. Clear Browser Cookies
```
1. Open browser DevTools (F12)
2. Go to Application tab
3. Clear all cookies for your frontend domain
4. Refresh the page
```

### 2. Login Again
```
1. Go to login page
2. Enter credentials
3. Login
```

### 3. Test Authentication
```
✅ Navigate to Question Bank - should load without 401 error
✅ Try to delete a paper - should work without 401 error
✅ Upload a new paper - should work
✅ Parse questions - should work
```

## 🔍 Verify Fix

### Check Backend Logs:

```bash
sudo journalctl -u qadam-backend -f
```

Look for:
```
🍪 Session cookies: SameSite=None, Secure=True, HttpOnly=True
```

### Check Browser Console:

1. Open DevTools (F12)
2. Go to Network tab
3. Login
4. Check the `/api/login` response headers
5. Should see: `Set-Cookie` with `SameSite=None; Secure; HttpOnly`

### Check Cookies in Browser:

1. Open DevTools (F12)
2. Go to Application tab
3. Expand Cookies
4. Click on your frontend domain
5. Should see session cookie with:
   - `SameSite`: None
   - `Secure`: ✓
   - `HttpOnly`: ✓

## 🐛 Troubleshooting

### Issue: Still Getting 401 Error

**Solution 1: Clear all browser data**
```
1. Open browser settings
2. Clear browsing data
3. Select "Cookies and other site data"
4. Clear data
5. Restart browser
6. Try again
```

**Solution 2: Check backend logs**
```bash
sudo journalctl -u qadam-backend -n 50 --no-pager
```

Look for session-related errors.

**Solution 3: Verify HTTPS is working**
```bash
curl -k https://130.107.48.166/api/health
```

Should return 200 OK.

### Issue: Backend Not Starting

```bash
# Check service status
sudo systemctl status qadam-backend

# Check logs
sudo journalctl -u qadam-backend -n 50 --no-pager

# Restart service
sudo systemctl restart qadam-backend
```

### Issue: CORS Errors

Check that frontend URL is in ALLOWED_ORIGINS in `proxy/app.py`:
```python
ALLOWED_ORIGINS = [
    'https://zealous-ocean-06e22b51e.3.azurestaticapps.net',
    ...
]
```

## 📊 Technical Details

### Session Cookie Configuration

**Before (Incorrect):**
```python
SameSite=Lax, Secure=False
```
- ❌ Doesn't work for cross-origin requests
- ❌ Browser blocks cookies

**After (Correct):**
```python
SameSite=None, Secure=True, HttpOnly=True
```
- ✅ Works for cross-origin requests
- ✅ Requires HTTPS
- ✅ Secure and HttpOnly for protection

### Environment Variable

```bash
BACKEND_HTTPS=true
```

This tells the Flask app that it's being accessed via HTTPS (through Nginx), so it should set `Secure=True` on cookies.

## 🎯 Summary

| Issue | Solution | Status |
|-------|----------|--------|
| 401 errors | Fixed session cookies | ✅ |
| SameSite=Lax | Changed to SameSite=None | ✅ |
| Secure=False | Changed to Secure=True | ✅ |
| Missing env var | Added BACKEND_HTTPS=true | ✅ |

## 🚀 Quick Commands

```bash
# On VM
cd /opt/qadam-backend
git pull origin backend-proxy
cd proxy
chmod +x fix_auth.sh
./fix_auth.sh

# Check logs
sudo journalctl -u qadam-backend -f

# Restart if needed
sudo systemctl restart qadam-backend
```

**After running the fix script, authentication should work!** 🎉
