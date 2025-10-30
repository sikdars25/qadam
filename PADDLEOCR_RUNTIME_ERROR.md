# PaddleOCR Runtime Error - "could not execute a primitive"

## Error Details

```
RuntimeError: could not execute a primitive
at paddleocr/tools/infer/predict_det.py", line 255, in predict
    self.predictor.run()
```

## Root Cause

This error occurs when PaddleOCR's inference engine (PaddlePaddle) cannot execute a computation primitive. Common causes:

1. **Insufficient Memory** - Most likely
2. **CPU Resource Limits** - Azure Function constraints
3. **Corrupted Model Files** - Less likely
4. **Concurrent Requests** - Resource contention

## Why It Happens

Azure Functions (Consumption Plan) have limited resources:
- **Memory:** ~1.5GB per instance
- **CPU:** Shared, throttled
- **Timeout:** 5-10 minutes

PaddleOCR with all models loaded can use:
- **Memory:** 500MB-1GB
- **CPU:** High during inference

When multiple requests hit simultaneously or memory is exhausted, PaddlePaddle fails with this error.

## Solutions

### Solution 1: Upgrade to Premium Plan (Recommended)

**Azure Functions Premium Plan** provides:
- ✅ More memory (3.5GB - 14GB)
- ✅ Dedicated CPU
- ✅ Always-on instances
- ✅ Better performance

**Cost:** ~$150-300/month

**How to upgrade:**
```bash
# Create Premium plan
az functionapp plan create \
  --name qadam-ocr-premium \
  --resource-group qadam_ocr \
  --location canadacentral \
  --sku EP1 \
  --is-linux

# Move function to Premium plan
az functionapp update \
  --name qadam-ocr-addrcugfg4d4drg7 \
  --resource-group qadam_ocr \
  --plan qadam-ocr-premium
```

### Solution 2: Reduce PaddleOCR Memory Usage

Modify OCR initialization to use less memory:

**File:** `ocr/function_app.py`

```python
# Current (uses more memory)
ocr = PaddleOCR(use_angle_cls=True, lang=lang)

# Optimized (uses less memory)
ocr = PaddleOCR(
    use_angle_cls=False,      # Disable angle classifier
    use_gpu=False,             # CPU only
    enable_mkldnn=True,        # Enable Intel optimization
    cpu_threads=2,             # Limit threads
    max_batch_size=1,          # Process one at a time
    lang=lang
)
```

### Solution 3: Add Retry Logic with Exponential Backoff

**File:** `backend/ocr_client.py`

```python
def ocr_image_with_retry(image_file, language='en', max_retries=3):
    """OCR with automatic retry on failure"""
    import time
    
    for attempt in range(max_retries):
        try:
            result = ocr_image(image_file, language)
            
            if result.get('success'):
                return result
            
            # If error is RuntimeError, retry
            error = result.get('error', '')
            if 'could not execute a primitive' in error and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"⚠️ OCR failed, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            
            return result
            
        except Exception as e:
            if attempt == max_retries - 1:
                return {'success': False, 'error': str(e)}
            time.sleep(2 ** attempt)
    
    return {'success': False, 'error': 'Max retries exceeded'}
```

### Solution 4: Use Dedicated OCR Service

Instead of Azure Functions, use:
- **Azure Container Instances** - More resources, always-on
- **Azure App Service** - Dedicated compute
- **Azure Kubernetes Service** - Scalable, production-grade

### Solution 5: Rate Limiting

Add rate limiting to prevent concurrent requests overwhelming the service:

```python
# In OCR function
import threading
from time import sleep

# Global semaphore (max 2 concurrent OCR operations)
ocr_semaphore = threading.Semaphore(2)

@app.route('/api/ocr/image', methods=['POST'])
def ocr_image():
    # Acquire semaphore (wait if 2 requests already processing)
    acquired = ocr_semaphore.acquire(timeout=30)
    
    if not acquired:
        return create_cors_response({
            'success': False,
            'error': 'OCR service busy, please try again'
        }, 503)
    
    try:
        # Process OCR
        result = ocr.ocr(image_path, cls=True)
        return create_cors_response(result)
    finally:
        ocr_semaphore.release()
```

## Immediate Workarounds

### Workaround 1: Retry on Frontend

```javascript
async function ocrWithRetry(imageFile, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('/api/ocr/extract', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (result.success) {
        return result;
      }
      
      // If runtime error, retry
      if (result.error?.includes('could not execute a primitive') && i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, 2000 * (i + 1)));
        continue;
      }
      
      return result;
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 2000 * (i + 1)));
    }
  }
}
```

### Workaround 2: Show User-Friendly Error

```javascript
if (error.includes('could not execute a primitive')) {
  showMessage('OCR service is busy. Please try again in a moment.');
} else {
  showMessage('OCR failed. Please try again.');
}
```

## Monitoring

### Check Function Memory Usage

```bash
# View metrics
az monitor metrics list \
  --resource /subscriptions/.../resourceGroups/qadam_ocr/providers/Microsoft.Web/sites/qadam-ocr-addrcugfg4d4drg7 \
  --metric "MemoryWorkingSet" \
  --start-time 2025-10-30T00:00:00Z \
  --end-time 2025-10-30T23:59:59Z
```

### Check Concurrent Executions

```bash
az monitor metrics list \
  --resource /subscriptions/.../resourceGroups/qadam_ocr/providers/Microsoft.Web/sites/qadam-ocr-addrcugfg4d4drg7 \
  --metric "FunctionExecutionCount"
```

## Recommended Action Plan

### Short Term (Immediate)
1. ✅ Add retry logic in backend
2. ✅ Show user-friendly error messages
3. ✅ Monitor frequency of errors

### Medium Term (This Week)
1. 🔄 Optimize PaddleOCR settings (disable angle classifier)
2. 🔄 Add rate limiting (max 2 concurrent)
3. 🔄 Implement request queuing

### Long Term (Next Month)
1. 📋 Upgrade to Premium Plan OR
2. 📋 Move to Container Instances OR
3. 📋 Use managed OCR service (Azure Computer Vision)

## Alternative: Azure Computer Vision

Consider using Azure's managed OCR service:

**Pros:**
- ✅ No infrastructure management
- ✅ Highly scalable
- ✅ No runtime errors
- ✅ Built-in retry logic

**Cons:**
- ❌ Costs per request (~$1 per 1000 images)
- ❌ Less customizable

**Example:**
```python
from azure.cognitiveservices.vision.computervision import ComputerVisionClient

client = ComputerVisionClient(endpoint, credentials)
result = client.read(image_url, raw=True)
```

## Summary

**Current Issue:** PaddleOCR running out of resources on Azure Functions Consumption Plan

**Quick Fix:** Add retry logic (implement now)

**Best Fix:** Upgrade to Premium Plan or use Container Instances

**Cost vs Reliability:**
- Consumption Plan: $0-10/month, occasional errors
- Premium Plan: $150-300/month, reliable
- Container Instances: $50-100/month, reliable
- Azure Computer Vision: Pay per use, very reliable

## Immediate Action

I'll implement retry logic in the backend right now to handle these errors gracefully.

---

**Last Updated:** October 30, 2025  
**Status:** Runtime error identified, solutions documented
