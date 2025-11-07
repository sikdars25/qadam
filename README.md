# QADAM - OCR Service (Local Development)

OCR Service for text extraction from images using EasyOCR.

**Branch**: `backend-ocr`  
**Folder**: `ocr/`  
**Port**: 8000

## 🚀 Quick Start

### 1. Setup OCR Service
```bash
.\setup_ocr_only.bat
```

This will:
- Checkout `backend-ocr` branch
- Create Python virtual environment
- Install EasyOCR and dependencies
- Create `.env` configuration file

### 2. Run OCR Service
```bash
.\run_ocr_only.bat
```

The service will start on: **http://localhost:8000**

### 3. Test OCR Service
```bash
# Health check
curl http://localhost:8000/api/health

# Extract text from image
curl -X POST -F "file=@test.png" http://localhost:8000/api/extract-text
```

## 📋 API Endpoints

### Health Check
```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "OCR Service (Flask on VM)",
  "ocr_engine": "EasyOCR",
  "easyocr_installed": true
}
```

### Extract Text from Image
```
POST /api/extract-text
```

**Request (File Upload):**
```bash
curl -X POST \
  -F "file=@image.png" \
  http://localhost:8000/api/extract-text
```

**Request (Base64):**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Response:**
```json
{
  "success": true,
  "text": "Extracted text from image",
  "confidence": 0.95,
  "details": [
    {
      "text": "Line 1",
      "confidence": 0.98,
      "bbox": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    }
  ]
}
```

### Extract Text from PDF
```
POST /api/extract-from-pdf
```

**Request:**
```bash
curl -X POST \
  -F "file=@document.pdf" \
  http://localhost:8000/api/extract-from-pdf
```

**Response:**
```json
{
  "success": true,
  "text": "Full text from all pages",
  "pages": 3
}
```

## 🛠️ Manual Setup (Alternative)

If you prefer manual setup:

```bash
# 1. Checkout OCR branch
git checkout backend-ocr

# 2. Navigate to OCR folder
cd ocr

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
venv\Scripts\activate.bat

# 5. Install dependencies
pip install -r requirements.txt

# 6. Create .env file
echo FLASK_ENV=development > .env
echo PORT=8000 >> .env

# 7. Run the service
python app.py
```

## 📁 Project Structure

```
aqnamic/
├── ocr/                    # OCR service (backend-ocr branch)
│   ├── app.py             # Flask application
│   ├── requirements.txt   # Python dependencies
│   ├── .env              # Configuration
│   └── venv/             # Virtual environment
├── setup_ocr_only.bat    # Setup script
└── run_ocr_only.bat      # Run script
```

## 🔧 Configuration

Edit `ocr/.env`:

```env
FLASK_ENV=development
PORT=8000
OCR_LANGUAGES=en
FRONTEND_URL=http://localhost:3000
```

## 🐛 Troubleshooting

### "Module not found" error
```bash
cd ocr
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Port already in use
```bash
# Change port in ocr/.env
PORT=5001
```

### EasyOCR initialization fails
```bash
# Reinstall EasyOCR
pip uninstall easyocr
pip install easyocr==1.7.0
```

## ☁️ Deployment

The OCR service is deployed to Azure VM:
- **Public IP**: 130.107.48.145
- **Port**: 8000
- **Health Check**: http://130.107.48.145:8000/api/health

Deployment is automated via GitHub Actions when you push to `backend-ocr` branch.

## 📚 Documentation

- [OCR VM Deployment Guide](DEPLOY_OCR_VM_COMPLETE_GUIDE.md)
- [GitHub Workflow](.github/workflows/deploy-ocr-vm.yml)
- [EasyOCR Documentation](https://github.com/JaidedAI/EasyOCR)

## 🎯 Features

- ✅ **EasyOCR** - Accurate text extraction
- ✅ **Multi-language** - English + 80+ languages
- ✅ **PDF Support** - Extract text from PDF documents
- ✅ **Bounding Boxes** - Get text coordinates
- ✅ **No GPU Required** - Runs on CPU
- ✅ **Easy Setup** - One-click installation

## 💡 Tips

- First OCR request takes ~10-15 seconds (model loading)
- Subsequent requests are faster (~2-5 seconds)
- For best results, use clear, high-contrast images
- Supported formats: PNG, JPG, JPEG, PDF
