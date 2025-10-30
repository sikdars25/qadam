# OCR 500 Error - Diagnosis & Solutions

## Error Message
```
❌ Error: OCR failed: OCR service error: 500
Duration: 150+ seconds
```

## What's Happening

The error shows:
1. ✅ Backend successfully calls OCR service
2. ✅ OCR service receives the request
3. ❌ OCR processing fails with 500 error
4. ⏱️ Takes 150+ seconds (very slow)

## Possible Causes

### 1. Image Too Large
**Symptom:** Long processing time (150s+)  
**Cause:** Large images take too long to process  
**Solution:** Resize images before sending

### 2. Corrupted Image Data
**Symptom:** 500 error immediately  
**Cause:** Invalid image data sent from backend  
**Solution:** Validate image before sending

### 3. Memory Issues
**Symptom:** 500 error after long processing  
**Cause:** OCR service running out of memory  
**Solution:** Reduce image size or upgrade plan

### 4. PaddleOCR Crash
**Symptom:** 500 error with specific images  
**Cause:** PaddleOCR fails on certain image types  
**Solution:** Better error handling (deployed)

## Immediate Actions

### 1. Check Image Size
```python
# Before sending to OCR
from PIL import Image
import io

def resize_if_needed(image_bytes, max_size=2048):
    img = Image.open(io.BytesIO(image_bytes))
    
    # Check if resize needed
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
        
        # Convert back to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    return image_bytes
```

### 2. Add Image Validation
```python
# In backend before calling OCR
from PIL import Image
import io

def validate_image(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        
        # Check size
        if img.size[0] * img.size[1] > 10000000:  # 10 megapixels
            return False, "Image too large"
        
        # Check format
        if img.format not in ['PNG', 'JPEG', 'JPG']:
            return False, f"Unsupported format: {img.format}"
        
        return True, "OK"
    except Exception as e:
        return False, str(e)
```

### 3. Use Timeout Properly
```python
# When calling OCR from backend
try:
    response = requests.post(
        ocr_url,
        files=files,
        data=data,
        timeout=120  # 2 minutes max
    )
except requests.exceptions.Timeout:
    return jsonify({
        'success': False,
        'error': 'OCR processing timeout - image may be too large'
    }), 504
```

## Monitoring

### Check OCR Logs
```bash
# View recent OCR function logs
az webapp log tail --name qadam-ocr-addrcugfg4d4drg7 --resource-group qadam_ocr
```

### Check Backend Logs
```bash
# View backend logs
az webapp log tail --name qadam-backend --resource-group qadam_bend_group
```

### Test OCR Directly
```bash
# Test OCR service with small image
curl -X POST https://qadam-ocr-addrcugfg4d4drg7.canadacentral-01.azurewebsites.net/api/ocr/image \
  -F "file=@small_test.png" \
  -F "language=en"
```

## Recommended Image Specifications

| Property | Recommended | Maximum |
|----------|-------------|---------|
| **Format** | PNG, JPEG | PNG, JPEG, JPG |
| **Size** | < 1 MB | < 5 MB |
| **Dimensions** | < 2048x2048 | < 4096x4096 |
| **Resolution** | 150-300 DPI | 300 DPI |
| **Color** | RGB or Grayscale | Any |

## Updated Error Logging

I've deployed enhanced error logging to the OCR service. It now logs:
- Image path
- Image size in bytes
- Error type
- Detailed error message

This will help diagnose the exact cause of 500 errors.

## Testing After Fix

### Test 1: Small Image
```python
# Create small test image
from PIL import Image, ImageDraw
import io

img = Image.new('RGB', (400, 100), color='white')
draw = ImageDraw.Draw(img)
draw.text((10, 30), "Test", fill='black')

buffer = io.BytesIO()
img.save(buffer, format='PNG')
img_bytes = buffer.getvalue()

print(f"Image size: {len(img_bytes)} bytes")  # Should be < 10KB

# Send to OCR
# Should work fine
```

### Test 2: Large Image
```python
# Create large image
img = Image.new('RGB', (4000, 4000), color='white')
# This might fail or be very slow

# Resize first
img = img.resize((2000, 2000))
# Should work better
```

## Quick Fixes

### Fix 1: Add Image Preprocessing in Backend

Update `backend/ocr_client.py`:
```python
def ocr_image(image_file, language: str = 'en') -> Dict[str, Any]:
    try:
        # Read and validate image
        if isinstance(image_file, str):
            with open(image_file, 'rb') as f:
                img_bytes = f.read()
        else:
            img_bytes = image_file.read()
        
        # Resize if needed
        img_bytes = resize_if_needed(img_bytes)
        
        # Now send to OCR
        files = {'file': ('image.png', io.BytesIO(img_bytes), 'image/png')}
        # ... rest of code
```

### Fix 2: Add Retry Logic
```python
def ocr_image_with_retry(image_file, language='en', max_retries=2):
    for attempt in range(max_retries):
        try:
            result = ocr_client.ocr_image(image_file, language)
            if result.get('success'):
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2)  # Wait before retry
    
    return {'success': False, 'error': 'Max retries exceeded'}
```

## Summary

**Current Status:**
- ✅ OCR service is healthy
- ✅ Backend can connect to OCR
- ❌ OCR processing fails on some images
- ⏱️ Very slow (150s+) suggests large images

**Next Steps:**
1. ✅ Enhanced logging deployed (will show exact error)
2. 🔄 Add image resizing in backend
3. 🔄 Add image validation before OCR
4. 🔄 Implement retry logic

**Immediate Workaround:**
- Resize images to < 2048x2048 before uploading
- Use PNG or JPEG format only
- Keep file size < 1 MB

---

**Last Updated:** October 30, 2025  
**Status:** Enhanced logging deployed, monitoring for root cause
