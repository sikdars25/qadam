# OCR Service - EasyOCR

Simple OCR service using EasyOCR for text extraction from images and PDFs.

## Features

- ✅ Image OCR (PNG, JPG, etc.)
- ✅ PDF OCR (multi-page support)
- ✅ REST API
- ✅ High accuracy with EasyOCR
- ✅ No GPU required (CPU mode)

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

### Development
```bash
python app.py
```

### Production (with Gunicorn)
```bash
gunicorn --workers 2 --timeout 300 --bind 127.0.0.1:8000 app:app
```

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Extract Text from Image
```bash
POST /api/extract-text
Content-Type: application/json

{
  "image_base64": "base64_encoded_image"
}
```

Or with file upload:
```bash
POST /api/extract-text
Content-Type: multipart/form-data

file: <image_file>
```

### Extract Text from PDF
```bash
POST /api/extract-from-pdf
Content-Type: multipart/form-data

file: <pdf_file>
```

## Dependencies

- Flask: Web framework
- EasyOCR: OCR engine
- Pillow: Image processing
- PyMuPDF: PDF processing (optional)
- Gunicorn: Production server
