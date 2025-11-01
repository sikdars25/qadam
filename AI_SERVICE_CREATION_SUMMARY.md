# AI Service Azure Function App - Creation Summary

**Date**: November 1, 2025  
**Branch**: `backend-ai`  
**Repository**: https://github.com/sikdars25/qadam/tree/backend-ai/ai

## Overview

Created a dedicated Azure Function App for AI operations, separating AI functionality from the main Flask backend into a native serverless function app.

## What Was Created

### New Branch: `backend-ai`

A dedicated branch for the AI service, similar to `backend-ocr` for OCR functionality.

### New Folder: `ai/`

Complete Azure Function App structure with all AI-related code:

```
ai/
├── function_app.py          # Main Azure Function endpoints
├── ai_helpers.py            # Groq API wrapper and utilities
├── ai_service.py            # AI service logic (TextbookIndex, etc.)
├── requirements.txt         # Python dependencies
├── host.json               # Azure Functions configuration
├── .funcignore             # Files to exclude from deployment
├── .gitignore              # Git ignore patterns
├── .env.example            # Environment variable template
├── README.md               # Service documentation
└── AZURE_SETUP.md          # Azure deployment guide
```

## AI Endpoints Created

### 1. Health Check
```
GET /api/health
```
Returns service status and available AI features.

### 2. Solve Question
```
POST /api/solve-question
Body: {
  "question_text": "Question to solve",
  "subject": "Physics" (optional),
  "context": "Additional context" (optional)
}
```
Generates step-by-step solutions using Groq API.

### 3. Generate Text
```
POST /api/generate-text
Body: {
  "prompt": "Your prompt",
  "model": "llama-3.3-70b-versatile" (optional),
  "max_tokens": 1000 (optional),
  "temperature": 0.7 (optional)
}
```
General-purpose text generation with Groq's Llama models.

### 4. Semantic Search
```
POST /api/semantic-search
Body: {
  "query": "Search query",
  "documents": [{"id": "1", "text": "Document text"}, ...],
  "top_k": 5 (optional)
}
```
TF-IDF based similarity search for documents.

### 5. Parse Questions
```
POST /api/parse-questions
Body: {
  "text": "Text containing questions"
}
```
Extract and parse questions from text using Groq AI.

### 6. Map to Chapters
```
POST /api/map-to-chapters
Body: {
  "question_text": "Question to map",
  "chapters": [{"name": "Chapter 1", "text": "Content"}, ...]
}
```
Map questions to relevant textbook chapters.

## Code Extracted from Backend

### From `backend/ai_helpers.py`:
- ✅ Groq API client initialization
- ✅ `generate_with_groq()` - Text generation
- ✅ `generate_solution()` - Question solving
- ✅ `parse_questions_from_text()` - Question parsing
- ✅ `search_similar_texts()` - Semantic search
- ✅ `map_question_to_chapters()` - Chapter mapping
- ✅ TF-IDF vectorization utilities

### From `backend/ai_service.py`:
- ✅ `TextbookIndex` class
- ✅ PDF text extraction
- ✅ Question paper analysis
- ✅ Semantic textbook search

## Environment Variables

### Required:
- **`GROQ_API_KEY`**: Groq API key for LLM inference

This is the same key used by the main backend, ensuring consistency.

## GitHub Workflow

Created `.github/workflows/backend-ai_qadam-ai.yml`:

- **Trigger**: Push to `backend-ai` branch or changes in `ai/` folder
- **Build**: Install dependencies to `.python_packages`
- **Deploy**: Deploy to Azure Function App `qadam-ai`
- **Secret**: Uses `AZURE_AI_FUNCTIONAPP_PUBLISH_PROFILE`

## Dependencies

```
azure-functions
groq==0.11.0
scikit-learn
numpy
PyMuPDF
```

All lightweight, Azure free-tier compatible.

## Architecture Benefits

### Before (Monolithic):
```
backend/
├── app.py (Flask + AI + Database + Auth)
├── ai_service.py
├── ai_helpers.py
└── ...
```

### After (Microservices):
```
backend/          # Flask app (Auth, Database, CRUD)
ocr/             # OCR Function App
ai/              # AI Function App (NEW)
frontend/        # React app
```

### Advantages:

1. **Separation of Concerns**: AI logic isolated from main backend
2. **Independent Scaling**: AI functions scale separately
3. **Easier Maintenance**: Changes to AI don't affect backend
4. **Better Performance**: Serverless functions for AI workloads
5. **Cost Optimization**: Pay only for AI function execution
6. **Deployment Flexibility**: Deploy AI updates independently

## Deployment Steps

### 1. Create Azure Function App

```bash
# Via Azure Portal:
- Name: qadam-ai
- Runtime: Python 3.10
- Plan: Consumption (Serverless)
- Region: Same as backend
```

### 2. Download Publish Profile

From Azure Portal → `qadam-ai` → Get publish profile

### 3. Add GitHub Secret

```
Name: AZURE_AI_FUNCTIONAPP_PUBLISH_PROFILE
Value: (contents of publish profile)
```

### 4. Configure Environment Variables

In Azure Portal → `qadam-ai` → Configuration:
```
GROQ_API_KEY = your_groq_api_key
```

### 5. Deploy

```bash
# Already done - pushed to backend-ai branch
# GitHub Actions will deploy automatically
```

## Repository Structure

### Branches:

- **`main`**: Production backend (Flask) + frontend
- **`backend-ocr`**: OCR Function App
- **`backend-ai`**: AI Function App (NEW)

### URLs:

- **Main Backend**: https://qadam-backend.azurewebsites.net
- **OCR Service**: https://qadam-ocr.azurewebsites.net
- **AI Service**: https://qadam-ai.azurewebsites.net (to be deployed)
- **Frontend**: https://zealous-ocean-06e22b51e.3.azurestaticapps.net

## Next Steps

1. **Create Azure Function App** `qadam-ai` in Azure Portal
2. **Add publish profile** to GitHub Secrets
3. **Set `GROQ_API_KEY`** in Azure Function App settings
4. **Monitor deployment** at https://github.com/sikdars25/qadam/actions
5. **Test endpoints** using the health check and solve-question APIs
6. **Update main backend** to call AI service instead of local AI code (optional)

## Integration with Main Backend

The main backend can now call the AI service via HTTP:

```python
# Instead of:
from ai_service import generate_question_solution
solution = generate_question_solution(question_text)

# Use:
import requests
response = requests.post(
    'https://qadam-ai.azurewebsites.net/api/solve-question',
    json={'question_text': question_text, 'subject': subject}
)
solution = response.json()['solution']
```

## Cost Estimate

**Azure Consumption Plan**:
- First 1 million executions: FREE
- Additional: $0.20 per million
- Memory: $0.000016/GB-s

**Expected Monthly Cost**: $0 (within free tier)

## Verification

After deployment, test:

```bash
# Health check
curl https://qadam-ai.azurewebsites.net/api/health

# Solve question
curl -X POST https://qadam-ai.azurewebsites.net/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{"question_text": "What is 2 + 2?", "subject": "Math"}'
```

## Summary

✅ **Created**: Dedicated AI Azure Function App  
✅ **Branch**: `backend-ai`  
✅ **Folder**: `ai/`  
✅ **Endpoints**: 6 AI-powered APIs  
✅ **Workflow**: Automated deployment via GitHub Actions  
✅ **Documentation**: Complete setup and usage guides  
✅ **Code**: Extracted all AI logic from backend  
✅ **Dependencies**: Lightweight, free-tier compatible  

The AI service is now ready for deployment as a standalone Azure Function App! 🚀
