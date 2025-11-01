# AI Service - Azure Function App

AI-powered service for question solving, text generation, and semantic search using Groq API.

## Features

- **Question Solving**: Generate step-by-step solutions for academic questions
- **Text Generation**: Use Groq's Llama models for text generation
- **Semantic Search**: TF-IDF based similarity search for documents
- **Question Parsing**: Extract and parse questions from text
- **Chapter Mapping**: Map questions to relevant textbook chapters

## Endpoints

### Health Check
```
GET /api/health
```

### Solve Question
```
POST /api/solve-question
Body: {
  "question_text": "Your question here",
  "subject": "Physics" (optional),
  "context": "Additional context" (optional)
}
```

### Generate Text
```
POST /api/generate-text
Body: {
  "prompt": "Your prompt",
  "model": "llama-3.3-70b-versatile" (optional),
  "max_tokens": 1000 (optional),
  "temperature": 0.7 (optional)
}
```

### Semantic Search
```
POST /api/semantic-search
Body: {
  "query": "Search query",
  "documents": [
    {"id": "1", "text": "Document text"},
    ...
  ],
  "top_k": 5 (optional)
}
```

### Parse Questions
```
POST /api/parse-questions
Body: {
  "text": "Text containing questions"
}
```

### Map to Chapters
```
POST /api/map-to-chapters
Body: {
  "question_text": "Question to map",
  "chapters": [
    {"name": "Chapter 1", "text": "Chapter content"},
    ...
  ]
}
```

## Environment Variables

- `GROQ_API_KEY`: Your Groq API key (required)

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variable:
```bash
export GROQ_API_KEY=your_groq_api_key
```

3. Run locally:
```bash
func start
```

## Deployment

This function app is automatically deployed to Azure when changes are pushed to the `backend-ai` branch.

**Function App Name**: `qadam-ai`
**URL**: `https://qadam-ai.azurewebsites.net`

## Technology Stack

- **Azure Functions**: Serverless compute
- **Groq API**: LLM inference (Llama 3.3)
- **scikit-learn**: TF-IDF vectorization and similarity search
- **PyMuPDF**: PDF text extraction

## Architecture

```
ai/
├── function_app.py      # Main Azure Function endpoints
├── ai_helpers.py        # Groq API wrapper and utilities
├── ai_service.py        # AI service logic (TextbookIndex, etc.)
├── requirements.txt     # Python dependencies
├── host.json           # Azure Functions configuration
└── .funcignore         # Files to exclude from deployment
```

## Free Tier Compatible

This service is designed to run within Azure's free tier limits:
- Uses lightweight TF-IDF for embeddings (no heavy ML models)
- Groq API provides free tier access
- Minimal memory footprint
- Fast cold start times
