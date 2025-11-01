"""
AI Service - Flask Application
Direct Flask app for AI-powered question solving and text generation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
import os

# Import AI helpers and services
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

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
logging.basicConfig(level=logging.INFO)

# ============================================================================
# ROOT & HEALTH CHECK
# ============================================================================

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'service': 'Qadam AI Service',
        'status': 'running',
        'version': '1.0',
        'endpoints': {
            'health': '/api/health',
            'solve_question': '/api/solve-question',
            'generate_text': '/api/generate-text',
            'semantic_search': '/api/semantic-search',
            'parse_questions': '/api/parse-questions',
            'map_to_chapters': '/api/map-to-chapters'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logging.info('Health check request received')
    
    try:
        status = check_ai_availability()
        
        return jsonify({
            'status': 'healthy',
            'service': 'AI Service (Flask on VM)',
            'features': status,
            'message': get_ai_status_message()
        })
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# ============================================================================
# QUESTION SOLVING
# ============================================================================

@app.route('/api/solve-question', methods=['POST'])
def solve_question():
    """
    Solve a question using AI
    
    Body: {
        "question_text": "Your question here",
        "subject": "Physics" (optional),
        "context": "Additional context" (optional)
    }
    """
    logging.info('Solve question request received')
    
    try:
        data = request.get_json()
        
        if not data or 'question_text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: question_text'
            }), 400
        
        question_text = data['question_text']
        subject = data.get('subject', '')
        context = data.get('context', '')
        
        # Generate solution
        solution = generate_solution(
            question_text=question_text,
            subject=subject,
            context=context
        )
        
        return jsonify({
            'success': True,
            'solution': solution
        })
    
    except Exception as e:
        logging.error(f"Error solving question: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# TEXT GENERATION
# ============================================================================

@app.route('/api/generate-text', methods=['POST'])
def generate_text():
    """
    Generate text using Groq API
    
    Body: {
        "prompt": "Your prompt",
        "model": "llama-3.3-70b-versatile" (optional),
        "max_tokens": 1000 (optional),
        "temperature": 0.7 (optional)
    }
    """
    logging.info('Generate text request received')
    
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: prompt'
            }), 400
        
        prompt = data['prompt']
        model = data.get('model', 'llama-3.3-70b-versatile')
        max_tokens = data.get('max_tokens', 1000)
        temperature = data.get('temperature', 0.7)
        
        # Generate text
        result = generate_with_groq(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return jsonify({
            'success': True,
            'text': result
        })
    
    except Exception as e:
        logging.error(f"Error generating text: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# SEMANTIC SEARCH
# ============================================================================

@app.route('/api/semantic-search', methods=['POST'])
def semantic_search():
    """
    Perform semantic search on documents
    
    Body: {
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
        data = request.get_json()
        
        if not data or 'query' not in data or 'documents' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: query, documents'
            }), 400
        
        query = data['query']
        documents = data['documents']
        top_k = data.get('top_k', 5)
        
        # Perform search
        results = search_similar_texts(
            query=query,
            documents=documents,
            top_k=top_k
        )
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        logging.error(f"Error in semantic search: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# QUESTION PARSING
# ============================================================================

@app.route('/api/parse-questions', methods=['POST'])
def parse_questions():
    """
    Parse questions from text
    
    Body: {
        "text": "Text containing questions"
    }
    """
    logging.info('Parse questions request received')
    
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: text'
            }), 400
        
        text = data['text']
        
        # Parse questions
        questions = parse_questions_from_text(text)
        
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions)
        })
    
    except Exception as e:
        logging.error(f"Error parsing questions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# CHAPTER MAPPING
# ============================================================================

@app.route('/api/map-to-chapters', methods=['POST'])
def map_to_chapters():
    """
    Map question to relevant chapters
    
    Body: {
        "question_text": "Question to map",
        "chapters": [
            {"name": "Chapter 1", "text": "Chapter content"},
            ...
        ]
    }
    """
    logging.info('Map to chapters request received')
    
    try:
        data = request.get_json()
        
        if not data or 'question_text' not in data or 'chapters' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: question_text, chapters'
            }), 400
        
        question_text = data['question_text']
        chapters = data['chapters']
        
        # Map to chapters
        result = map_question_to_chapters(
            question_text=question_text,
            chapters=chapters
        )
        
        return jsonify({
            'success': True,
            'mapping': result
        })
    
    except Exception as e:
        logging.error(f"Error mapping to chapters: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=False)
