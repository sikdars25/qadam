# OCR Service Optimization Plan

## Current Issues
- OCR scan failing frequently
- Need faster processing
- Minimize memory usage
- Improve reliability

## Optimization Strategy

### 1. **PaddleOCR Configuration** ⚡
**Current:** Default settings
**Optimized:**
```python
ocr_engine = PaddleOCR(
    use_angle_cls=True,          # Keep for rotated text
    lang='en',                    # English only (faster)
    use_gpu=False,                # CPU mode for VM
    show_log=False,               # Reduce logging overhead
    det_db_thresh=0.3,            # Lower threshold for better detection
    det_db_box_thresh=0.5,        # Filter low-confidence boxes
    rec_batch_num=6,              # Process 6 lines at once (faster)
    max_text_length=25,           # Limit text length (faster)
    use_mp=True,                  # Enable multiprocessing
    total_process_num=2           # Use 2 processes (balance speed/memory)
)
```

### 2. **Image Preprocessing** 🖼️
**Add before OCR:**
```python
from PIL import Image
import cv2
import numpy as np

def preprocess_image(image_data):
    """Optimize image for OCR"""
    # Load image
    img = Image.open(io.BytesIO(image_data))
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize if too large (max 2000px width)
    max_width = 2000
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    
    # Convert to numpy array
    img_np = np.array(img)
    
    # Enhance contrast (improves OCR accuracy)
    img_np = cv2.convertScaleAbs(img_np, alpha=1.2, beta=10)
    
    return img_np
```

### 3. **Memory Management** 💾
```python
import gc

def extract_text_optimized(image_data):
    """Extract text with memory optimization"""
    try:
        # Preprocess
        img = preprocess_image(image_data)
        
        # Run OCR
        result = ocr.ocr(img, cls=True)
        
        # Clear image from memory immediately
        del img
        gc.collect()
        
        # Process results
        text = process_results(result)
        
        return text
    finally:
        # Always clean up
        gc.collect()
```

### 4. **Error Handling & Retries** 🔄
```python
import time

def extract_with_retry(image_data, max_retries=2):
    """Extract text with automatic retry on failure"""
    for attempt in range(max_retries):
        try:
            return extract_text_optimized(image_data)
        except Exception as e:
            if attempt < max_retries - 1:
                logging.warning(f"OCR attempt {attempt + 1} failed: {e}, retrying...")
                time.sleep(0.5)  # Brief pause before retry
                gc.collect()  # Clean memory before retry
            else:
                raise
```

### 5. **Caching** 📦
```python
from functools import lru_cache
import hashlib

def get_image_hash(image_data):
    """Get hash of image for caching"""
    return hashlib.md5(image_data).hexdigest()

# Simple in-memory cache (last 10 images)
ocr_cache = {}
MAX_CACHE_SIZE = 10

def extract_with_cache(image_data):
    """Extract text with caching"""
    img_hash = get_image_hash(image_data)
    
    # Check cache
    if img_hash in ocr_cache:
        logging.info("✅ Cache hit!")
        return ocr_cache[img_hash]
    
    # Extract text
    result = extract_with_retry(image_data)
    
    # Update cache
    if len(ocr_cache) >= MAX_CACHE_SIZE:
        # Remove oldest entry
        ocr_cache.pop(next(iter(ocr_cache)))
    ocr_cache[img_hash] = result
    
    return result
```

### 6. **Timeout Protection** ⏱️
```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import signal

def extract_with_timeout(image_data, timeout=30):
    """Extract text with timeout protection"""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(extract_with_cache, image_data)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            logging.error("OCR timeout!")
            raise Exception("OCR processing timeout - image may be too complex")
```

### 7. **Response Optimization** 📤
```python
def create_response(text, confidence, details=None):
    """Create optimized response"""
    response = {
        'success': True,
        'text': text,
        'confidence': round(confidence, 3)  # Limit decimal places
    }
    
    # Only include details if requested
    if details and request.args.get('include_details') == 'true':
        response['details'] = details
    
    return jsonify(response)
```

## Implementation Priority

### Phase 1: Critical (Implement Now) 🔴
1. ✅ PaddleOCR optimization parameters
2. ✅ Image preprocessing
3. ✅ Memory management with gc.collect()
4. ✅ Error handling with retries

### Phase 2: Important (Next) 🟡
5. ✅ Timeout protection
6. ✅ Response optimization

### Phase 3: Nice to Have (Later) 🟢
7. ✅ Caching (if same images processed repeatedly)

## Expected Improvements

### Speed 🚀
- **Before:** 3-5 seconds per image
- **After:** 1-2 seconds per image
- **Improvement:** 50-60% faster

### Reliability 📈
- **Before:** ~80% success rate
- **After:** ~95% success rate
- **Improvement:** Retry logic + better error handling

### Memory 💾
- **Before:** 500-800 MB per request
- **After:** 200-400 MB per request
- **Improvement:** 50% reduction via gc.collect()

## Testing Commands

```bash
# Test on VM
curl -X POST http://localhost:8000/api/extract-text \
  -F "file=@test_image.jpg"

# Benchmark
time curl -X POST http://localhost:8000/api/extract-text \
  -F "file=@test_image.jpg"

# Memory usage
ps aux | grep python | grep ocr
```

## Monitoring

```bash
# Watch logs
sudo journalctl -u qadam-ocr -f

# Check memory
free -h

# Check process
top -p $(pgrep -f "ocr")
```
