"""
Main Backend Flask Application
Integrates with OCR Azure Function
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# OCR Function App URL
OCR_FUNCTION_URL = os.getenv('OCR_FUNCTION_URL', 'https://qadam-ocr-addrcugfg4d4drg7.canadacentral-01.azurewebsites.net')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Main Backend',
        'ocr_service': OCR_FUNCTION_URL
    })

@app.route('/api/ocr/scan', methods=['POST'])
def scan_document():
    """
    Scan document using OCR service
    
    Accepts:
    - file: Image/PDF file upload
    - image_base64: Base64 encoded image (JSON)
    - language: Optional language code (default: 'en')
    
    Returns:
    - OCR results with extracted text
    """
    try:
        # Check if it's a file upload or JSON request
        if 'file' in request.files:
            # File upload - forward to OCR service
            file = request.files['file']
            language = request.form.get('language', 'en')
            
            # Determine endpoint based on file type
            file_extension = file.filename.split('.')[-1].lower() if file.filename else ''
            
            if file_extension == 'pdf':
                ocr_endpoint = f"{OCR_FUNCTION_URL}/api/ocr/pdf"
            else:
                ocr_endpoint = f"{OCR_FUNCTION_URL}/api/ocr/image"
            
            # Forward the file to OCR service
            files = {'file': (file.filename, file.stream, file.content_type)}
            data = {'language': language}
            
            response = requests.post(ocr_endpoint, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                return jsonify(response.json())
            else:
                return jsonify({
                    'success': False,
                    'error': f'OCR service error: {response.text}'
                }), response.status_code
                
        elif request.is_json:
            # JSON request with base64 image
            data = request.get_json()
            
            if 'image_base64' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing image_base64 field'
                }), 400
            
            # Forward to OCR service
            ocr_endpoint = f"{OCR_FUNCTION_URL}/api/ocr/image"
            
            payload = {
                'image_base64': data['image_base64'],
                'language': data.get('language', 'en')
            }
            
            response = requests.post(ocr_endpoint, json=payload, timeout=60)
            
            if response.status_code == 200:
                return jsonify(response.json())
            else:
                return jsonify({
                    'success': False,
                    'error': f'OCR service error: {response.text}'
                }), response.status_code
        else:
            return jsonify({
                'success': False,
                'error': 'No file or image_base64 provided'
            }), 400
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'OCR service timeout - image may be too large or complex'
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Failed to connect to OCR service: {str(e)}'
        }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/ocr/languages', methods=['GET'])
def get_languages():
    """Get supported OCR languages"""
    try:
        response = requests.get(f"{OCR_FUNCTION_URL}/api/ocr/languages", timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch languages: {str(e)}'
        }), 503

@app.route('/api/ocr/health', methods=['GET'])
def ocr_health():
    """Check OCR service health"""
    try:
        response = requests.get(f"{OCR_FUNCTION_URL}/api/health", timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'OCR service unavailable: {str(e)}'
        }), 503

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
