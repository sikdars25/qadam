#!/usr/bin/env python3
"""
Diagram Service Flask API
Analyzes AI solution texts and generates unified diagrams
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
from comprehensive_diagram_generator import analyze_and_generate_diagram

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'comprehensive_diagram_service',
        'version': '1.0.0'
    })

@app.route('/analyze-diagrams', methods=['POST'])
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
        
        # Generate unified diagram
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

@app.route('/test-diagram', methods=['GET'])
def test_diagram():
    """Test endpoint with sample data"""
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
        result = analyze_and_generate_diagram(sample_solution, sample_question)
        
        return jsonify({
            'success': True,
            'diagram': result,
            'test_info': {
                'sample_question': sample_question,
                'diagram_markers_found': result['elements_count'],
                'diagram_type': result['type']
            }
        })
        
    except Exception as e:
        logger.error(f"Error in test diagram: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        }), 500

@app.route('/generate-diagrams', methods=['POST'])
def generate_diagrams():
    """
    Legacy endpoint for compatibility with existing frontend
    Maps to the new analyze-diagrams endpoint
    """
    try:
        data = request.get_json()
        
        # Map old format to new format
        solution_text = f"Question: {data.get('question_text', '')}\n\nSubject: {data.get('subject', 'Mathematics')}\n\nSolution with diagrams:"
        question_text = data.get('question_text', '')
        
        # Add some sample diagram markers if none exist
        if '[DIAGRAM:' not in solution_text:
            solution_text += f"\n\n[DIAGRAM: Line segment for {question_text[:20]}...]"
        
        # Call the new analyzer
        result = analyze_and_generate_diagram(solution_text, question_text)
        
        # Format response for legacy frontend
        return jsonify({
            'success': True,
            'diagrams': [result],  # Wrap in array for compatibility
            'diagram_count': result['elements_count'],
            'has_diagrams': result['elements_count'] > 0
        })
        
    except Exception as e:
        logger.error(f"Error in generate-diagrams: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

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

if __name__ == '__main__':
    print("🎨 Starting Comprehensive Diagram Service...")
    print("📊 Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /analyze-diagrams - Analyze solution and generate unified diagram")
    print("  POST /generate-diagrams - Legacy compatibility endpoint")
    print("  GET  /test-diagram - Test with sample data")
    print()
    
    # Run on port 5002 to avoid conflicts
    app.run(host='0.0.0.0', port=5002, debug=True)
