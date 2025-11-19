# AI Question Solver Integration Guide

## Overview

This guide explains how the Proxy service integrates with the AI Question Solver to provide intelligent question solving with dependency management.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER REQUEST                              │
│                  (Image with question)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROXY SERVICE                                 │
│                  (backend-proxy branch)                          │
│                                                                  │
│  1. Receives image from user                                    │
│  2. Calls OCR service to extract text                           │
│  3. Receives OCR text                                           │
│  4. Calls AI service to solve question                          │
│  5. Returns solution to user                                    │
└─────────────────────────────────────────────────────────────────┘
          │                                          │
          │ (2) Extract text                         │ (4) Solve question
          ▼                                          ▼
┌──────────────────────────┐          ┌──────────────────────────┐
│     OCR SERVICE          │          │     AI SERVICE           │
│  (backend-ocr branch)    │          │  (backend-ai branch)     │
│                          │          │                          │
│  • LaTeX-OCR             │          │  • Groq extraction       │
│  • EasyOCR               │          │  • Dependency graph      │
│  • Image preprocessing   │          │  • Wolfram solving       │
│  • LaTeX post-processing │          │  • Groq synthesis        │
│  • MCQ formatting        │          │                          │
└──────────────────────────┘          └──────────────────────────┘
          │                                          │
          │ (3) Return OCR text                      │ (5) Return solution
          ▼                                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROXY SERVICE                                 │
│              Combines OCR + AI results                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        USER RESPONSE                             │
│  • Original question text (from OCR)                            │
│  • Extracted expressions (from AI)                              │
│  • Step-by-step solution (from AI)                              │
│  • Final answer (from AI)                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Branch Organization

### backend-ocr (OCR Service)
**Purpose:** Text extraction from images

**Responsibilities:**
- Extract text using LaTeX-OCR and EasyOCR
- Preprocess images for better OCR
- Post-process LaTeX output
- Format MCQ options

**Does NOT:**
- Solve mathematical problems
- Use Groq or Wolfram APIs
- Generate explanations

### backend-ai (AI Service)
**Purpose:** Intelligent question solving

**Responsibilities:**
- Extract mathematical expressions using Groq AI
- Identify dependencies between expressions
- Solve expressions using Wolfram Alpha
- Synthesize comprehensive answers using Groq AI

**Does NOT:**
- Handle image processing
- Perform OCR
- Interact with users directly

### backend-proxy (Proxy Service)
**Purpose:** Orchestration and integration

**Responsibilities:**
- Receive user requests
- Call OCR service to extract text
- Call AI service to solve questions
- Combine and return results
- Handle authentication and user management

**Integration Module:** `ai_question_solver_client.py`

## Integration Modes

The Proxy service can integrate with the AI service in two modes:

### 1. Direct Import (Development)
```python
from ai.intelligent_question_solver import IntelligentQuestionSolver

solver = IntelligentQuestionSolver()
result = solver.solve_question(question_text, subject)
```

**Advantages:**
- Fast (no HTTP overhead)
- Easy debugging
- Good for development

**Requirements:**
- AI module must be in same codebase
- All AI dependencies installed

### 2. HTTP API (Production)
```python
import requests

response = requests.post(
    'http://ai-service:8001/api/solve-question',
    json={'question_text': text, 'subject': subject}
)
result = response.json()
```

**Advantages:**
- Services can be deployed separately
- Better scalability
- Independent scaling of AI service

**Requirements:**
- AI service must be running
- Network connectivity

## Using the AI Client

### Basic Usage

```python
from ai_question_solver_client import AIQuestionSolverClient

# Initialize client (auto-detects best mode)
client = AIQuestionSolverClient(mode='auto')

# Solve a question
result = client.solve_question(
    question_text="Find x where 2x + 5 = 15",
    subject="Algebra"
)

if result['success']:
    print(result['final_answer'])
```

### Integration in Proxy Endpoint

