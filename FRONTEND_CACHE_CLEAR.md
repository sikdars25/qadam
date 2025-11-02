# Frontend Cache Clear Guide

## 🔄 Problem: Frontend Still Shows Deleted Data

After running the cleanup script on the backend, the frontend may still show old papers and textbooks due to:
1. **Browser cache** - Old API responses cached
2. **React state** - Component state not refreshed
3. **Service worker cache** - PWA caching

## ✅ Solutions

### Solution 1: Hard Refresh (Quick)

**Windows/Linux:**
```
Ctrl + Shift + R
```

**Mac:**
```
Cmd + Shift + R
```

This forces the browser to:
- Bypass cache
- Reload all resources
- Fetch fresh data from API

### Solution 2: Clear Browser Cache (Thorough)

1. **Open DevTools:** Press `F12`

2. **Clear Storage:**
   - Go to **Application** tab
   - Click **Clear storage** (left sidebar)
   - Check all boxes
   - Click **Clear site data**

3. **Refresh:** `F5` or `Ctrl + R`

### Solution 3: Incognito/Private Mode (Test)

Open the site in:
- **Chrome:** `Ctrl + Shift + N`
- **Firefox:** `Ctrl + Shift + P`
- **Edge:** `Ctrl + Shift + N`

This bypasses all cache and shows fresh data.

### Solution 4: Clear Specific Cache

**In DevTools (F12):**

1. **Network Tab:**
   - Right-click → Clear browser cache
   - Check "Disable cache" checkbox
   - Refresh page

2. **Application Tab:**
   - Storage → Local Storage → Delete
   - Storage → Session Storage → Delete
   - Cache Storage → Delete all

3. **Console Tab:**
   ```javascript
   localStorage.clear();
   sessionStorage.clear();
   location.reload(true);
   ```

## 🧪 Verify Data is Cleared

### Check Backend API Directly:

**1. Check Papers:**
```bash
curl https://130.107.48.166/api/uploaded-papers
```

**Expected:** Empty array `[]`

**2. Check Textbooks:**
```bash
curl https://130.107.48.166/api/textbooks
```

**Expected:** Empty array `[]`

### Check Frontend Network Requests:

1. Open DevTools (`F12`)
2. Go to **Network** tab
3. Refresh page
4. Look for `/api/uploaded-papers` request
5. Click on it → **Response** tab
6. Should show empty array `[]`

## 🔍 Troubleshooting

### Issue: Still showing old data after hard refresh

**Cause:** Backend not restarted after cleanup

**Solution:**
```bash
ssh qadamuser@130.107.48.166
sudo systemctl restart qadam-backend
```

### Issue: API returns empty but frontend shows data

**Cause:** React component state not refreshing

**Solution:**
1. Close the tab completely
2. Open new tab
3. Navigate to site again

### Issue: Some files show, others don't

**Cause:** Partial cleanup or blob storage not cleared

**Solution:**
```bash
# Run cleanup script again
cd /opt/qadam-backend/proxy
source venv/bin/activate
python3 clear_all_data_with_blobs.py
```

### Issue: Browser says "Can't reach this page"

**Cause:** Backend service down

**Solution:**
```bash
ssh qadamuser@130.107.48.166
sudo systemctl status qadam-backend
sudo systemctl restart qadam-backend
```

## 📋 Complete Cleanup Checklist

- [ ] Run `clear_all_data_with_blobs.py` on backend
- [ ] Restart backend service
- [ ] Wait 10 seconds for service to start
- [ ] Hard refresh frontend (`Ctrl + Shift + R`)
- [ ] Clear browser cache (DevTools → Application → Clear storage)
- [ ] Verify API returns empty arrays
- [ ] Check Upload Resources page - should be empty
- [ ] Check Textbooks page - should be empty
- [ ] Check Answer Full Paper - should be empty

## 🎯 Quick Fix Commands

**On VM:**
```bash
# Complete cleanup
cd /opt/qadam-backend/proxy
source venv/bin/activate
python3 clear_all_data_with_blobs.py
sudo systemctl restart qadam-backend
sudo journalctl -u qadam-backend -n 20
```

**In Browser Console:**
```javascript
// Clear all cache and reload
localStorage.clear();
sessionStorage.clear();
caches.keys().then(keys => keys.forEach(key => caches.delete(key)));
location.reload(true);
```

## 🌐 Alternative: Deploy Fresh Frontend

If cache issues persist, trigger a fresh frontend deployment:

```bash
# In your local repo
git commit --allow-empty -m "trigger-frontend-rebuild"
git push origin main
```

This forces GitHub Actions to rebuild and deploy fresh frontend.

---

**After cleanup, always hard refresh the frontend to see changes!** 🔄
