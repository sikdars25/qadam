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
from simple_diagram_extractor import analyze_and_generate_diagram

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://130.107.48.221:8001')
AI_ENABLED = os.getenv('AI_ENABLED', 'false').lower() == 'true'  # Disabled to force fallback for frontend testing

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

def generate_fallback_solution(question_text):
    """Generate a basic fallback solution for common geometry problems with diagram markers"""
    question_lower = question_text.lower()
    
    # Perpendicular bisector problems
    if 'perpendicular bisector' in question_lower:
        return f'''
To construct the perpendicular bisector of a line segment, follow these steps:

Step 1: Draw the given line segment AB.
[DIAGRAM: Line segment AB with given length]

Step 2: With A as center, draw an arc with radius more than half of AB.
[DIAGRAM: Arc drawn from point A]

Step 3: With B as center, draw another arc with the same radius to intersect the first arc.
[DIAGRAM: Arc drawn from point B intersecting first arc]

Step 4: Draw a line through the intersection points of the arcs.
[DIAGRAM: Perpendicular bisector line through intersection points]

The perpendicular bisector is now constructed.

Question: {question_text}
'''
    
    # Triangle construction problems
    elif 'triangle' in question_lower and 'construct' in question_lower:
        if 'bc' in question_lower and 'angle' in question_lower:
            return f'''
To construct triangle ABC with the given specifications, follow these steps:

Step 1: Draw the base segment BC of the specified length.
[DIAGRAM: Base segment BC with given length]

Step 2: At point B, construct the specified angle using a protractor.
[DIAGRAM: Angle constructed at point B]

Step 3: At point C, construct the specified angle using a protractor.
[DIAGRAM: Angle constructed at point C]

Step 4: The intersection of the two angle rays will be point A, completing the triangle.
[DIAGRAM: Triangle ABC completed]

The final triangle ABC is constructed with the given specifications.

Question: {question_text}
'''
        else:
            return f'''
To construct the triangle with the given specifications, follow these steps:

Step 1: Draw the base segment of the specified length.
[DIAGRAM: Base segment of given length]

Step 2: Construct the required angles at the base vertices.
[DIAGRAM: Angles constructed at base vertices]

Step 3: Complete the triangle by connecting the vertices.
[DIAGRAM: Triangle completed]

Question: {question_text}
'''
    
    # General geometry construction
    elif 'construct' in question_lower:
        return f'''
To construct the geometric figure with the given specifications, follow these steps:

Step 1: Draw the base elements as specified.
[DIAGRAM: Base elements drawn]

Step 2: Construct the required angles and measurements.
[DIAGRAM: Angles and measurements constructed]

Step 3: Complete the construction using the given parameters.
[DIAGRAM: Final construction completed]

Question: {question_text}
'''
    
    # Default fallback
    else:
        return f'''
Solution for the given problem:

This is a fallback solution generated when the AI service is not available.
[DIAGRAM: Basic construction diagram]

Question: {question_text}
'''

def get_solution_from_ai_service(question_text, subject="Mathematics", solution_type="with-diagram"):
    """Get solution text from AI service"""
    if not AI_ENABLED or not check_ai_service():
        logger.info("AI service not available, using fallback solution generation")
        
        # Generate a basic fallback solution for common geometry problems
        fallback_solution = generate_fallback_solution(question_text)
        
        return {
            'success': True,
            'solution': fallback_solution,
            'diagrams': [],
            'has_diagrams': False,
            'diagram_count': 0,
            'fallback_used': True
        }
    
    try:
        # Request solution from AI service
        payload = {
            'question_text': question_text,
            'subject': subject,
            'solution_type': solution_type
        }
        
        logger.info(f"Requesting solution from AI service: {AI_SERVICE_URL}/solve-question")
        response = requests.post(
            f"{AI_SERVICE_URL}/solve-question",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                logger.info(f"AI service returned solution with diagrams: {result.get('has_diagrams', False)}")
                return {
                    'success': True,
                    'solution': result.get('solution', ''),
                    'diagrams': result.get('diagrams', []),
                    'has_diagrams': result.get('has_diagrams', False),
                    'diagram_count': result.get('diagram_count', 0)
                }
            else:
                logger.error(f"AI service returned error: {result.get('error', 'Unknown error')}")
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'solution': '',
                    'diagrams': []
                }
        else:
            logger.error(f"AI service HTTP error: {response.status_code}")
            return {
                'success': False,
                'error': f'AI service error: {response.status_code}',
                'solution': '',
                'diagrams': []
            }
            
    except Exception as e:
        logger.error(f"AI service request error: {e}")
        return {
            'success': False,
            'error': str(e),
            'solution': '',
            'diagrams': []
        }