```python
from flask import Flask, request, jsonify
from ocr_client import ocr_image  # Existing OCR client
from ai_question_solver_client import solve_question_with_ai

app = Flask(__name__)

@app.route('/api/solve-question-from-image', methods=['POST'])
def solve_question_from_image():
    """
    Complete workflow: Image → OCR → AI Solving → Response
    """
    # Step 1: Get image from request
    image_file = request.files.get('image')
    subject = request.form.get('subject', '')
    
    # Step 2: Extract text using OCR service
    ocr_result = ocr_image(image_file)
    
    if not ocr_result.get('success'):
        return jsonify({
            'success': False,
            'error': 'OCR extraction failed',
            'details': ocr_result.get('error')
        }), 400
    
    question_text = ocr_result.get('text', '')
    
    # Step 3: Solve question using AI service
    ai_result = solve_question_with_ai(question_text, subject)
    
    if not ai_result.get('success'):
        return jsonify({
            'success': False,
            'error': 'AI solving failed',
            'details': ai_result.get('error'),
            'ocr_text': question_text  # Still return OCR text
        }), 500
    
    # Step 4: Return complete result
    return jsonify({
        'success': True,
        'ocr_text': question_text,
        'extracted_expressions': ai_result.get('extracted_expressions', []),
        'dependency_graph': ai_result.get('dependency_graph', {}),
        'solving_order': ai_result.get('solving_order', []),
        'solved_expressions': ai_result.get('solved_expressions', []),
        'final_answer': ai_result.get('final_answer', ''),
        'processing_time': {
            'ocr_seconds': ocr_result.get('processing_time', 0),
            'ai_seconds': ai_result.get('processing_time_seconds', 0),
            'total_seconds': (
                ocr_result.get('processing_time', 0) + 
                ai_result.get('processing_time_seconds', 0)
            )
        },
        'metadata': ai_result.get('metadata', {})
    })
```

## Configuration

### Environment Variables

Add to Proxy service `.env` file:

```env
# AI Service Configuration
AI_SERVICE_URL=http://localhost:8001

# For production deployment
# AI_SERVICE_URL=http://ai-service.internal:8001

# OCR Service Configuration (existing)
OCR_SERVICE_URL=http://localhost:8000
```

### Development Setup

1. **Install AI module dependencies:**
   ```bash
   cd ai
   pip install -r requirements.txt
   ```

2. **Configure API keys in root `.env`:**
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   WOLFRAM_APP_ID=your_wolfram_app_id_here
   ```

3. **Test AI client:**
   ```bash
   cd proxy
   python ai_question_solver_client.py
   ```

### Production Setup

1. **Deploy AI service separately:**
   ```bash
   # On AI service server
   cd ai
   pip install -r requirements.txt
   python -m flask run --host=0.0.0.0 --port=8001
   ```

2. **Configure Proxy to use AI service URL:**
   ```env
   AI_SERVICE_URL=http://ai-service-host:8001
   ```

3. **Deploy Proxy service:**
   ```bash
   # On Proxy service server
   cd proxy
   pip install -r requirements.txt
   python app.py
   ```

## Workflow Example

### User Request Flow

```
1. User uploads image with question:
   "Find x where 2x + 5 = 15, then calculate y = 3x - 2"

2. Proxy receives image
   → Calls OCR service

3. OCR service processes image
   → Returns text: "Find x where 2x + 5 = 15, then calculate y = 3x - 2"

4. Proxy receives OCR text
   → Calls AI service with text

5. AI service processes question:
   
   5a. Groq extracts expressions:
       - expr_1: "2x + 5 = 15" (independent)
       - expr_2: "y = 3x - 2" (depends on expr_1)
   
   5b. Determines solving order:
       expr_1 → expr_2
   
   5c. Wolfram solves expressions:
       - expr_1: x = 5
       - expr_2: y = 13 (using x = 5)
   
   5d. Groq synthesizes answer:
       "## Understanding the Question
        We need to find x first, then use it to calculate y.
        
        ## Step-by-Step Solution
        ### Step 1: Solve for x
        Expression: 2x + 5 = 15
        Solution: x = 5
        
        ### Step 2: Calculate y
        Expression: y = 3x - 2
        Substituting x = 5: y = 13
        
        ## Final Answer: y = 13"

6. Proxy receives AI result
   → Combines with OCR text
   → Returns to user

