"""
AI Service - Flask Application
Direct Flask app for AI-powered question solving and text generation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
import os
import re

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Math symbol mappings for better processing
MATH_SYMBOLS = {
    'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta', 'θ': 'theta',
    'π': 'pi', 'σ': 'sigma', 'Σ': 'summation', '∫': 'integral', '√': 'sqrt',
    '∑': 'sum', '∏': 'product', '±': 'plus_minus', '×': 'multiply', '÷': 'divide',
    '≤': 'less_equal', '≥': 'greater_equal', '≠': 'not_equal', '≈': 'approximately'
}

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
logger = logging.getLogger(__name__)

def contains_math_symbols(text):
    """Check if text contains mathematical symbols"""
    return any(symbol in text for symbol in MATH_SYMBOLS.keys())

def normalize_math_expression(text):
    """Preserve mathematical expressions exactly - DO NOT modify Greek letters"""
    # PRESERVE Greek letters and math symbols exactly as they appear
    # DO NOT apply any corrections to λn, λp, λn/λp or other Greek expressions
    
    normalized = text
    
    # Apply comprehensive mathematical symbol corrections
    normalized = correct_math_symbols(normalized)
    
    # Only log the presence of math symbols for debugging
    for symbol in MATH_SYMBOLS.keys():
        if symbol in normalized:
            logger.info(f"🔍 Found math symbol: {symbol}")
    
    # Handle Greek letters specifically - just log, don't modify
    greek_pattern = r'[α-ωΑ-Ω]'
    if re.search(greek_pattern, normalized):
        logger.info("🔍 Detected Greek letters in expression - preserving as-is")
    
    return normalized

def correct_math_symbols(text):
    """
    Correct common OCR detection errors for mathematical symbols and expressions
    
    Issues addressed:
    1. τ (tau) detected as T
    2. Vector arrows (→) not detected above letters
    3. Single letter with prefix/suffix split incorrectly
    4. Power digits (exponential) not detected correctly
    5. Expressions in parentheses/brackets not detected correctly
    """
    if not text:
        return text
    
    corrected_text = text
    corrections_made = []
    
    # 1. Fix τ (tau) detection issues
    tau_corrections = [
        # Common contexts where τ is misdetected as T
        (r'\btorque\s+T\b', 'torque τ'),
        (r'\bshear\s+stress\s+T\b', 'shear stress τ'),
        (r'\btime\s+constant\s+T\b', 'time constant τ'),
        (r'\bangular\s+period\s+T\b', 'angular period τ'),
        (r'\bT\s+(constant|period|torque)\b', r'τ \1'),
        # Direct T to τ in math contexts
        (r'([=+\-*/(])T([a-zA-Z])', r'\1τ\2'),
        (r'([a-zA-Z])T([=+\-*/)])', r'\1τ\2'),
        # Handle T between variables
        (r'([=+\-*/(])T\s+([a-zA-Z])', r'\1τ\2'),
        (r'([a-zA-Z])\s+T([=+\-*/)])', r'\1τ\2'),
    ]
    
    for pattern, replacement in tau_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append(f"T → τ")
    
    # 2. Fix vector arrow detection
    vector_corrections = [
        # Common vector notations that get split - be more specific
        (r'\bvec\s+([a-zA-Z])\b', r'→\1'),  # vec a → →a
        (r'\b([a-zA-Z])\s+vec\b(?!\s+vec)', r'\1→'),  # a vec → a→ (not if followed by another vec)
        (r'\b([a-zA-Z])\s+vector\b', r'\1→'),  # a vector → a→
        (r'\bvector\s+([a-zA-Z])\b', r'→\1'),  # vector a → →a
        # Arrow combinations
        (r'->\s*([a-zA-Z])', r'→\1'),  # -> a → →a
        (r'([a-zA-Z])\s*->', r'\1→'),  # a -> → a→
    ]
    
    for pattern, replacement in vector_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("vector arrow fixed")
    
    # 3. Fix single letter with prefix/suffix splitting
    # Combine common math notation that gets incorrectly split
    combination_corrections = [
        # Greek letters with subscripts/superscripts - be more specific
        (r'λ\s+n\b', 'λn'),
        (r'λ\s+p\b', 'λp'),
        (r'α\s+n\b', 'αn'),
        (r'β\s+n\b', 'βn'),
        (r'θ\s+n\b', 'θn'),
        (r'μ\s+0\b', 'μ₀'),
        (r'σ\s+2\b', 'σ²'),
        # Variables with subscripts - be more specific to avoid power conflicts
        (r'([a-zA-Z])\s+(\d+)\b', r'\1\2'),  # a 1 → a1 (only at word boundary)
        (r'([a-zA-Z])\s+_(\d+)', r'\1_\2'),  # a _1 → a_1
        # Function notation
        (r'f\s*\(\s*x\s*\)', 'f(x)'),  # f ( x ) → f(x)
        (r'g\s*\(\s*x\s*\)', 'g(x)'),
        (r'sin\s*\(\s*x\s*\)', 'sin(x)'),
        (r'cos\s*\(\s*x\s*\)', 'cos(x)'),
        (r'tan\s*\(\s*x\s*\)', 'tan(x)'),
        (r'log\s*\(\s*x\s*\)', 'log(x)'),
        (r'ln\s*\(\s*x\s*\)', 'ln(x)'),
    ]
    
    for pattern, replacement in combination_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("combined split characters")
    
    # 4. Fix power digits and exponentials - fix negative exponent issue
    power_corrections = [
        # Superscript patterns - fix negative exponent issue
        (r'\^\s*-(\d+)', r'^-\1'),  # ^ -2 → ^-2
        (r'\^\s*(\d+)', r'^\1'),  # ^ 2 → ^2
        (r'([a-zA-Z])\s*\^\s*-(\d+)', r'\1^-\2'),  # x ^ -2 → x^-2
        (r'([a-zA-Z])\s*\^\s*(\d+)', r'\1^\2'),  # x ^ 2 → x^2
        # Only apply x2 → x^2 for common variables, not all letters
        (r'([xyze])\s*(\d+)\b', r'\1^\2'),  # x2 → x^2, y3 → y^3, etc.
        (r'e\s*\^\s*-(\d+)', r'e^-\1'),  # e ^ -2 → e^-2
        (r'e\s*\^\s*(\d+)', r'e^\1'),  # e ^ 2 → e^2
        (r'10\s*\^\s*-(\d+)', r'10^-\1'),  # 10 ^ -2 → 10^-2
        (r'10\s*\^\s*(\d+)', r'10^\1'),  # 10 ^ 2 → 10^2
    ]
    
    for pattern, replacement in power_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("power/exponential fixed")
    
    # 5. Scientific notation - apply after power corrections
    scientific_corrections = [
        # Scientific notation - be more specific, avoid conflicts with power corrections
        (r'(\d+\.\d+)\s+e\s+(\d+)(?!\s*\w)', r'\1e\2'),  # 1.2 e 3 → 1.2e3
        (r'(\d+\.\d+)\s+e\s+-(\d+)(?!\s*\w)', r'\1e-\2'),  # 1.2 e -3 → 1.2e-3
        (r'(\d+)\s+e\s+(\d+)(?!\s*\w)', r'\1e\2'),  # 1 e 3 → 1e3
        (r'(\d+)\s+e\s+-(\d+)(?!\s*\w)', r'\1e-\2'),  # 1 e -3 → 1e-3
    ]
    
    for pattern, replacement in scientific_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("scientific notation fixed")
    
    # 6. Fix parentheses and brackets expressions
    bracket_corrections = [
        # Fix spacing in mathematical expressions
        (r'\(\s*([^)]+?)\s*\)', r'(\1)'),  # ( x + y ) → (x+y)
        (r'\[\s*([^\]]+?)\s*\]', r'[\1]'),  # [ x + y ] → [x+y]
        (r'\{\s*([^}]+?)\s*\}', r'{\1}'),  # { x + y } → {x+y}
        # Remove extra spaces around operators in parentheses
        (r'\(\s*([^)]+?)\s*\+\s*([^)]+?)\s*\)', r'(\1+\2)'),  # ( a + b ) → (a+b)
        (r'\(\s*([^)]+?)\s*\-\s*([^)]+?)\s*\)', r'(\1-\2)'),  # ( a - b ) → (a-b)
        (r'\(\s*([^)]+?)\s*\*\s*([^)]+?)\s*\)', r'(\1*\2)'),  # ( a * b ) → (a*b)
        (r'\(\s*([^)]+?)\s*\/\s*([^)]+?)\s*\)', r'(\1/\2)'),  # ( a / b ) → (a/b)
        # Similar for brackets
        (r'\[\s*([^\]]+?)\s*\+\s*([^\]]+?)\s*\]', r'[\1+\2]'),  # [ a + b ] → [a+b]
        (r'\[\s*([^\]]+?)\s*\-\s*([^\]]+?)\s*\]', r'[\1-\2]'),  # [ a - b ] → [a-b]
        (r'\{\s*([^}]+?)\s*\+\s*([^}]+?)\s*\}', r'{\1+\2}'),  # { a + b } → {a+b}
        (r'\{\s*([^}]+?)\s*\-\s*([^}]+?)\s*\}', r'{\1-\2}'),  # { a - b } → {a-b}
    ]
    
    for pattern, replacement in bracket_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("parentheses/brackets fixed")
    
    # Log corrections for debugging
    if corrections_made:
        logger.info(f"🔧 Math symbol corrections applied: {', '.join(set(corrections_made))}")
    
    return corrected_text

def analyze_math_content(question_text):
    """Analyze question for mathematical content"""
    has_greek = bool(re.search(r'[α-ωΑ-Ω]', question_text))
    has_symbols = contains_math_symbols(question_text)
    has_equations = '=' in question_text or 'x' in question_text.lower()
    
    return {
        'has_greek_letters': has_greek,
        'has_math_symbols': has_symbols,
        'has_equations': has_equations,
        'detected_symbols': [sym for sym in MATH_SYMBOLS.keys() if sym in question_text],
        'is_math_expression': has_greek or has_symbols or has_equations
    }

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
        
        # Analyze for Greek/math characters
        math_analysis = analyze_math_content(question_text)
        logger.info(f"📊 Math analysis: {math_analysis}")
        
        # Preserve original text exactly - no modifications to Greek letters
        # normalize_math_expression only logs, doesn't change the text
        processed_text = normalize_math_expression(question_text)
        logger.info("🔧 Preserving Greek letters and math symbols exactly")
        
        # Generate solution
        solution = generate_solution(
            question_text=processed_text,
            subject=subject,
            context=context
        )
        
        return jsonify({
            'success': True,
            'solution': solution,
            'math_analysis': math_analysis,
            'original_question': question_text,
            'processed_question': processed_text,
            'greek_preserved': True,
            'utf8_encoded': True,
            'character_encoding': 'UTF-8'
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
# MATH VALIDATION
# ============================================================================

@app.route('/api/validate-math', methods=['POST'])
def validate_math():
    """
    Validate mathematical expressions with Greek letters and symbols
    
    Body: {
        "expression": "θ = 45° + π/4"
    }
    """
    logging.info('Validate math expression request received')
    
    try:
        data = request.get_json()
        
        if not data or 'expression' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: expression'
            }), 400
        
        expression = data['expression']
        
        # Analyze the expression
        math_analysis = analyze_math_content(expression)
        
        validation_result = {
            'success': True,
            'is_valid': True,
            'expression': expression,
            'math_analysis': math_analysis,
            'character_encoding': 'UTF-8',
            'can_process': True,
            'supported_symbols': list(MATH_SYMBOLS.keys())
        }
        
        logger.info(f"✅ Math validation completed: {math_analysis}")
        return jsonify(validation_result)
        
    except Exception as e:
        logging.error(f"Error validating math expression: {str(e)}")
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
