"""
AI Service Azure Function App
Provides AI-powered endpoints for question solving, text generation, and semantic search
"""

import azure.functions as func
import logging
import json
import os
from ai_helpers import (
    generate_with_groq,
    generate_solution,
    search_similar_texts,
    parse_questions_from_text,
    map_question_to_chapters,
    check_ai_availability,
    get_ai_status_message
)
from ai_service import (
    TextbookIndex,
    generate_question_solution,
    analyze_question_paper,
    semantic_search_textbook
)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    logging.info('Health check request received')
    
    try:
        status = check_ai_availability()
        
        return func.HttpResponse(
            json.dumps({
                'status': 'healthy',
                'service': 'AI Service',
                'features': status,
                'message': get_ai_status_message()
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Health check error: {str(e)}")
        return func.HttpResponse(
            json.dumps({'status': 'unhealthy', 'error': str(e)}),
            mimetype="application/json",
            status_code=500
        )

# ============================================================================
# SOLUTION GENERATION
# ============================================================================

@app.route(route="solve-question", methods=["POST"])
def solve_question(req: func.HttpRequest) -> func.HttpResponse:
    """
    Solve a question using Groq AI
    
    Request body:
    {
        "question_text": "Question to solve",
        "subject": "Physics" (optional),
        "context": "Additional context" (optional)
    }
    """
    logging.info('Solve question request received')
    
    try:
        req_body = req.get_json()
        question_text = req_body.get('question_text')
        subject = req_body.get('subject', '')
        context = req_body.get('context', '')
        
        if not question_text:
            return func.HttpResponse(
                json.dumps({'error': 'question_text is required'}),
                mimetype="application/json",
                status_code=400
            )
        
        logging.info(f"Solving question: {question_text[:60]}...")
        
        # Generate solution
        solution = generate_solution(
            question_text=question_text,
            context=context,
            subject=subject
        )
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'solution': solution,
                'question_text': question_text,
                'subject': subject
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except ValueError as e:
        logging.error(f"Invalid request: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': 'Invalid JSON in request body'}),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error solving question: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            mimetype="application/json",
            status_code=500
        )

# ============================================================================
# TEXT GENERATION
# ============================================================================

@app.route(route="generate-text", methods=["POST"])
def generate_text(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate text using Groq API
    
    Request body:
    {
        "prompt": "Your prompt here",
        "model": "llama-3.3-70b-versatile" (optional),
        "max_tokens": 1000 (optional),
        "temperature": 0.7 (optional)
    }
    """
    logging.info('Generate text request received')
    
    try:
        req_body = req.get_json()
        prompt = req_body.get('prompt')
        model = req_body.get('model', 'llama-3.3-70b-versatile')
        max_tokens = req_body.get('max_tokens', 1000)
        temperature = req_body.get('temperature', 0.7)
        
        if not prompt:
            return func.HttpResponse(
                json.dumps({'error': 'prompt is required'}),
                mimetype="application/json",
                status_code=400
            )
        
        logging.info(f"Generating text with model: {model}")
        
        # Generate text
        generated_text = generate_with_groq(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'generated_text': generated_text,
                'model': model
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except ValueError as e:
        logging.error(f"Invalid request: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': 'Invalid JSON in request body'}),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error generating text: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            mimetype="application/json",
            status_code=500
        )

# ============================================================================
# SEMANTIC SEARCH
# ============================================================================

@app.route(route="semantic-search", methods=["POST"])
def semantic_search(req: func.HttpRequest) -> func.HttpResponse:
    """
    Perform semantic search on documents
    
    Request body:
    {
        "query": "Search query",
        "documents": [
            {"id": "1", "text": "Document text"},
            ...
        ],
        "top_k": 5 (optional)
    }
    """
    logging.info('Semantic search request received')
    
    try:
        req_body = req.get_json()
        query = req_body.get('query')
        documents = req_body.get('documents', [])
        top_k = req_body.get('top_k', 5)
        
        if not query:
            return func.HttpResponse(
                json.dumps({'error': 'query is required'}),
                mimetype="application/json",
                status_code=400
            )
        
        if not documents:
            return func.HttpResponse(
                json.dumps({'error': 'documents list is required'}),
                mimetype="application/json",
                status_code=400
            )
        
        logging.info(f"Searching {len(documents)} documents for: {query[:60]}...")
        
        # Extract texts and IDs
        doc_texts = [doc.get('text', '') for doc in documents]
        doc_ids = [doc.get('id', str(i)) for i, doc in enumerate(documents)]
        
        # Perform search
        results = search_similar_texts(
            query_text=query,
            document_texts=doc_texts,
            document_ids=doc_ids,
            top_k=top_k
        )
        
        # Format results
        formatted_results = [
            {
                'document_id': doc_id,
                'similarity_score': score,
                'text': text[:200]  # Truncate for response
            }
            for doc_id, score, text in results
        ]
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'query': query,
                'results': formatted_results,
                'total_results': len(formatted_results)
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except ValueError as e:
        logging.error(f"Invalid request: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': 'Invalid JSON in request body'}),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error in semantic search: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            mimetype="application/json",
            status_code=500
        )

# ============================================================================
# QUESTION PARSING
# ============================================================================

@app.route(route="parse-questions", methods=["POST"])
def parse_questions(req: func.HttpRequest) -> func.HttpResponse:
    """
    Parse questions from text using Groq AI
    
    Request body:
    {
        "text": "Text containing questions"
    }
    """
    logging.info('Parse questions request received')
    
    try:
        req_body = req.get_json()
        text = req_body.get('text')
        
        if not text:
            return func.HttpResponse(
                json.dumps({'error': 'text is required'}),
                mimetype="application/json",
                status_code=400
            )
        
        logging.info(f"Parsing questions from {len(text)} characters of text...")
        
        # Parse questions
        questions = parse_questions_from_text(text)
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'questions': questions,
                'total_questions': len(questions)
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except ValueError as e:
        logging.error(f"Invalid request: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': 'Invalid JSON in request body'}),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error parsing questions: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            mimetype="application/json",
            status_code=500
        )

# ============================================================================
# CHAPTER MAPPING
# ============================================================================

@app.route(route="map-to-chapters", methods=["POST"])
def map_to_chapters(req: func.HttpRequest) -> func.HttpResponse:
    """
    Map a question to relevant textbook chapters
    
    Request body:
    {
        "question_text": "Question to map",
        "chapters": [
            {"name": "Chapter 1", "text": "Chapter content"},
            ...
        ]
    }
    """
    logging.info('Map to chapters request received')
    
    try:
        req_body = req.get_json()
        question_text = req_body.get('question_text')
        chapters = req_body.get('chapters', [])
        
        if not question_text:
            return func.HttpResponse(
                json.dumps({'error': 'question_text is required'}),
                mimetype="application/json",
                status_code=400
            )
        
        if not chapters:
            return func.HttpResponse(
                json.dumps({'error': 'chapters list is required'}),
                mimetype="application/json",
                status_code=400
            )
        
        logging.info(f"Mapping question to {len(chapters)} chapters...")
        
        # Extract chapter data
        chapter_names = [ch.get('name', f'Chapter {i+1}') for i, ch in enumerate(chapters)]
        chapter_texts = [ch.get('text', '') for ch in chapters]
        
        # Map question to chapters
        results = map_question_to_chapters(
            question_text=question_text,
            chapter_texts=chapter_texts,
            chapter_names=chapter_names
        )
        
        # Format results
        formatted_results = [
            {
                'chapter_name': name,
                'similarity_score': score
            }
            for name, score in results
        ]
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'question_text': question_text,
                'matched_chapters': formatted_results
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except ValueError as e:
        logging.error(f"Invalid request: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': 'Invalid JSON in request body'}),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error mapping to chapters: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            mimetype="application/json",
            status_code=500
        )

# ============================================================================
# STARTUP MESSAGE
# ============================================================================

logging.info("="*60)
logging.info("AI Service Azure Function App Started")
logging.info(get_ai_status_message())
logging.info("="*60)
