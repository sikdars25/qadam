# Migration Guide: Old AI → New Lightweight AI

## ✅ What's Changed

### Old Stack (Heavy - 1.5+ GB)
- ❌ FAISS for vector storage
- ❌ sentence-transformers for embeddings
- ❌ PyTorch (800 MB)
- ❌ Local LLM models

### New Stack (Lightweight - 150 MB)
- ✅ scikit-learn TF-IDF for embeddings
- ✅ NumPy/SciPy for vector operations
- ✅ Groq API for text generation
- ✅ In-memory vector search

## 📝 Code Changes Required

### 1. Import Statement (DONE ✅)

**File:** `app.py` (lines 63-83)

```python
# OLD:
from ai_service import (
    analyze_question_paper,
    generate_solution,
    extract_chapters_from_textbook,
    semantic_search_textbook
)

# NEW:
from ai_service_new import (
    analyze_question_paper,
    generate_question_solution as generate_solution,
    index_textbook as extract_chapters_from_textbook,
    semantic_search_textbook,
    TextbookIndex,
    get_service_status
)
```

### 2. Textbook Indexing

**File:** `app.py` (around line 1928)

**OLD Code:**
```python
from ai_service import extract_chapters_from_textbook
result = extract_chapters_from_textbook(file_path, textbook_id)
```

**NEW Code:**
```python
from ai_service_new import index_textbook
index = index_textbook(file_path, textbook_id, chapter_detection='auto')

# Save the index
index_dir = f"vector_indices/{textbook_id}"
os.makedirs(index_dir, exist_ok=True)
index.save(f"{index_dir}/index.pkl")

result = {
    'success': True,
    'chapters': len(index.chapters),
    'textbook_id': textbook_id
}
```

### 3. Loading Textbook Chapters

**File:** `app.py` (around line 1842)

**OLD Code:**
```python
from ai_service import load_textbook_chapters
chapters = load_textbook_chapters(textbook_id)
```

**NEW Code:**
```python
from ai_service_new import TextbookIndex

# Try to load index
index_path = f"vector_indices/{textbook_id}/index.pkl"
if os.path.exists(index_path):
    index = TextbookIndex.load(index_path)
    chapters = [
        {
            'name': ch['name'],
            'preview': ch['text'][:200]  # First 200 chars
        }
        for ch in index.chapters
    ]
else:
    chapters = []
```

### 4. Generating Solutions

**File:** `app.py` (solution generation endpoint)

**OLD Code:**
```python
solution = generate_solution(question_text, textbook_id=textbook_id)
```

**NEW Code:**
```python
from ai_service_new import generate_question_solution, TextbookIndex

# Load textbook index if available
textbook_index = None
if textbook_id:
    index_path = f"vector_indices/{textbook_id}/index.pkl"
    if os.path.exists(index_path):
        textbook_index = TextbookIndex.load(index_path)

# Generate solution
solution = generate_question_solution(
    question_text,
    textbook_index=textbook_index,
    subject=subject
)
```

### 5. Semantic Search

**OLD Code:**
```python
from ai_service import semantic_search_textbook
results = semantic_search_textbook(query, textbook_id, top_k=5)
```

**NEW Code:**
```python
from ai_service_new import TextbookIndex

# Load index
index_path = f"vector_indices/{textbook_id}/index.pkl"
if os.path.exists(index_path):
    index = TextbookIndex.load(index_path)
    results = index.search(query, top_k=5)
else:
    results = []
```

### 6. Question Parsing

**OLD Code:**
```python
from ai_service import analyze_question_paper
result = analyze_question_paper(pdf_path, textbook_id)
```

**NEW Code:**
```python
from ai_service_new import analyze_question_paper, TextbookIndex

# Load textbook index if available
textbook_index = None
if textbook_id:
    index_path = f"vector_indices/{textbook_id}/index.pkl"
    if os.path.exists(index_path):
        textbook_index = TextbookIndex.load(index_path)

# Analyze paper
result = analyze_question_paper(pdf_path, textbook_index=textbook_index)
```

## 🔧 Function Mapping

| Old Function | New Function | Notes |
|--------------|--------------|-------|
| `extract_chapters_from_textbook()` | `index_textbook()` | Returns `TextbookIndex` object |
| `load_textbook_chapters()` | `TextbookIndex.load()` | Load from pickle file |
| `generate_solution()` | `generate_question_solution()` | Uses Groq API |
| `semantic_search_textbook()` | `TextbookIndex.search()` | Uses TF-IDF |
| `analyze_question_paper()` | `analyze_question_paper()` | Same name, different implementation |
| `get_embedding_model()` | N/A | Not needed (uses TF-IDF) |

## 📦 Storage Changes

### Old Storage (FAISS)
```
vector_indices/
  {textbook_id}/
    index.faiss
    metadata.json
```

### New Storage (Pickle)
```
vector_indices/
  {textbook_id}/
    index.pkl  # Contains: chapters, embeddings, vectorizer
```

## 🚀 Deployment Steps

### Step 1: Test Locally

```bash
cd backend

# Install new dependencies
pip install -r requirements.txt

# Test AI features
python test_ai.py

# Test with your app
python app.py
```

### Step 2: Update Code

Use this migration guide to update all endpoints in `app.py` that use AI features.

### Step 3: Set Environment Variables

Add to `.env`:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

Add to Azure Function App settings:
- Go to Azure Portal → Function App → Configuration
- Add: `GROQ_API_KEY` = your key

### Step 4: Deploy

```bash
git add .
git commit -m "Migrate to lightweight AI stack"
git push origin main
```

## ⚠️ Breaking Changes

1. **Index Format:** Old FAISS indices won't work. You'll need to re-index textbooks.
2. **API Changes:** Some function signatures changed (see mapping table above).
3. **Dependencies:** Remove old AI dependencies from any custom scripts.

## ✅ Benefits

1. **Deployment Size:** 1.5+ GB → 150 MB (10x smaller!)
2. **Azure Compatible:** Fits within free tier limits
3. **Faster Deployment:** Smaller package = faster uploads
4. **Cost:** Free (Groq API has generous free tier)
5. **Maintenance:** Fewer dependencies to manage

## 🔄 Rollback Plan

If you need to rollback:

1. Revert to old `ai_service.py`
2. Install old dependencies: `pip install -r requirements-ai.txt`
3. Restore FAISS indices from backup

## 📞 Support

If you encounter issues:

1. Check `test_ai.py` output for errors
2. Verify `GROQ_API_KEY` is set
3. Check Azure Function App logs
4. Ensure all dependencies are installed

## 🎯 Next Steps

1. ✅ Review this migration guide
2. ⏳ Update `app.py` endpoints (see sections 2-6 above)
3. ⏳ Test locally
4. ⏳ Deploy to Azure
5. ⏳ Re-index textbooks (old indices won't work)
