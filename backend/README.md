# Backend API - OCR Integration

## Overview

This backend acts as a proxy between the frontend and the Azure OCR Function App, following the flow:

```
Frontend → Backend (/api/ocr/scan) → OCR Service → Backend → Frontend
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
OCR_FUNCTION_URL=https://qadam-ocr-addrcugfg4d4drg7.canadacentral-01.azurewebsites.net
PORT=5000
FRONTEND_URL=http://localhost:3000
```

### 3. Run the Server

```bash
python app.py
```

Server will start at `http://localhost:5000`

## API Endpoints

### 1. Health Check

**GET** `/api/health`

Check backend service health.

**Response:**
```json
{
  "status": "healthy",
  "service": "Main Backend",
  "ocr_service": "https://qadam-ocr-..."
}
```

### 2. OCR Scan (Main Endpoint)

**POST** `/api/ocr/scan`

Scan documents using OCR. Frontend calls this endpoint.

**Request Options:**

**Option A: File Upload (multipart/form-data)**
```bash
curl -X POST http://localhost:5000/api/ocr/scan \
  -F "file=@document.png" \
  -F "language=en"
```

**Option B: Base64 Image (JSON)**
```bash
curl -X POST http://localhost:5000/api/ocr/scan \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "iVBORw0KGgo...",
    "language": "en"
  }'
```

**Response:**
```json
{
  "success": true,
  "text": "Extracted text from document",
  "confidence": 0.95,
  "lines_detected": 5,
  "details": [
    {
      "text": "Line 1",
      "confidence": 0.97,
      "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
  ]
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

### 3. Supported Languages

**GET** `/api/ocr/languages`

Get list of supported OCR languages.

**Response:**
```json
{
  "success": true,
  "languages": {
    "en": "English",
    "ch": "Chinese",
    "hi": "Hindi",
    ...
  }
}
```

### 4. OCR Service Health

**GET** `/api/ocr/health`

Check OCR Azure Function health.

**Response:**
```json
{
  "status": "healthy",
  "service": "OCR Function App",
  "ocr_engine": "PaddleOCR",
  "paddleocr_installed": true,
  "paddleocr_version": "2.8.1"
}
```

## Frontend Integration

### JavaScript/TypeScript Example

```javascript
// File Upload
async function scanDocument(file) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', 'en');
  
  const response = await fetch('http://localhost:5000/api/ocr/scan', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  if (result.success) {
    console.log('Extracted text:', result.text);
    console.log('Confidence:', result.confidence);
  } else {
    console.error('OCR failed:', result.error);
  }
}

// Base64 Image
async function scanBase64Image(base64Image) {
  const response = await fetch('http://localhost:5000/api/ocr/scan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      image_base64: base64Image,
      language: 'en'
    })
  });
  
  const result = await response.json();
  return result;
}
```

### React Example

```jsx
import { useState } from 'react';

function OCRUpload() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', 'en');
    
    try {
      const response = await fetch('http://localhost:5000/api/ocr/scan', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <input type="file" onChange={handleFileUpload} accept="image/*,application/pdf" />
      {loading && <p>Processing...</p>}
      {result && result.success && (
        <div>
          <h3>Extracted Text:</h3>
          <p>{result.text}</p>
          <p>Confidence: {(result.confidence * 100).toFixed(1)}%</p>
        </div>
      )}
      {result && !result.success && (
        <p style={{color: 'red'}}>Error: {result.error}</p>
      )}
    </div>
  );
}
```

## Error Handling

The backend handles various error scenarios:

- **400 Bad Request**: Invalid input (missing file, invalid format)
- **503 Service Unavailable**: OCR service is down
- **504 Gateway Timeout**: OCR processing took too long
- **500 Internal Server Error**: Unexpected backend error

## Flow Diagram

```
┌──────────┐         ┌──────────┐         ┌─────────────┐
│ Frontend │────────▶│ Backend  │────────▶│ OCR Service │
│          │         │          │         │  (Azure)    │
└──────────┘         └──────────┘         └─────────────┘
     ▲                    │                       │
     │                    │                       │
     │                    ◀───────────────────────┘
     │                    │
     └────────────────────┘
          (Response)
```

## Testing

Run the test script to verify integration:

```bash
python test_backend.py
```

This will test:
- Backend health
- OCR service health
- Language support
- File upload OCR
- Base64 image OCR

## Deployment

For production deployment, consider:

1. Use environment variables for configuration
2. Add authentication/authorization
3. Implement rate limiting
4. Add request logging
5. Use production WSGI server (gunicorn, uwsgi)

Example with gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Notes

- Maximum file size: Limited by Azure Functions (typically 100MB)
- Timeout: 60 seconds for OCR processing
- Supported formats: PNG, JPG, JPEG, BMP, TIFF, PDF
- Supported languages: 17+ languages (see `/api/ocr/languages`)
