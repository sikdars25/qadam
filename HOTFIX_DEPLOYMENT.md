# 🚨 HOTFIX: OCR Service NameError Fix

## ❌ **Critical Bug**

**Error:** `NameError: name 'post_process_latex_ocr_result' is not defined`

**Impact:** All OCR text extraction requests failing with HTTP 500 errors

**Root Cause:** Function scope issue in `latex_ocr_integration.py`
- Function was defined inside `get_latex_ocr_integration()` 
- Called from `extract_text_with_latex_priority()` outside that scope

---

## ✅ **Fix Applied**

**Commit:** `945d5d1`  
**Branch:** `backend-ocr`  
**File:** `ocr/latex_ocr_integration.py`

**Changes:**
- Moved `post_process_latex_ocr_result()` to module level
- Added proper error handling for `LargeSymbolProcessor` import
- Added fallback to return raw result if processing fails

---

## 🚀 **URGENT DEPLOYMENT REQUIRED**

### **SSH into OCR Server:**
```bash
ssh qadamuser@130.107.48.145
```

### **Deploy the Fix:**
```bash
# Navigate to OCR directory
cd /opt/qadam-ocr/ocr

# Pull latest changes
git pull origin backend-ocr

# Restart the service
sudo systemctl restart qadam-ocr

# Verify service is running
sudo systemctl status qadam-ocr

# Check logs for errors
sudo journalctl -u qadam-ocr -n 50 --no-pager
```

### **Test the Fix:**
```bash
# From your local machine or another terminal
curl -X POST http://130.107.48.145:8000/api/ocr/extract \
  -H "Content-Type: multipart/form-data" \
  -F "image=@test_image.png"

# Should return OCR text without 500 error
```

---

## 🔍 **Verification**

After deployment, verify:

1. ✅ OCR service starts without errors
2. ✅ `/api/ocr/extract` endpoint returns text successfully
3. ✅ No `NameError` in logs
4. ✅ LaTeX OCR post-processing works

---

## 📊 **Expected Behavior**

**Before Fix:**
```
NameError: name 'post_process_latex_ocr_result' is not defined
HTTP 500 Internal Server Error
```

**After Fix:**
```json
{
  "success": true,
  "text": "extracted OCR text",
  "engine": "latex-ocr",
  "confidence": 0.95
}
```

---

## ⏱️ **Deployment Priority**

**CRITICAL** - Deploy immediately to restore OCR functionality

**Estimated Downtime:** < 30 seconds (service restart)

---

## 📝 **Rollback Plan**

If issues occur after deployment:

```bash
cd /opt/qadam-ocr/ocr
git reset --hard fa9ff04  # Previous commit
sudo systemctl restart qadam-ocr
```

---

**Status:** ✅ Fix committed and pushed  
**Next Step:** Deploy to production server immediately