@app.route('/analyze-diagrams', methods=['POST', 'OPTIONS'])
def analyze_diagrams():
    """
    Analyze solution text and generate unified diagram
    
    Expected payload:
    {
        "question_text": "Original question text",
        "subject": "Subject name (optional)",
        "solution_type": "with-diagram or step-by-step (optional)"
    }
    
    Process:
    1. Get solution from AI service
    2. Extract diagram markers from solution
    3. Generate unified diagram from all markers
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
        
        question_text = data.get('question_text', '')
        subject = data.get('subject', 'Mathematics')
        solution_type = data.get('solution_type', 'with-diagram')
        
        if not question_text.strip():
            return jsonify({
                'success': False,
                'error': 'question_text is required'
            }), 400
        
        logger.info(f"Analyzing diagrams for question: {question_text[:50]}...")
        
        # Step 1: Get solution from AI service
        ai_result = get_solution_from_ai_service(question_text, subject, solution_type)
        
        if not ai_result['success']:
            logger.error(f"Failed to get solution from AI service: {ai_result['error']}")
            return jsonify({
                'success': False,
                'error': f'AI service error: {ai_result["error"]}',
                'diagram': None
            }), 500
        
        solution_text = ai_result['solution']
        logger.info(f"Got solution from AI service (length: {len(solution_text)} chars)")
        
        # Log solution preview for debugging
        logger.info(f"Solution preview: {solution_text[:200]}...")
        
        # Check if solution contains diagram markers
        has_markers = '[DIAGRAM:' in solution_text
        logger.info(f"Solution contains [DIAGRAM:] markers: {has_markers}")
        
        if has_markers:
            import re
            markers = re.findall(r'\[DIAGRAM:([^\]]+)\]', solution_text)
            logger.info(f"Found {len(markers)} diagram markers in solution:")
            for i, marker in enumerate(markers[:3]):  # Log first 3
                logger.info(f"  Marker {i+1}: {marker.strip()}")
        
        # Step 2: Extract all [DIAGRAM:...] texts and combine them
        logger.info("Extracting diagram texts from solution...")
        combined_diagram = analyze_and_generate_diagram(solution_text, question_text)
        
        # Log extraction results
        logger.info(f"Extraction results: type={combined_diagram['type']}, elements={combined_diagram['elements_count']}")
        if combined_diagram['elements_count'] > 0:
            logger.info(f"Extracted diagram texts: {combined_diagram['raw_texts']}")
        
        # Step 3: Return simple result with combined diagram texts
        response = {
            'success': True,
            'diagram': combined_diagram,
            'diagrams': combined_diagram.get('diagrams', []),  # Top-level diagrams array
            'content': combined_diagram.get('content', ''),  # Top-level content field
            'text_content': combined_diagram.get('text_content', ''),  # Top-level text content
            'svg': combined_diagram.get('svg', ''),  # Top-level SVG field
            'type': combined_diagram.get('type', 'empty'),  # Top-level type field
            'elements_count': combined_diagram.get('elements_count', 0),  # Top-level elements count
            'ai_solution': {
                'solution_text': solution_text,
                'has_diagrams': ai_result['has_diagrams'],
                'diagram_count': ai_result['diagram_count'],
                'ai_diagrams': ai_result['diagrams']
            },
            'metadata': {
                'question_text': question_text,
                'subject': subject,
                'solution_type': solution_type,
                'solution_length': len(solution_text),
                'has_diagrams': combined_diagram['elements_count'] > 0,
                'elements_found': combined_diagram['elements_count'],
                'processing_method': 'extract_and_append_diagram_texts'
            }
        }
        
        logger.info(f"Generated combined diagram with {combined_diagram['elements_count']} diagram texts")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error analyzing diagrams: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'diagram': None
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
