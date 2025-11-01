"""
OCR Service - Flask Application
Runs the Azure Function App as a standalone Flask service on Azure VM
"""

from flask import Flask, request, jsonify
import azure.functions as func
import logging
import sys

# Import the Azure Functions
from function_app import (
    health_check,
    extract_text,
    extract_text_with_boxes,
    extract_from_pdf
)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def azure_func_to_flask(azure_func):
    """Convert Azure Function to Flask route"""
    def wrapper():
        try:
            # Get request data
            if request.method == 'POST':
                body = request.get_data()
            else:
                body = b''
            
            # Create mock Azure Functions request
            req = func.HttpRequest(
                method=request.method,
                url=request.url,
                headers=dict(request.headers),
                params=dict(request.args),
                route_params={},
                body=body
            )
            
            # Call Azure Function
            response = azure_func(req)
            
            # Convert Azure Functions response to Flask response
            return (
                response.get_body(),
                response.status_code,
                {'Content-Type': response.headers.get('Content-Type', 'application/json')}
            )
        except Exception as e:
            logging.error(f"Error in {azure_func.__name__}: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    wrapper.__name__ = azure_func.__name__
    return wrapper

# Health check
@app.route('/api/health', methods=['GET'])
def health():
    return azure_func_to_flask(health_check)()

# Extract text from image
@app.route('/api/extract-text', methods=['POST'])
def extract():
    return azure_func_to_flask(extract_text)()

# Extract text with bounding boxes
@app.route('/api/extract-text-with-boxes', methods=['POST'])
def extract_boxes():
    return azure_func_to_flask(extract_text_with_boxes)()

# Extract text from PDF
@app.route('/api/extract-from-pdf', methods=['POST'])
def extract_pdf():
    return azure_func_to_flask(extract_from_pdf)()

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'service': 'Qadam OCR Service',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'extract_text': '/api/extract-text',
            'extract_with_boxes': '/api/extract-text-with-boxes',
            'extract_from_pdf': '/api/extract-from-pdf'
        }
    })

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    app.run(host='0.0.0.0', port=port, debug=False)
