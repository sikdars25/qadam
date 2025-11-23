#!/usr/bin/env python3
"""
Separate Diagram Endpoint for Clean Text/Diagram Separation
Enhanced with Comprehensive Diagram Analysis
"""

import os
import requests
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from simple_diagram_extractor import analyze_and_generate_diagram
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://130.107.48.221:8001')
AI_ENABLED = os.getenv('AI_ENABLED', 'false').lower() == 'true'  # Disabled to force fallback for testing

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

def get_solution_with_diagrams_from_ai(question_text: str, subject: str, solution_type: str) -> Dict[str, Any]:
    """
    Get solution with diagrams from AI service (first call)
    """
    try:
        payload = {
            'question_text': question_text,
            'subject': subject,
            'solution_type': solution_type
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
                    'solution': result.get('solution', ''),
                    'diagrams': result.get('diagrams', [])
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'solution': '',
                    'diagrams': []
                }
        else:
            return {
                'success': False,
                'error': f'AI service error: {response.status_code}',
                'solution': '',
                'diagrams': []
            }
            
    except Exception as e:
        logger.exception("Error getting solution from AI service")
        return {
            'success': False,
            'error': str(e),
            'solution': '',
            'diagrams': []
        }

def extract_diagram_tags_from_solution(solution_text: str) -> List[str]:
    """
    Extract all diagram tags from the solution text
    """
    pattern = r'\[DIAGRAM:\s*([^\]]+)\]'
    matches = re.findall(pattern, solution_text, re.IGNORECASE)
    return [m.strip() for m in matches]

def create_final_diagram_prompt(diagram_tags: List[str], question_text: str) -> str:
    """
    Create a summarized prompt for final diagram generation
    """
    diagram_summary = "\n".join([f"- {tag}" for tag in diagram_tags])
    
    final_prompt = f"""
Based on the following mathematical construction problem and diagram requirements, create a single, comprehensive diagram description that incorporates all the construction steps:

Question: {question_text}

Required Diagram Elements:
{diagram_summary}

Please create a detailed, step-by-step diagram description that combines all these construction elements into a single coherent geometric diagram. Focus on:
1. The geometric construction process
2. Clear labeling of all points, lines, and angles
3. Proper sequence of construction steps
4. Mathematical accuracy

Return your response in this format:
[FINAL_DIAGRAM: Your comprehensive diagram description here]
"""
    
    return final_prompt

def get_final_diagram_from_ai(final_prompt: str) -> Dict[str, Any]:
    """
    Get final diagram description from AI service (second call)
    """
    try:
        payload = {
            'question_text': final_prompt,
            'subject': 'Mathematics',
            'solution_type': 'diagram-only'
        }
        
        response = requests.post(
            f"{AI_SERVICE_URL}/solve-question",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                solution = result.get('solution', '')
                # Extract the final diagram tag
                final_diagram_match = re.search(r'\[FINAL_DIAGRAM:\s*([^\]]+)\]', solution, re.IGNORECASE | re.DOTALL)
                
                if final_diagram_match:
                    final_diagram = final_diagram_match.group(1).strip()
                    return {
                        'success': True,
                        'final_diagram': final_diagram,
                        'raw_solution': solution
                    }
                else:
                    # If no FINAL_DIAGRAM tag, use the whole solution
                    return {
                        'success': True,
                        'final_diagram': solution,
                        'raw_solution': solution
                    }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'final_diagram': ''
                }
        else:
            return {
                'success': False,
                'error': f'AI service error: {response.status_code}',
                'final_diagram': ''
            }
            
    except Exception as e:
        logger.exception("Error getting final diagram from AI service")
        return {
            'success': False,
            'error': str(e),
            'final_diagram': ''
        }

