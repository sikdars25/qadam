# OCR Endpoints Documentation

## Overview

The backend provides multiple OCR endpoints for different use cases:

1. **`/api/ocr/extract`** - Simple OCR extraction (NEW - Recommended for testing)
2. **`/api/parse-single-question`** - OCR + Question parsing
3. **`/api/ocr/warmup`** - Warmup OCR service

---

## 1. Simple OCR Extraction (Recommended)

### Endpoint
```
POST /api/ocr/extract
```

### Description
Extracts text from an image using the OCR Azure Function. This endpoint bypasses question parsing and returns raw OCR results. **Use this for direct OCR testing.**

### Request
**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Image file (PNG, JPG, JPEG, etc.)
- `language` (optional): Language code (default: 'en')

### Example Request

**cURL:**
```bash
curl -X POST https://qadam-backend.azurewebsites.net/api/ocr/extract \
  -F "file=@image.png" \
  -F "language=en"
```

**Python:**
```python
import requests

files = {'file': open('image.png', 'rb')}
data = {'language': 'en'}

response = requests.post(
    'https://qadam-backend.azurewebsites.net/api/ocr/extract',
    files=files,
    data=data
)

result = response.json()
print(f"Text: {result['text']}")
print(f"Confidence: {result['confidence']}")
```

**JavaScript:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('language', 'en');

const response = await fetch('https://qadam-backend.azurewebsites.net/api/ocr/extract', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log('Text:', result.text);
console.log('Confidence:', result.confidence);
```

### Response

**Success (200):**
```json
{
  "success": true,
  "text": "What is the capital of France?",
  "confidence": 0.95,
  "lines_detected": 1,
  "details": [
    {
      "text": "What is the capital of France?",
      "confidence": 0.95,
      "bbox": [[10, 20], [300, 20], [300, 40], [10, 40]]
    }
  ],
  "message": "OCR completed successfully"
}
```

**Error (400/500):**
```json
{
  "success": false,
  "error": "No file uploaded"
}
```

### Performance
- **First request (cold start):** 60-90 seconds (model download)
- **Subsequent requests:** 2-10 seconds
- **Timeout:** 120 seconds

---

## 2. Parse Single Question (With Question Parsing)

### Endpoint
```
POST /api/parse-single-question
```

### Description
Extracts text from an image AND parses it as a question. This endpoint includes additional question parsing logic.

### Request
**Content-Type:** `multipart/form-data`

**Parameters:**
- `input_type` (required): 'file' or 'text'
- `file_type` (required for file): 'png', 'jpg', 'jpeg', 'pdf', 'docx'
- `file` (required for file): The file to process
- `question_text` (required for text): Direct text input

### Example Request

**cURL:**
```bash
curl -X POST https://qadam-backend.azurewebsites.net/api/parse-single-question \
  -F "input_type=file" \
  -F "file_type=png" \
  -F "file=@question.png"
```

### Response

**Success (200):**
```json
{
  "success": true,
  "question_text": "What is the capital of France?",
  "parsed_data": {
    // Additional parsed question data
  }
}
```

**Note:** This endpoint may fail if question parsing logic has issues. Use `/api/ocr/extract` for pure OCR testing.

---

## 3. Warmup OCR Service

### Endpoint
```
POST /api/ocr/warmup
```

### Description
Pre-downloads PaddleOCR models to avoid delays on first user request. Call this after deployment.

### Request
No parameters required.

### Example Request

**cURL:**
```bash
curl -X POST https://qadam-backend.azurewebsites.net/api/ocr/warmup
```

**Python:**
```python
import requests

response = requests.post(
    'https://qadam-backend.azurewebsites.net/api/ocr/warmup',
    timeout=180
)

result = response.json()
print(result['message'])
```

### Response

**Success (200):**
```json
{
  "success": true,
  "message": "OCR service warmed up successfully"
}
```

**Error (503):**
```json
{
  "success": false,
  "message": "OCR service warmup failed"
}
```

### Performance
- **Duration:** 60-90 seconds (first time)
- **Duration:** 2-5 seconds (if models already downloaded)

---

## Supported Languages

Get list of supported languages:

```bash
curl https://qadam-ocr-addrcugfg4d4drg7.canadacentral-01.azurewebsites.net/api/ocr/languages
```

**Supported:** English, Chinese, Tamil, Telugu, Kannada, Hindi, Marathi, Nepali, Urdu, Arabic, French, German, Japanese, Korean, Russian, Spanish, Portuguese

---

## Testing Flow

### 1. Test OCR Service Directly
```bash
curl https://qadam-ocr-addrcugfg4d4drg7.canadacentral-01.azurewebsites.net/api/health
```

### 2. Test Backend OCR Integration
```bash
curl -X POST https://qadam-backend.azurewebsites.net/api/ocr/extract \
  -F "file=@test.png" \
  -F "language=en"
```

### 3. Test Full Question Parsing
```bash
curl -X POST https://qadam-backend.azurewebsites.net/api/parse-single-question \
  -F "input_type=file" \
  -F "file_type=png" \
  -F "file=@question.png"
```

---

## Troubleshooting

### Issue: Timeout Error
**Cause:** First request downloads PaddleOCR models (~15 MB)  
**Solution:** 
- Wait 60-90 seconds for first request
- Call `/api/ocr/warmup` after deployment
- Subsequent requests will be fast

### Issue: 500 Internal Server Error
**Cause:** Various (check logs)  
**Solution:**
- Use `/api/ocr/extract` instead of `/api/parse-single-question`
- Check Azure Function logs
- Verify `OCR_SERVICE_URL` environment variable is set

### Issue: 404 Not Found
**Cause:** Endpoint doesn't exist or deployment incomplete  
**Solution:**
- Wait for deployment to complete
- Check GitHub Actions status
- Verify correct URL

---

## Environment Variables

Required environment variables for backend:

```bash
OCR_SERVICE_URL=https://qadam-ocr-addrcugfg4d4drg7.canadacentral-01.azurewebsites.net
```

Set using:
```bash
az webapp config appsettings set \
  --name qadam-backend \
  --resource-group qadam_bend_group \
  --settings OCR_SERVICE_URL=https://qadam-ocr-addrcugfg4d4drg7.canadacentral-01.azurewebsites.net
```

---

## Architecture

```
┌──────────┐         ┌──────────────┐         ┌─────────────────┐
│ Frontend │────────▶│   Backend    │────────▶│  OCR Function   │
│          │         │ Flask/Azure  │         │   PaddleOCR     │
└──────────┘         └──────────────┘         └─────────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Database   │
                     │ (Optional)   │
                     └──────────────┘
```

**Flow:**
1. Frontend uploads image to backend
2. Backend saves temp file
3. Backend calls OCR Azure Function
4. OCR processes with PaddleOCR
5. Backend receives OCR result
6. Backend optionally parses/processes
7. Backend returns to frontend

---

## Quick Start

1. **Deploy backend** (automatic via GitHub Actions)
2. **Set environment variable:**
   ```bash
   az webapp config appsettings set --name qadam-backend --resource-group qadam_bend_group --settings OCR_SERVICE_URL=https://qadam-ocr-addrcugfg4d4drg7.canadacentral-01.azurewebsites.net
   ```
3. **Warmup OCR service:**
   ```bash
   curl -X POST https://qadam-backend.azurewebsites.net/api/ocr/warmup
   ```
4. **Test OCR extraction:**
   ```bash
   curl -X POST https://qadam-backend.azurewebsites.net/api/ocr/extract -F "file=@test.png"
   ```

Done! 🎉
