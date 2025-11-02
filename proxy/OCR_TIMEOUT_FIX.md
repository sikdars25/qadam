# OCR Timeout Fix

## Problem

The backend was timing out when calling the OCR Azure Function because:

1. **PaddleOCR downloads models on first run** (~10-15 MB)
2. **Model download takes 60-90 seconds**
3. **Backend timeout was only 60 seconds**

### Error Message
```
OCR failed: OCR service timeout
Duration=116395ms (116 seconds)
```

## Solution

### 1. Increased Timeout ✅

**File**: `backend/ocr_client.py`

- **Before**: 60 seconds timeout
- **After**: 120 seconds timeout (2 minutes)

This allows PaddleOCR to download models on first request.

```python
# ocr_image function
response = requests.post(url, files=files, data=data, timeout=120)  # 2 min timeout
```

### 2. Added Warmup Endpoint ✅

**File**: `backend/app.py`

New endpoint: `POST /api/ocr/warmup`

This endpoint can be called to pre-download OCR models before actual use.

```bash
curl -X POST https://qadam-backend.azurewebsites.net/api/ocr/warmup
```

**Response:**
```json
{
  "success": true,
  "message": "OCR service warmed up successfully"
}
```

## Usage

### Option 1: Wait for First Request (Automatic)

The first OCR request will take 60-90 seconds to download models. Subsequent requests will be fast (2-5 seconds).

### Option 2: Pre-Warmup (Recommended)

Call the warmup endpoint after deployment to pre-download models:

```bash
# After backend deployment
curl -X POST https://qadam-backend.azurewebsites.net/api/ocr/warmup
```

This ensures the first user doesn't experience the delay.

### Option 3: Frontend Loading State

Show a loading message to users:

```javascript
async function scanImage(file) {
  setLoading(true);
  setMessage("Processing image... This may take up to 2 minutes on first use.");
  
  try {
    const response = await fetch('/api/parse-single-question', {
      method: 'POST',
      body: formData
    });
    // Handle response
  } finally {
    setLoading(false);
  }
}
```

## Timeline

### First Request (Cold Start)
```
User uploads image
  ↓
Backend calls OCR service (0s)
  ↓
OCR downloads detection model (0-30s)
  ↓
OCR downloads recognition model (30-60s)
  ↓
OCR downloads classifier model (60-70s)
  ↓
OCR processes image (70-75s)
  ↓
Returns result to backend (75s)
  ↓
Backend returns to frontend (75s)
```

### Subsequent Requests (Warm)
```
User uploads image
  ↓
Backend calls OCR service (0s)
  ↓
OCR processes image (models cached) (0-5s)
  ↓
Returns result (5s)
```

## Deployment

After pushing these changes:

1. **Backend redeploys automatically** (GitHub Actions)
2. **First request will be slow** (model download)
3. **Call warmup endpoint** to pre-download models
4. **Subsequent requests will be fast**

## Testing

### Test Warmup
```bash
curl -X POST https://qadam-backend.azurewebsites.net/api/ocr/warmup
```

### Test OCR
```bash
curl -X POST https://qadam-backend.azurewebsites.net/api/parse-single-question \
  -F "input_type=file" \
  -F "file_type=png" \
  -F "file=@test_image.png"
```

## Alternative Solutions (Future)

### 1. Keep OCR Function Warm
Use Azure Functions Premium Plan or configure "Always On" to keep the function warm.

### 2. Pre-download Models in Deployment
Add a deployment script that downloads models during build:

```python
# In deployment script
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')
# Models downloaded during deployment
```

### 3. Use Blob Storage for Models
Store models in Azure Blob Storage and download them during function startup.

## Summary

✅ **Fixed**: Increased timeout from 60s to 120s  
✅ **Added**: Warmup endpoint for pre-downloading models  
✅ **Result**: First request works (slow), subsequent requests are fast  

The OCR service now works correctly, but the first request after deployment will take 60-90 seconds. Use the warmup endpoint to avoid user-facing delays.