def get_solution_from_ai_service(question_text, subject="Mathematics", solution_type="with-diagram"):
    """Get solution text from AI service with two-step approach and fallback"""
    if not AI_ENABLED or not check_ai_service():
        logger.info("AI service not available, using fallback two-step approach")
        
        # Generate a basic fallback solution for common geometry problems
        fallback_solution = generate_fallback_solution(question_text)
        
        # Extract diagram tags from fallback
        diagram_tags = extract_diagram_tags_from_solution(fallback_solution)
        logger.info(f"Fallback: Extracted {len(diagram_tags)} diagram tags")
        
        # Create final diagram from fallback tags
        if diagram_tags:
            final_diagram = create_final_diagram_from_tags(diagram_tags, question_text)
            return {
                'success': True,
                'solution': fallback_solution,
                'final_diagram': final_diagram,
                'diagrams': [],
                'has_diagrams': True,
                'diagram_count': len(diagram_tags),
                'fallback_used': True
            }
        else:
            return {
                'success': True,
                'solution': fallback_solution,
                'final_diagram': None,
                'diagrams': [],
                'has_diagrams': False,
                'diagram_count': 0,
                'fallback_used': True
            }
    
    try:
        # Step 1: Get solution from AI service
        ai_result = get_solution_with_diagrams_from_ai(question_text, subject, solution_type)
        
        if not ai_result['success']:
            logger.error(f"Failed to get solution from AI service: {ai_result['error']}")
            return {
                'success': False,
                'error': f'AI service error: {ai_result["error"]}',
                'solution': '',
                'diagrams': []
            }
        
        solution_text = ai_result['solution']
        logger.info(f"Got solution from AI service (length: {len(solution_text)} chars)")
        
        # Check if solution contains diagram markers
        has_markers = '[DIAGRAM:' in solution_text
        logger.info(f"Solution contains [DIAGRAM:] markers: {has_markers}")
        
        if has_markers:
            diagram_tags = extract_diagram_tags_from_solution(solution_text)
            logger.info(f"Found {len(diagram_tags)} diagram tags in solution:")
            for i, tag in enumerate(diagram_tags[:3]):  # Log first 3
                logger.info(f"  Tag {i+1}: {tag.strip()}")
            
            # Create a summarized prompt for final diagram generation
            final_prompt = create_final_diagram_prompt(diagram_tags, question_text)
            
            # Step 2: Get final diagram description from AI service
            final_diagram_result = get_final_diagram_from_ai(final_prompt)
            
            if final_diagram_result['success']:
                final_diagram = final_diagram_result['final_diagram']
                logger.info(f"Got final diagram from AI service (length: {len(final_diagram)} chars)")
                
                return {
                    'success': True,
                    'solution': solution_text,
                    'final_diagram': final_diagram,
                    'diagrams': ai_result['diagrams'],
                    'has_diagrams': True,
                    'diagram_count': len(diagram_tags)
                }
            else:
                logger.error(f"Failed to get final diagram from AI service: {final_diagram_result['error']}")
                # Fallback to creating final diagram from tags
                final_diagram = create_final_diagram_from_tags(diagram_tags, question_text)
                return {
                    'success': True,
                    'solution': solution_text,
                    'final_diagram': final_diagram,
                    'diagrams': ai_result['diagrams'],
                    'has_diagrams': True,
                    'diagram_count': len(diagram_tags),
                    'fallback_used': True
                }
        else:
            return {
                'success': True,
                'solution': solution_text,
                'final_diagram': None,
                'diagrams': ai_result['diagrams'],
                'has_diagrams': False,
                'diagram_count': 0
            }
            
    except Exception as e:
        logger.error(f"AI service request error: {e}")
        return {
            'success': False,
            'error': str(e),
            'solution': '',
            'diagrams': []
        }

def create_final_diagram_from_tags(diagram_tags: List[str], question_text: str) -> str:
    """Create a final diagram description from extracted tags"""
    tag_descriptions = "\n".join([f"{i+1}. {tag}" for i, tag in enumerate(diagram_tags)])
    
    final_diagram = f"""
A comprehensive geometric construction for: {question_text}

Construction Steps:
{tag_descriptions}

This diagram shows the complete step-by-step construction process with all necessary geometric elements, measurements, and labels clearly indicated. The construction follows standard geometric principles with accurate angle measurements and proper sequencing of steps.
"""
    
    return final_diagram.strip()

