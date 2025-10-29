# Azure Function App Limitations & Workarounds

## 🚫 Known Limitations on Azure Free Tier

### 1. Tesseract OCR Not Available

**Issue:** Tesseract OCR requires a system binary that cannot be installed on Azure Function Apps free tier.

**Error:**
```
TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

**Workaround:**
- ✅ **Use text input** - Copy and paste question text directly
- ✅ **Use PDF files** - Text extraction from PDFs works (uses PyMuPDF)
- ✅ **Use DOCX files** - Text extraction from Word documents works
- ❌ **Image OCR** - Not available (JPG, PNG image uploads won't work)

**User Message:**
When users try to upload images, they'll see:
> "OCR not available on Azure. Please use text input or PDF/DOCX files instead."

### 2. System Package Installation

**Issue:** Cannot install system packages (apt-get, yum) on Azure Function Apps free tier.

**Affected Features:**
- Tesseract OCR (requires `tesseract` binary)
- Any other system-level dependencies

**Solution:** Use Python-only packages or cloud APIs instead.

## ✅ What Works on Azure

### AI Features (Fully Functional)
- ✅ **Groq API** - Text generation, question parsing, solution generation
- ✅ **TF-IDF Embeddings** - Text similarity, semantic search
- ✅ **Vector Search** - In-memory similarity search
- ✅ **PDF Text Extraction** - PyMuPDF works perfectly
- ✅ **DOCX Text Extraction** - python-docx works perfectly

### Database
- ✅ **Cosmos DB** - Primary database (Azure native)
- ✅ **MySQL** - Fallback (if configured)

### File Processing
- ✅ **PDF** - Full text extraction
- ✅ **DOCX** - Full text extraction
- ✅ **TXT** - Direct reading
- ❌ **Images (JPG/PNG)** - OCR not available

## 📋 Feature Availability Matrix

| Feature | Local | Azure Free Tier | Notes |
|---------|-------|-----------------|-------|
| Text Input | ✅ | ✅ | Always works |
| PDF Upload | ✅ | ✅ | PyMuPDF |
| DOCX Upload | ✅ | ✅ | python-docx |
| Image OCR | ✅ | ❌ | Requires Tesseract binary |
| Question Parsing | ✅ | ✅ | Groq API |
| Solution Generation | ✅ | ✅ | Groq API |
| Textbook Indexing | ✅ | ✅ | TF-IDF |
| Semantic Search | ✅ | ✅ | scikit-learn |
| Cosmos DB | ✅ | ✅ | Azure native |

## 🔧 Alternative Solutions for OCR

If OCR is critical, consider these options:

### Option 1: Azure Computer Vision API (Paid)
```python
from azure.cognitiveservices.vision.computervision import ComputerVisionClient

# Use Azure's OCR service
client = ComputerVisionClient(endpoint, credentials)
result = client.read(image_url)
```

**Pros:**
- Cloud-based, no binary needed
- High accuracy
- Supports multiple languages

**Cons:**
- Requires paid Azure subscription
- API costs per request

### Option 2: Google Cloud Vision API (Paid)
```python
from google.cloud import vision

client = vision.ImageAnnotatorClient()
response = client.text_detection(image=image)
```

**Pros:**
- High accuracy
- Good documentation

**Cons:**
- Requires Google Cloud account
- API costs per request

### Option 3: Client-Side OCR (Free)
Use Tesseract.js in the frontend:
```javascript
import Tesseract from 'tesseract.js';

Tesseract.recognize(image, 'eng')
  .then(({ data: { text } }) => {
    // Send extracted text to backend
  });
```

**Pros:**
- Free
- No backend changes needed
- Works with Azure free tier

**Cons:**
- Slower (runs in browser)
- Uses client's resources

## 📝 Recommendations

### For Current Setup (Azure Free Tier)
1. ✅ **Disable image upload** in UI or show clear warning
2. ✅ **Promote text input** as primary method
3. ✅ **Support PDF/DOCX** uploads (works perfectly)
4. ✅ **Use Groq API** for all AI features (working great!)

### For Future Upgrades
1. Consider Azure Computer Vision API if OCR is critical
2. Or implement client-side OCR with Tesseract.js
3. Or upgrade to Azure App Service (allows custom containers with Tesseract)

## 🎯 Current Status

**Deployment:** ✅ Fully functional on Azure
**AI Features:** ✅ Working (Groq + TF-IDF)
**OCR:** ⚠️ Not available (graceful error handling added)
**Workaround:** ✅ Text/PDF/DOCX input supported

The application is production-ready with the current limitations clearly communicated to users.