7. User receives:
   - Original question text
   - Extracted expressions
   - Dependency graph
   - Step-by-step solution
   - Final answer
```

## Error Handling

### OCR Service Unavailable
```python
if not ocr_result.get('success'):
    return {
        'success': False,
        'error': 'OCR service unavailable',
        'stage': 'ocr'
    }
```

### AI Service Unavailable
```python
if not ai_result.get('success'):
    return {
        'success': False,
        'error': 'AI service unavailable',
        'stage': 'ai',
        'ocr_text': question_text  # Still return OCR text
    }
```

### Graceful Degradation
```python
# If AI service fails, return OCR text only
if not ai_result.get('success'):
    return {
        'success': True,
        'ocr_text': question_text,
        'ai_available': False,
        'message': 'OCR successful, AI solving unavailable'
    }
```

## Testing

### Test AI Client Directly
```bash
cd proxy
python ai_question_solver_client.py
```

### Test Complete Workflow
```bash
# 1. Start OCR service
cd ocr
python app.py  # Runs on port 8000

# 2. Start AI service (if using API mode)
cd ai
python -m flask run --port=8001

# 3. Start Proxy service
cd proxy
python app.py  # Runs on port 5000

# 4. Test with curl
curl -X POST http://localhost:5000/api/solve-question-from-image \
  -F "image=@test_question.jpg" \
  -F "subject=Algebra"
```

## Performance Considerations

### Typical Processing Times

**OCR Service:**
- Image preprocessing: ~0.5-1s
- Text extraction: ~2-3s
- Post-processing: ~0.1-0.2s
- **Total: ~3-5s**

**AI Service:**
- Expression extraction (Groq): ~2-3s
- Solving per expression (Wolfram): ~1-2s
- Answer synthesis (Groq): ~3-5s
- **Total: ~6-15s**

**Complete Workflow:**
- **Total: ~9-20s** (OCR + AI)

### Optimization Strategies

1. **Parallel Processing:**
   - OCR and AI can't run in parallel (AI needs OCR output)
   - But multiple independent expressions can be solved in parallel

2. **Caching:**
   - Cache common expressions and their solutions
   - Cache Groq extraction results for similar questions

3. **Async Processing:**
   - Return OCR text immediately
   - Process AI solving asynchronously
   - Use webhooks or polling for results

## Deployment Checklist

### Backend-OCR Service
- [ ] Deploy OCR service
- [ ] Configure environment variables
- [ ] Test text extraction
- [ ] Verify MCQ formatting

### Backend-AI Service
- [ ] Deploy AI service
- [ ] Configure Groq API key
- [ ] Configure Wolfram Alpha App ID
- [ ] Test expression extraction
- [ ] Test solving and synthesis

### Backend-Proxy Service
- [ ] Deploy Proxy service
- [ ] Configure OCR service URL
- [ ] Configure AI service URL
- [ ] Test complete workflow
- [ ] Set up monitoring and logging

## Monitoring

### Key Metrics to Track

**OCR Service:**
- Request count
- Processing time
- Success rate
- Error types

**AI Service:**
- Expression extraction success rate
- Wolfram Alpha API calls
- Groq API calls
- Processing time per stage

**Proxy Service:**
- End-to-end processing time
- Service availability (OCR, AI)
- User satisfaction metrics

## Troubleshooting

### AI Service Not Responding
1. Check AI service is running
2. Verify AI_SERVICE_URL is correct
3. Check network connectivity
4. Review AI service logs

### Expression Extraction Failing
1. Verify GROQ_API_KEY is configured
2. Check Groq API quota
3. Review question text format
4. Check Groq API logs

### Wolfram Alpha Errors
1. Verify WOLFRAM_APP_ID is configured
2. Check Wolfram Alpha quota
3. Review expression format
4. Try with simpler expressions

## Summary

The Proxy service acts as the orchestrator:
1. ✅ Receives user requests
2. ✅ Calls OCR service for text extraction
3. ✅ Calls AI service for intelligent solving
4. ✅ Combines results and returns to user

Each service has a clear responsibility:
- **OCR:** Text extraction only
- **AI:** Question solving only
- **Proxy:** Integration and orchestration

This separation allows independent development, testing, and scaling of each component.