@app.route('/test-simple', methods=['GET'])
def test_simple():
    """Simple test endpoint that always returns a diagram"""
    return jsonify({
        'success': True,
        'final_diagram': 'TEST DIAGRAM: This is a test diagram to verify frontend is working. Draw base segment BC of length 6 cm, construct 60° angle at B, construct 45° angle at C, complete triangle ABC.',
        'processing_method': 'test_endpoint',
        'content': 'TEST DIAGRAM: This is a test diagram to verify frontend is working. Draw base segment BC of length 6 cm, construct 60° angle at B, construct 45° angle at C, complete triangle ABC.'
    })

@app.route('/analyze-diagrams', methods=['POST', 'OPTIONS'])
def analyze_diagrams():
    """
    Two-Step AI Approach for Diagram Generation
    
    Process:
    1. First call to Groq API: Get solution with diagram tags
    2. Extract and summarize all diagram tags from solution
    3. Second call to Groq API: Send summary for final diagram creation
    4. Return final diagram tag to frontend for display
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
        
        logger.info(f"Starting two-step diagram generation for question: {question_text[:50]}...")
        
        # Step 1: Get solution with diagrams from AI service (first call)
        logger.info("Step 1: Getting solution with diagram tags from AI service...")
        ai_result = get_solution_from_ai_service(question_text, subject, solution_type)
        
        if not ai_result['success']:
            logger.error(f"Failed to get solution from AI service: {ai_result['error']}")
            return jsonify({
                'success': False,
                'error': f'AI service error: {ai_result["error"]}',
                'final_diagram': None
            }), 500
        
        solution_text = ai_result['solution']
        logger.info(f"Got solution from AI service (length: {len(solution_text)} chars)")
        
        # Check if solution contains diagram markers
        has_markers = '[DIAGRAM:' in solution_text
        logger.info(f"Solution contains [DIAGRAM:] markers: {has_markers}")
        
        if not has_markers:
            logger.info("No diagram markers found in solution")
            return jsonify({
                'success': True,
                'final_diagram': None,
                'content': 'No diagram elements found in solution',
                'processing_method': 'no_diagrams_found'
            })
        
        # Step 2: Extract diagram tags from solution
        logger.info("Step 2: Extracting diagram tags from solution...")
        diagram_tags = extract_diagram_tags_from_solution(solution_text)
        logger.info(f"Extracted {len(diagram_tags)} diagram tags:")
        for i, tag in enumerate(diagram_tags):
            logger.info(f"  Tag {i+1}: {tag}")
        
        # Step 3: Create final diagram prompt and get final diagram (second call)
        logger.info("Step 3: Creating final diagram prompt and calling AI service...")
        final_prompt = create_final_diagram_prompt(diagram_tags, question_text)
        
        final_diagram_result = get_final_diagram_from_ai(final_prompt)
        
        if not final_diagram_result['success']:
            logger.error(f"Failed to get final diagram from AI service: {final_diagram_result['error']}")
            return jsonify({
                'success': False,
                'error': f'AI service error: {final_diagram_result["error"]}',
                'final_diagram': None
            }), 500
        
        final_diagram = final_diagram_result['final_diagram']
        logger.info(f"Got final diagram from AI service (length: {len(final_diagram)} chars)")
        
        # Step 4: Return final diagram to frontend
        response = {
            'success': True,
            'final_diagram': final_diagram,
            'content': final_diagram,
            'processing_method': 'two_step_ai_generation',
            'steps': {
                'step1_solution_length': len(solution_text),
                'step2_diagram_tags_count': len(diagram_tags),
                'step3_final_diagram_length': len(final_diagram)
            },
            'metadata': {
                'question_text': question_text,
                'subject': subject,
                'solution_type': solution_type,
                'diagram_tags': diagram_tags,
                'raw_solution': solution_text,
                'final_diagram_raw': final_diagram_result.get('raw_solution', '')
            }
        }
        
        logger.info("Two-step diagram generation completed successfully")
        return jsonify(response), 200
        
    except Exception as e:
        logger.exception("Error in two-step diagram generation")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'final_diagram': None
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
