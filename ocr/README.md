# OCR Function App

Separate Azure Function App for OCR processing using PaddleOCR.

**Last Deployment**: November 1, 2025 5:10 PM IST - Successfully deployed to Azure VM

## 🎯 Why Separate Function App?

1. **Avoid Dependency Conflicts** - PaddleOCR has heavy dependencies that conflict with other packages
2. **Independent Scaling** - OCR can scale separately from main backend
3. **Better Performance** - Dedicated resources for OCR processing
4. **Easier Maintenance** - OCR updates don't affect main backend

## 🚀 Features

- ✅ **PaddleOCR** - Better accuracy than Tesseract
- ✅ **80+ Languages** - Including Hindi, Tamil, Telugu, etc.
- ✅ **Handwriting Recognition** - Works with handwritten text
- ✅ **No System Dependencies** - Pure Python, no binaries needed
- ✅ **PDF Support** - Extract text from PDF images
- ✅ **Bounding Boxes** - Get text coordinates for layout analysis

## 📋 API Endpoints

### 1. Health Check
```
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "service": "OCR Function App",
  "ocr_engine": "PaddleOCR"
}
```

### 2. OCR Image
```
POST /api/ocr/image
```

**Request (File Upload):**
```bash
curl -X POST \
  -F "file=@image.png" \
  -F "language=en" \
  https://qadam-ocr.azurewebsites.net/api/ocr/image
```

**Request (Base64):**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "text": "Extracted text from image",
  "confidence": 0.95,
  "lines_detected": 5,
  "details": [
    {
      "text": "Line 1",
      "confidence": 0.98,
      "bbox": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    }
  ]
}
```

### 3. OCR PDF
```
POST /api/ocr/pdf
```

**Request:**
```bash
curl -X POST \
  -F "file=@document.pdf" \
  -F "language=en" \
  https://qadam-ocr.azurewebsites.net/api/ocr/pdf
```

**Response:**
```json
{
  "success": true,
  "text": "Full text from all pages",
  "total_pages": 3,
  "pages": [
    "Page 1 text",
    "Page 2 text",
    "Page 3 text"
  ]
}
```

### 4. Supported Languages
```
GET /api/ocr/languages
```

Response:
```json
{
  "success": true,
  "languages": {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    ...
  }
}
```

## 🛠️ Local Development

### 1. Install Dependencies

```bash
cd ocr
pip install -r requirements.txt
```

### 2. Create .env File

```bash
cp .env.example .env
```

Edit `.env`:
```
FRONTEND_URL=http://localhost:3000
PORT=8000
```

### 3. Run Locally

```bash
python app.py
```

Server runs on: http://localhost:8000

### 4. Test OCR

```bash
# Test with image
curl -X POST \
  -F "file=@test.png" \
  http://localhost:8000/api/ocr/image

# Test health
curl http://localhost:8000/api/health
```

## ☁️ Azure Deployment

### 1. Create Azure Function App

```bash
az functionapp create \
  --name qadam-ocr \
  --resource-group qadam-rg \
  --consumption-plan-location centralus \
  --runtime python \
  --runtime-version 3.10 \
  --functions-version 4 \
  --os-type Linux \
  --storage-account qadamstorage
```

### 2. Get Publish Profile

1. Go to Azure Portal
2. Navigate to Function App → `qadam-ocr`
3. Click **"Get publish profile"**
4. Download the file

### 3. Add GitHub Secret

1. Go to GitHub repository → Settings → Secrets
2. Click **"New repository secret"**
3. Name: `AZURE_OCR_FUNCTIONAPP_PUBLISH_PROFILE`
4. Value: Paste contents of publish profile file
5. Click **"Add secret"**

### 4. Deploy

Push to main branch:
```bash
git add backend/ocr/
git commit -m "Add OCR Function App"
git push origin main
```

GitHub Actions will automatically deploy!

### 5. Configure CORS

In Azure Portal → Function App → CORS:
- Add your frontend URL
- Add `https://*.azurestaticapps.net`

## 🔧 Configuration

### Environment Variables (Azure)

Add in Function App → Configuration → Application settings:

| Name | Value | Description |
|------|-------|-------------|
| `FRONTEND_URL` | `https://your-app.azurestaticapps.net` | Frontend URL for CORS |
| `DEFAULT_OCR_LANGUAGE` | `en` | Default language |

## 📊 Performance

- **Cold Start:** ~10-15 seconds (first request)
- **Warm Start:** ~1-2 seconds
- **OCR Processing:** ~2-5 seconds per image
- **PDF Processing:** ~3-6 seconds per page

## 💰 Cost

**Azure Function App (Consumption Plan):**
- First 1 million executions: FREE
- After: $0.20 per million executions
- Memory: $0.000016/GB-s

**Typical Usage:**
- 1000 OCR requests/month = FREE
- Well within free tier!

## 🔗 Integration with Main Backend

Update main backend to call OCR service:

```python
import requests

def ocr_image(image_file):
    """Call OCR Function App"""
    ocr_url = "https://qadam-ocr.azurewebsites.net/api/ocr/image"
    
    files = {'file': image_file}
    response = requests.post(ocr_url, files=files)
    
    if response.status_code == 200:
        return response.json()['text']
    else:
        raise Exception(f"OCR failed: {response.text}")
```

## 🐛 Troubleshooting

### PaddleOCR not initializing
- Check logs in Azure Portal → Function App → Log stream
- Ensure Python 3.10 is used
- Increase timeout in `host.json`

### Out of memory
- Increase Function App plan (not needed for most cases)
- Process images in smaller batches

### Slow performance
- First request is always slow (cold start)
- Keep function warm with periodic health checks

## 📚 Resources

- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- [Azure Functions Python Guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Supported Languages](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_en/multi_languages_en.md)
