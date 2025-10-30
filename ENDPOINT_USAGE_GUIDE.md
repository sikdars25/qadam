# Backend Endpoint Usage Guide

## ⚠️ Important: Different Endpoints for Different Purposes

The error you're seeing is because `/api/parse-single-question` requires `GROQ_API_KEY` for AI-powered question parsing. This is **different** from the OCR endpoints.

---

## 📋 Available Endpoints

### 1. Simple OCR Extraction (✅ Recommended - No API Key Required)

**Endpoint:** `POST /api/ocr/extract`

**Purpose:** Extract text from images using PaddleOCR  
**Requires:** No API keys  
**Returns:** Raw OCR text with confidence scores  

**Example:**
```bash
curl -X POST https://qadam-backend.azurewebsites.net/api/ocr/extract \
  -F "file=@image.png" \
  -F "language=en"
```

**Response:**
```json
{
  "success": true,
  "text": "Extracted text here",
  "confidence": 0.95,
  "lines_detected": 3
}
```

---

### 2. OCR Warmup (✅ No API Key Required)

**Endpoint:** `POST /api/ocr/warmup`

**Purpose:** Pre-download PaddleOCR models  
**Requires:** No API keys  
**Use:** Call after deployment to avoid first-user delay  

**Example:**
```bash
curl -X POST https://qadam-backend.azurewebsites.net/api/ocr/warmup
```

**Response:**
```json
{
  "success": true,
  "message": "OCR service warmed up successfully"
}
```

---

### 3. Parse Single Question (⚠️ Requires GROQ_API_KEY)

**Endpoint:** `POST /api/parse-single-question`

**Purpose:** OCR + AI-powered question parsing  
**Requires:** `GROQ_API_KEY` environment variable  
**Returns:** Parsed question with AI analysis  

**Example:**
```bash
curl -X POST https://qadam-backend.azurewebsites.net/api/parse-single-question \
  -F "input_type=file" \
  -F "file_type=png" \
  -F "file=@question.png"
```

**Error if GROQ_API_KEY not set:**
```
❌ GROQ_API_KEY not configured
```

---

## 🔑 Setting Up GROQ_API_KEY (Optional)

If you want to use `/api/parse-single-question`, you need to set the GROQ API key:

```bash
az webapp config appsettings set \
  --name qadam-backend \
  --resource-group qadam_bend_group \
  --settings GROQ_API_KEY=your_groq_api_key_here
```

**Get GROQ API Key:**
1. Go to https://console.groq.com
2. Sign up/Login
3. Create an API key
4. Set it in Azure

---

## 🎯 Which Endpoint Should You Use?

### For Simple Text Extraction from Images:
✅ **Use `/api/ocr/extract`**
- No API key required
- Fast and simple
- Returns raw OCR text

### For AI-Powered Question Analysis:
⚠️ **Use `/api/parse-single-question`**
- Requires GROQ_API_KEY
- Parses question structure
- AI-enhanced analysis

### To Pre-warm the Service:
✅ **Use `/api/ocr/warmup`**
- No API key required
- Call after deployment
- Avoids first-user delay

---

## 🐛 Troubleshooting

### Error: "GROQ_API_KEY not configured"

**Cause:** You're calling `/api/parse-single-question` without setting GROQ_API_KEY

**Solutions:**
1. **Option A:** Use `/api/ocr/extract` instead (no API key needed)
2. **Option B:** Set GROQ_API_KEY environment variable

### Error: "OCR service timeout"

**Cause:** First request downloading PaddleOCR models

**Solution:** 
- Wait 60-90 seconds for first request
- Call `/api/ocr/warmup` after deployment

### Error: "Failed to parse question"

**Cause:** Question parsing logic error (not OCR related)

**Solution:**
- Use `/api/ocr/extract` for pure OCR
- Check GROQ_API_KEY is set if using question parser

---

## 📊 Endpoint Comparison

| Endpoint | Purpose | API Key Required | Response Time | Use Case |
|----------|---------|------------------|---------------|----------|
| `/api/ocr/extract` | OCR only | ❌ No | 2-10s | Text extraction |
| `/api/ocr/warmup` | Pre-download models | ❌ No | 60-90s (first time) | After deployment |
| `/api/parse-single-question` | OCR + AI parsing | ✅ Yes (GROQ) | 10-30s | Question analysis |

---

## ✅ Recommended Workflow

### 1. After Deployment
```bash
# Warmup the OCR service
curl -X POST https://qadam-backend.azurewebsites.net/api/ocr/warmup
```

### 2. For Text Extraction
```bash
# Use simple OCR endpoint
curl -X POST https://qadam-backend.azurewebsites.net/api/ocr/extract \
  -F "file=@image.png"
```

### 3. For Question Parsing (Optional)
```bash
# First, set GROQ_API_KEY
az webapp config appsettings set --name qadam-backend --resource-group qadam_bend_group --settings GROQ_API_KEY=xxx

# Then use question parser
curl -X POST https://qadam-backend.azurewebsites.net/api/parse-single-question \
  -F "input_type=file" \
  -F "file_type=png" \
  -F "file=@question.png"
```

---

## 🎉 Summary

**For OCR (No API Key):**
- ✅ `/api/ocr/extract` - Extract text from images
- ✅ `/api/ocr/warmup` - Pre-download models

**For AI Question Parsing (Requires GROQ_API_KEY):**
- ⚠️ `/api/parse-single-question` - Parse questions with AI

**Your Error:**
You're calling `/api/parse-single-question` which requires GROQ_API_KEY. Either:
1. Set the GROQ_API_KEY environment variable, OR
2. Use `/api/ocr/extract` instead (recommended for simple OCR)

---

**Last Updated:** October 30, 2025  
**Status:** OCR endpoints working, GROQ_API_KEY optional for question parsing
