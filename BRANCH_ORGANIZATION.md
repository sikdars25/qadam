# QADAM Branch Organization - Greek/Math Character Support

## 📋 Branch Structure

### 🔧 backend-ocr
**Focus**: OCR service only
**Port**: 8000
**Greek/Math Support**: ✅ **Implemented**
- Uses `['en', 'la']` languages with `latin_g2` network
- Recognizes Greek letters (α, β, γ, θ, π, σ, Σ)
- Supports math symbols (√, ∫, ∑, ±, ×, ÷, ≤, ≥, ≠)
- Handles mathematical expressions and equations

**Files**:
- `ocr/app.py` - Main OCR service with Greek/math support
- `ocr/requirements.txt` - EasyOCR and dependencies
- `README.md` - OCR-specific documentation

### 🌐 backend-proxy  
**Focus**: Proxy service routing between OCR and AI
**Port**: 5001
**Greek/Math Support**: ✅ **Implemented**
- UTF-8 encoding for all request/response handling
- Routes OCR requests with `en,la` language support
- Preserves Greek characters and math symbols in pipeline
- Complete pipeline: Client → Proxy → OCR/AI

**Files**:
- `proxy/app.py` - Main proxy application
- `proxy/ocr_client.py` - OCR client with UTF-8 encoding
- `proxy/requirements.txt` - Flask and dependencies

### 🤖 backend-ai
**Focus**: AI service for solution generation
**Port**: 5002
**Greek/Math Support**: ✅ **Implemented**
- Math symbol recognition and processing
- Greek letter detection and analysis
- Solution generation for mathematical expressions
- Validation endpoint for math expressions

**Files**:
- `ai/app.py` - Main AI service with math processing
- `ai/requirements.txt` - Groq AI and dependencies
- Math symbol mappings and analysis functions

## 🎯 Greek/Math Character Features

### ✅ Supported Characters
- **Greek Letters**: α, β, γ, δ, θ, π, σ, Σ, etc.
- **Math Symbols**: √, ∫, ∑, ±, ×, ÷, ≠, ≤, ≥, etc.
- **Variables**: x, y, z, a, b, c, etc.
- **Equations**: Complete mathematical expressions

### 🔧 Implementation Details

#### OCR Service (backend-ocr)
```python
ocr_reader = easyocr.Reader(
    ['en', 'la'],  # English + Latin for math
    gpu=False,
    recog_network='latin_g2'  # Latin character recognition
)
```

#### Proxy Service (backend-proxy)
```python
# UTF-8 encoding headers
headers = {'Accept': 'application/json; charset=utf-8'}
# Language support for Greek/math
language='en,la'
```

#### AI Service (backend-ai)
```python
MATH_SYMBOLS = {
    'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta', 'θ': 'theta',
    'π': 'pi', 'σ': 'sigma', 'Σ': 'summation', '∫': 'integral', '√': 'sqrt',
    # ... more symbols
}
```

## 🚀 Deployment Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│   Proxy     │───▶│   AI        │
│             │    │  (5001)     │    │  (5002)     │
└─────────────┘    └─────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │    OCR      │
                   │  (8000)     │
                   └─────────────┘
```

## 📝 API Endpoints

### OCR Service (Port 8000)
- `GET /api/health` - Health check
- `POST /api/extract-text` - Extract text with Greek/math support
- `GET /api/languages` - Supported languages

### Proxy Service (Port 5001)
- `GET /api/health` - Health check
- `POST /api/extract-text` - Proxy OCR with UTF-8 encoding
- `POST /api/generate-solution` - Proxy AI solution generation
- `POST /api/process-question` - Complete pipeline

### AI Service (Port 5002)
- `GET /api/health` - Health check
- `POST /api/solve-question` - Solve questions with math analysis
- `POST /api/validate-math` - Validate mathematical expressions

## ✅ Summary

Greek/math character support has been successfully implemented across all three services in their respective branches:

1. **backend-ocr**: Core OCR recognition with Latin language support
2. **backend-proxy**: UTF-8 encoding and routing with language preservation  
3. **backend-ai**: Math symbol processing and solution generation

Each branch can be deployed independently while maintaining full Greek/math character support throughout the pipeline.
