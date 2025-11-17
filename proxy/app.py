"""
Backend Proxy Application with LaTeX OCR API Integration
This is a minimal proxy app specifically for the LaTeX OCR API endpoint
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
from datetime import datetime

# Add the ocr directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ocr'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Import LaTeX OCR API Integration
try:
    from latex_ocr_api_integration import LatexOCRIntegration
    LATEX_OCR_ENABLED = True
    logger.info("✅ LaTeX OCR API integration enabled")
except ImportError as e:
    logger.error(f"LaTeX OCR API integration disabled: {e}")
    LATEX_OCR_ENABLED = False

# Mock JWT authentication for testing (replace with real auth in production)
def mock_token_required(f):
    """Mock JWT decorator - replace with real authentication"""
    def wrapper(*args, **kwargs):
        # For now, we'll just pass through
        # In production, this would validate JWT tokens
        return f(*args, **kwargs)
    return wrapper

def mock_get_current_user():
    """Mock current user function - replace with real auth"""
    return {
        'id': 1,
        'username': 'test_user',
        'is_admin': False
    }

@app.route('/api/latex-ocr-solve', methods=['POST'])
@mock_token_required
def solve_latex_ocr_question():
    """Solve OCR text question using LaTeX OCR integration with free math/science APIs and Groq explanations"""
    if not LATEX_OCR_ENABLED:
        return jsonify({'error': 'LaTeX OCR integration not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        ocr_text = data.get('ocr_text', '').strip()
        subject = data.get('subject', '')
        
        if not ocr_text:
            return jsonify({'error': 'OCR text is required'}), 400
        
        # Validate input length
        if len(ocr_text) > 10000:  # 10k character limit
            return jsonify({'error': 'OCR text too long (max 10000 characters)'}), 400
        
        logger.info(f"🔍 Processing LaTeX OCR question for user {mock_get_current_user()['id']}")
        logger.info(f"📝 OCR text: {ocr_text[:100]}...")
        
        # Initialize the integration
        integration = LatexOCRIntegration()
        
        # Process the OCR text with timeout protection
        import signal
        from contextlib import contextmanager
        
        @contextmanager
        def time_limit(seconds):
            def signal_handler(signum, frame):
                raise TimeoutError("Processing timed out")
            signal.signal(signal.SIGALRM, signal_handler)
            signal.alarm(seconds)
            try:
                yield
            finally:
                signal.alarm(0)
        
        try:
            with time_limit(300):  # 5 minute timeout
                result = integration.process_single_question(ocr_text, subject)
        except TimeoutError:
            return jsonify({'error': 'Processing timed out - question may be too complex'}), 408
        
        if result['success']:
            # Prepare response (exclude sensitive data)
            response_data = {
                'success': True,
                'original_text': result['original_text'],
                'subject': result['subject'],
                'detected_expressions': result['detected_expressions'],
                'final_answer': result['final_answer'],
                'processing_time_seconds': result.get('processing_time_seconds', 0)
            }
            
            # Include API results only if admin (for debugging)
            current_user = mock_get_current_user()
            if current_user.get('is_admin', False):
                response_data['api_results'] = result['api_results']
            
            return jsonify(response_data)
        else:
            return jsonify({
                'error': 'Failed to process OCR text', 
                'details': result.get('error', 'Unknown error'),
                'processing_time_seconds': result.get('processing_time_seconds', 0)
            }), 500
            
    except Exception as e:
        import traceback
        logger.error(f"❌ LaTeX OCR processing error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Internal server error during OCR processing'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'latex_ocr_enabled': LATEX_OCR_ENABLED,
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, port=port, host='0.0.0.0')
