# Math Expression OCR Guide

## Overview
The OCR service has been optimized to recognize mathematical expressions, including:
- **Latin letters** (a, b, c, x, y, z, etc.)
- **Greek letters** (α, β, γ, θ, π, etc.)
- **Mathematical symbols** (√, ∫, ∑, ±, ×, ÷, ≠, ≤, ≥, etc.)
- **Equations and formulas**

## Configuration Changes

### Language Support
```python
# Before: Only English
ocr_reader = easyocr.Reader(['en'], gpu=False)

# After: English + Latin for math
ocr_reader = easyocr.Reader(
    ['en', 'la'],  # English + Latin
    gpu=False,
    recog_network='latin_g2'  # Latin character recognition
)
```

### OCR Parameters
Optimized for detecting small math symbols:
```python
results = reader.readtext(
    img_np,
    detail=1,
    paragraph=False,      # Detect individual elements
    min_size=10,          # Detect smaller text (symbols)
    text_threshold=0.6,   # Lower threshold for symbols
    low_text=0.3          # Detect faint text
)
```

### Image Preprocessing
- **Higher resolution**: Max 2400px (was 2000px)
- **Upscaling**: Small images (<800px) are upscaled for better recognition
- **Better quality**: Maintains detail for math symbols

## Testing Math OCR

### 1. Restart the OCR Service
After updating the code, restart the service to download new language models:

```bash
cd ocr
.\run_ocr_only.bat
```

**Note**: First run will download Latin language models (~50-100MB). This is a one-time download.

### 2. Test with Sample Math Images

Create a test script `test_math_ocr.py`:

```python
import requests
import base64

def test_math_image(image_path):
    """Test OCR on a math image"""
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Send to OCR service
    response = requests.post(
        'http://localhost:5001/api/extract-text',
        json={'image_base64': image_data}
    )
    
    result = response.json()
    
    if result['success']:
        print(f"✅ Text extracted: {result['text']}")
        print(f"📊 Confidence: {result['confidence']:.2%}")
        print(f"📐 Has math: {result.get('has_math', 'N/A')}")
        
        if 'details' in result:
            print("\n📝 Detailed results:")
            for item in result['details']:
                print(f"  - '{item['text']}' (conf: {item['confidence']:.2%})")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

# Test with your math image
test_math_image('math_question.png')
```

### 3. Expected Improvements

**Before** (English only):
```
Input:  "Find the value of x in: 2x + 3 = 7"
Output: "Find the value of in: 2 + 3 = 7"  ❌ Missing 'x'
```

**After** (English + Latin):
```
Input:  "Find the value of x in: 2x + 3 = 7"
Output: "Find the value of x in: 2x + 3 = 7"  ✅ Correct
```

**Greek Letters**:
```
Input:  "θ = 45°, α = 30°"
Output: "θ = 45°, α = 30°"  ✅ Recognized
```

## Common Math Expressions

### Well-Supported
- ✅ Variables: x, y, z, a, b, c
- ✅ Greek: α, β, γ, θ, π, Σ
- ✅ Operators: +, -, ×, ÷, =, ≠
- ✅ Powers: x², x³, xⁿ
- ✅ Fractions: ½, ¾, ⅓
- ✅ Roots: √, ∛
- ✅ Calculus: ∫, ∑, ∏, ∂

### May Need Improvement
- ⚠️ Complex LaTeX: \frac{a}{b}, \sqrt{x}
- ⚠️ Matrices and vectors
- ⚠️ Handwritten equations
- ⚠️ Very small subscripts/superscripts

## Troubleshooting

### Issue: Latin letters still not recognized
**Solution**: Ensure the service restarted and downloaded Latin models
```bash
# Check logs for:
"📄 Initializing EasyOCR with math support..."
"✅ EasyOCR initialized with math support"
```

### Issue: Low confidence scores
**Solutions**:
1. **Increase image quality**: Use higher resolution images
2. **Better contrast**: Ensure good contrast between text and background
3. **Clean images**: Remove noise, blur, or artifacts
4. **Proper orientation**: Ensure text is horizontal

### Issue: Symbols confused with letters
**Example**: "x" recognized as "×" or vice versa

**Solutions**:
1. Check context in the `details` array
2. Use confidence scores to filter uncertain results
3. Apply post-processing based on mathematical context

## Image Quality Tips

### ✅ Good for OCR
- High resolution (>800px width)
- Clear, sharp text
- Good contrast (dark text on light background)
- Horizontal orientation
- Minimal noise

### ❌ Poor for OCR
- Low resolution (<400px)
- Blurry or pixelated
- Poor contrast
- Rotated or skewed
- Noisy or compressed

## API Usage

### Basic Request
```bash
curl -X POST http://localhost:5001/api/extract-text \
  -F "file=@math_question.png"
```

### With Details
```bash
curl -X POST "http://localhost:5001/api/extract-text?include_details=true" \
  -F "file=@math_question.png"
```

### Check Languages
```bash
curl http://localhost:5001/api/languages
```

Expected response:
```json
{
  "languages": ["en", "la"],
  "features": ["math_symbols", "greek_letters", "latin_characters"],
  "note": "Optimized for mathematical expressions and educational content"
}
```

## Performance Notes

### First Request
- **Slower**: Downloads and loads Latin models (~50-100MB)
- **Time**: 30-60 seconds for first request
- **One-time**: Models are cached after first use

### Subsequent Requests
- **Faster**: Models already loaded
- **Time**: 2-5 seconds per image
- **Consistent**: Performance remains stable

## Next Steps

1. **Test thoroughly**: Try various math expressions
2. **Collect samples**: Gather problematic images for improvement
3. **Fine-tune parameters**: Adjust thresholds based on results
4. **Consider alternatives**: For complex LaTeX, consider specialized tools

## Additional Resources

- **EasyOCR Docs**: https://github.com/JaidedAI/EasyOCR
- **Supported Languages**: https://www.jaided.ai/easyocr/
- **Latin Recognition**: Uses `latin_g2` network for better symbol recognition
