#!/usr/bin/env python3
"""
Separate Diagram Endpoint for Clean Text/Diagram Separation
Enhanced with Comprehensive Diagram Analysis
"""

import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from comprehensive_diagram_generator import analyze_and_generate_diagram

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://130.107.48.221:8001')
AI_ENABLED = os.getenv('AI_ENABLED', 'true').lower() == 'true'

def check_ai_service():
    """Check if AI service is available"""
    try:
        response = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"AI service check failed: {e}")
        return False

def generate_diagrams_only(question_text, subject="Mathematics"):
    """Generate only diagrams for the given question"""
    if not AI_ENABLED or not check_ai_service():
        return {
            'success': False,
            'error': 'AI service not available',
            'diagrams': []
        }
    
    try:
        # Request diagram generation from AI service
        payload = {
            'question_text': question_text,
            'subject': subject,
            'solution_type': 'with-diagram'
        }
        
        response = requests.post(
            f"{AI_SERVICE_URL}/solve-question",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {
                    'success': True,
                    'diagrams': result.get('diagrams', []),
                    'diagram_count': result.get('diagram_count', 0),
                    'has_diagrams': result.get('has_diagrams', False)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'diagrams': []
                }
        else:
            return {
                'success': False,
                'error': f'AI service error: {response.status_code}',
                'diagrams': []
            }
            
    except Exception as e:
        logger.error(f"Diagram generation error: {e}")
        return {
            'success': False,
            'error': str(e),
            'diagrams': []
        }

@app.route('/analyze-diagrams', methods=['POST', 'OPTIONS'])
def analyze_diagrams():
    """
    Analyze solution text and generate unified diagram
    
    Expected payload:
    {
        "solution_text": "AI solution text with [DIAGRAM: ...] markers",
        "question_text": "Original question text",
        "subject": "Subject name (optional)"
    }
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        solution_text = data.get('solution_text', '')
        question_text = data.get('question_text', '')
        subject = data.get('subject', 'Mathematics')
        
        if not solution_text:
            return jsonify({
                'success': False,
                'error': 'solution_text is required'
            }), 400
        
        if not question_text:
            return jsonify({
                'success': False,
                'error': 'question_text is required'
            }), 400
        
        logger.info(f"Analyzing diagrams for question: {question_text[:50]}...")
        logger.info(f"Solution text length: {len(solution_text)} characters")
        
        # Generate unified diagram using comprehensive analyzer
        result = analyze_and_generate_diagram(solution_text, question_text)
        
        # Add metadata
        response = {
            'success': True,
            'diagram': result,
            'metadata': {
                'question_text': question_text,
                'subject': subject,
                'solution_length': len(solution_text),
                'has_diagrams': result['elements_count'] > 0,
                'elements_found': result['elements_count']
            }
        }
        
        logger.info(f"Generated {result['type']} diagram with {result['elements_count']} elements")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error analyzing diagrams: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/generate-diagrams', methods=['POST', 'OPTIONS'])
def generate_diagrams():
    """Generate diagrams for a question"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if not AI_ENABLED:
        return jsonify({
            'success': False,
            'error': 'AI features are not enabled',
            'diagrams': []
        }), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided',
                'diagrams': []
            }), 400
        
        question_text = data.get('question_text', '')
        subject = data.get('subject', 'Mathematics')
        
        if not question_text.strip():
            return jsonify({
                'success': False,
                'error': 'Question text is required',
                'diagrams': []
            }), 400
        
        # Generate diagrams
        result = generate_diagrams_only(question_text, subject)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in generate_diagrams: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'diagrams': []
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_enabled': AI_ENABLED,
        'ai_service_available': check_ai_service()
    })

@app.route('/test-diagram', methods=['GET'])
def test_diagram():
    """Test endpoint that always returns a sample diagram"""
    # Test the comprehensive diagram analyzer
    sample_solution = """
    Step 1: Draw the base line segment.
    
    [DIAGRAM: Line segment BC with a length of 6 cm marked on it]
    
    Step 2: Mark angle measurements at the endpoints.
    
    [DIAGRAM: A simple line segment BC with angle measurements for B and C]
    
    Step 3: Construct the perpendicular bisector.
    
    [DIAGRAM: Perpendicular bisector of line segment BC]
    
    Step 4: Complete the construction.
    """
    
    sample_question = "Construct a perpendicular bisector of line segment BC with length 6cm"
    
    try:
        # Test comprehensive diagram analyzer
        comprehensive_result = analyze_and_generate_diagram(sample_solution, sample_question)
        
        # Return both old and new format for compatibility
        return jsonify({
            'success': True,
            'comprehensive_diagram': comprehensive_result,
            'legacy_diagrams': [
                {
                    'type': 'geometry',
                    'subtype': 'triangle',
                    'description': 'Sample triangle ABC with vertices A, B, C',
                    'ascii': '''
                       /\\
                      /  \\
                   A /____\\ C
                      B
                    ''',
                    'svg': '<svg width="200" height="150"><polygon points="100,20 170,130 30,130" fill="none" stroke="#007bff" stroke-width="2"/></svg>',
                    'position': 1
                }
            ],
            'test_info': {
                'sample_question': sample_question,
                'comprehensive_elements_found': comprehensive_result['elements_count'],
                'comprehensive_diagram_type': comprehensive_result['type'],
                'service_version': 'enhanced_with_comprehensive_analysis'
            }
        })
        
    except Exception as e:
        logger.error(f"Error in comprehensive test diagram: {str(e)}")
        # Fallback to legacy format
        return jsonify({
            'success': True,
            'diagrams': [
                {
                    'type': 'geometry',
                    'subtype': 'triangle',
                    'description': 'Sample triangle ABC with vertices A, B, C',
                    'ascii': '''
                       /\\
                      /  \\
                   A /____\\ C
                      B
                    ''',
                    'svg': '<svg width="200" height="150"><polygon points="100,20 170,130 30,130" fill="none" stroke="#007bff" stroke-width="2"/></svg>',
                    'position': 1
                }
            ],
            'diagram_count': 1,
            'has_diagrams': True,
            'fallback_reason': 'Comprehensive analyzer failed'
        })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))  # Use different port to avoid conflicts
    app.run(host='0.0.0.0', port=port, debug=True)
