# AI Architecture for Azure Free Tier

## Current Setup Issues
- Heavy AI dependencies (PyTorch, FAISS) exceed Azure Functions limits
- Deployment package size: ~1.5+ GB
- Azure Functions limit: 1.5 GB total

## Recommended Architecture

### 1. OCR (Optical Character Recognition)

**Option A: Azure Computer Vision API (Recommended)**
- **Service:** Azure Cognitive Services - Computer Vision
- **Free Tier:** 5,000 transactions/month
- **Pros:** 
  - No local dependencies
  - Better accuracy than Tesseract
  - Handles handwriting
  - No deployment size impact
- **Cons:** Requires Azure Cognitive Services account

**Option B: Tesseract OCR (Current - Keep)**
- **Package:** pytesseract (already installed)
- **Size:** ~10 MB
- **Pros:** 
  - Free, unlimited
  - Already working
  - No external dependencies
- **Cons:** 
  - Lower accuracy
  - Requires Tesseract binary on server

**Recommendation:** Keep Tesseract for now, upgrade to Azure CV later if needed.

### 2. Text Embeddings & Vector Search

**Option A: OpenAI Embeddings API (Recommended)**
- **Service:** OpenAI API (text-embedding-3-small)
- **Cost:** $0.02 per 1M tokens (~very cheap)
- **Size:** openai package ~5 MB
- **Pros:**
  - High quality embeddings
  - No local model needed
  - Minimal deployment size
- **Implementation:**
  ```python
  from openai import OpenAI
  client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
  
  response = client.embeddings.create(
      model="text-embedding-3-small",
      input="Your text here"
  )
  embedding = response.data[0].embedding
  ```

**Option B: Groq API (Free Alternative)**
- **Service:** Groq Cloud API
- **Free Tier:** Generous limits
- **Size:** groq package ~3 MB
- **Pros:**
  - Free tier available
  - Very fast inference
  - Good for text generation

**Option C: Lightweight Local (scikit-learn TF-IDF)**
- **Package:** scikit-learn
- **Size:** ~40 MB
- **Pros:**
  - No API costs
  - Works offline
  - Fast for small datasets
- **Cons:**
  - Lower quality than transformer embeddings
  - Not semantic search

**Recommendation:** Use OpenAI Embeddings API for production, TF-IDF for development.

### 3. Vector Storage

**Option A: Azure Cosmos DB (Current - Keep)**
- Store embeddings as arrays in Cosmos DB documents
- Use Python/NumPy for similarity search
- **Pros:** Already using Cosmos DB
- **Cons:** Not optimized for vector search

**Option B: Azure AI Search (Recommended for Scale)**
- **Service:** Azure Cognitive Search with vector search
- **Free Tier:** 50 MB storage, 3 indexes
- **Pros:**
  - Built-in vector search
  - Hybrid search (keyword + semantic)
  - Scalable
- **Cons:** Limited free tier

**Option C: In-Memory Vector Search (Current Approach)**
- Store vectors in Cosmos DB
- Load into memory and use NumPy/SciPy for search
- **Pros:** Simple, no extra services
- **Cons:** Limited by function memory

**Recommendation:** Keep current in-memory approach, migrate to Azure AI Search later.

### 4. Question Parsing & Generation

**Option A: Groq API (Recommended - Free)**
- **Service:** Groq Cloud API
- **Models:** llama-3.1-70b, mixtral-8x7b
- **Free Tier:** Very generous
- **Pros:**
  - Fast inference
  - Free tier
  - Good quality
- **Implementation:**
  ```python
  from groq import Groq
  client = Groq(api_key=os.getenv('GROQ_API_KEY'))
  
  response = client.chat.completions.create(
      model="llama-3.1-70b-versatile",
      messages=[{"role": "user", "content": "Parse this question..."}]
  )
  ```

**Option B: OpenAI API**
- **Service:** OpenAI GPT-4 or GPT-3.5
- **Cost:** $0.50-$10 per 1M tokens
- **Pros:** Best quality
- **Cons:** Costs money

**Recommendation:** Use Groq API (free) for question parsing and generation.

## Final Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Azure Function App (Python)                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Core Dependencies (~100 MB)                           │ │
│  │  - Flask, Azure SDK, Cosmos DB client                  │ │
│  │  - PyMuPDF, pytesseract, Pillow (PDF/OCR)            │ │
│  │  - NumPy, SciPy (vector operations)                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Lightweight AI (~50 MB)                               │ │
│  │  - openai (5 MB) - for embeddings                     │ │
│  │  - groq (3 MB) - for text generation                  │ │
│  │  - scikit-learn (40 MB) - fallback TF-IDF            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  External AI Services               │
        ├─────────────────────────────────────┤
        │  • Groq API (Free)                  │
        │    - Question parsing               │
        │    - Solution generation            │
        │    - Text analysis                  │
        │                                     │
        │  • OpenAI API (Paid)                │
        │    - Text embeddings                │
        │    - Semantic search                │
        │                                     │
        │  • Azure Computer Vision (Optional) │
        │    - Advanced OCR                   │
        │    - Handwriting recognition        │
        └─────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  Azure Cosmos DB                    │
        │  - Store embeddings as arrays       │
        │  - Store parsed questions           │
        │  - Store textbook content           │
        └─────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Update Dependencies (Now)
1. Replace `requirements-ai.txt` with `requirements-ai-lite.txt`
2. Add API keys to Azure Function App settings:
   - `GROQ_API_KEY`
   - `OPENAI_API_KEY` (optional)

### Phase 2: Update AI Code (Next)
1. Replace sentence-transformers with OpenAI embeddings
2. Replace local LLM with Groq API
3. Keep FAISS logic but use NumPy/SciPy instead

### Phase 3: Test & Deploy
1. Test locally with new dependencies
2. Deploy to Azure Functions
3. Verify deployment size < 500 MB

## Cost Estimate (Monthly)

| Service | Free Tier | Expected Usage | Cost |
|---------|-----------|----------------|------|
| Groq API | Very generous | 10K requests | $0 |
| OpenAI Embeddings | N/A | 1M tokens | $0.02 |
| Azure Functions | 1M executions | 50K executions | $0 |
| Azure Cosmos DB | 400 RU/s free | Within limits | $0 |
| **Total** | | | **~$0.02/month** |

## Next Steps

1. **Get API Keys:**
   - Groq: https://console.groq.com/
   - OpenAI: https://platform.openai.com/

2. **Update requirements.txt:**
   ```bash
   pip install -r requirements-ai-lite.txt
   ```

3. **Update AI code** to use APIs instead of local models

4. **Test locally** before deploying

5. **Deploy to Azure** with new dependencies
