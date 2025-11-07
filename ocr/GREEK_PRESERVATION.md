# Greek Letter Preservation in OCR

## 🎯 Overview

The OCR service is designed to **preserve Greek letters and mathematical symbols exactly as they appear** in the source text. No automatic corrections or transformations are applied to Greek characters.

## ✅ Preserved Characters

### Greek Letters
- **Lambda expressions**: λn, λp, λx, λy, λz, λa, λb, λc
- **Lambda division**: λn/λp (preserved exactly)
- **Other Greek letters**: α, β, γ, δ, θ, π, σ, Σ, etc.

### Mathematical Symbols
- **Integration**: ∫
- **Summation**: ∑
- **Square root**: √
- **Operations**: ±, ×, ÷
- **Comparisons**: ≤, ≥, ≠
- **Other symbols**: Various mathematical notation

## 🔧 Implementation

### OCR Configuration
```python
ocr_reader = easyocr.Reader(
    ['en', 'la'],  # English + Latin for math expressions
    gpu=False,
    recog_network='latin_g2'  # Latin character recognition
)
```

### Text Processing
- **No corrections applied** to Greek letters
- **UTF-8 encoding** maintained throughout
- **Original text preserved** exactly as detected
- **Mathematical expressions** kept intact

## 📋 Response Format

```json
{
  "success": true,
  "text": "λn + λp = λn/λp",  // Preserved exactly
  "confidence": 0.95,
  "details": [...]
}
```

## 🧪 Testing

Run the preservation test:

```bash
cd ocr
python test_greek_preservation.py
```

### Expected Preservations
- ✅ `λn = 5` → `λn = 5` (preserved)
- ✅ `λp = 10` → `λp = 10` (preserved)
- ✅ `λn/λp = 0.5` → `λn/λp = 0.5` (preserved)
- ✅ `α + β = γ` → `α + β = γ` (preserved)
- ✅ `∫f(x)dx = F(x) + C` → `∫f(x)dx = F(x) + C` (preserved)

## 🔍 Health Check

The OCR service health check shows preservation capabilities:

```bash
curl http://localhost:8000/api/health
```

Response includes:
```json
{
  "features": [
    "greek_math_support",
    "utf8_encoding", 
    "symbol_recognition",
    "latin_language_support"
  ],
  "supported_symbols": [
    "Greek letters: α, β, γ, δ, θ, π, σ, Σ, λ, etc.",
    "Math symbols: √, ∫, ∑, ±, ×, ÷, ≤, ≥, ≠, etc.",
    "Variables: λn, λp, λn/λp preserved as-is"
  ]
}
```

## 🚀 Usage

### Direct OCR
```bash
curl -X POST -F "file=@greek_math.png" \
  http://localhost:8000/api/extract-text
```

### Via Proxy Service
```bash
curl -X POST -F "file=@greek_math.png" \
  http://localhost:5001/api/extract-text
```

Both endpoints preserve Greek letters exactly as detected.

## 📝 Important Notes

### No Automatic Corrections
- **λn** stays as **λn** (not changed to 4n)
- **λp** stays as **λp** (not changed to 2p)
- **λn/λp** stays as **λn/λp** (not changed to ^n Ap)

### UTF-8 Encoding
- All text processing maintains UTF-8 encoding
- Greek characters are properly handled
- No character loss during transmission

### Integration
- **Proxy Service**: Preserves Greek letters through routing
- **AI Service**: Receives original Greek text for processing
- **Pipeline**: End-to-end preservation maintained

## 🔧 Configuration

The OCR service uses:
- **EasyOCR** with Latin language support
- **latin_g2** recognition network for better symbol detection
- **UTF-8 encoding** throughout the pipeline
- **No post-processing corrections** for Greek letters

## 📊 Benefits

1. **Accuracy**: Mathematical expressions preserved exactly
2. **Consistency**: No unexpected character transformations
3. **Compatibility**: Works with downstream AI processing
4. **Reliability**: Predictable text output for testing

The OCR service ensures that Greek letters and mathematical symbols are accurately detected and preserved without any automatic modifications.
