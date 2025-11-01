"""
OCR Service - Flask Application with EasyOCR
Lightweight OCR optimized for educational content (math, Greek letters)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import base64
import io
import gc
import time
import re
from PIL import Image
import numpy as np

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Initialize EasyOCR (lazy loading)
ocr_reader = None

def get_ocr_reader():
    """Get or initialize EasyOCR reader"""
    global ocr_reader
    if ocr_reader is None:
        try:
            import easyocr
            logging.info("📄 Initializing EasyOCR (lightweight)...")
            ocr_reader = easyocr.Reader(
                ['en'],  # English only for speed
                gpu=False,  # CPU mode
                model_storage_directory='./models',
                download_enabled=True,
                verbose=False
            )
            logging.info("✅ EasyOCR initialized successfully")
        except Exception as e:
            logging.error(f"❌ Failed to initialize EasyOCR: {e}")
            raise
    return ocr_reader

def preprocess_image(image_data):
    """Optimize image for OCR - resize and enhance"""
    try:
        # Load image
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large (max 2000px width for speed)
        max_width = 2000
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            logging.info(f"📐 Resized image to {new_size}")
        
        # Convert to numpy array
        img_np = np.array(img)
        
        return img_np
    except Exception as e:
        logging.error(f"Image preprocessing failed: {e}")
        raise

def detect_math_content(text):
    """Detect if text contains mathematical symbols"""
    math_indicators = [
        r'[∫∑∏√±×÷≠≤≥∞∂∇]',  # Math symbols
        r'[α-ωΑ-Ω]',              # Greek letters
        r'\d+\s*[+\-*/=]\s*\d+',  # Simple equations
        r'[a-zA-Z]\^[0-9]',       # Exponents
        r'\([^)]+\)',             # Parentheses
        r'\\frac|\\sqrt|\\int',   # LaTeX commands
    ]
    
    for pattern in math_indicators:
        if re.search(pattern, text):
            return True
    return False

def extract_text_with_retry(image_data, max_retries=2):
    """Extract text with automatic retry on failure"""
    for attempt in range(max_retries):
        try:
            # Preprocess image
            img = preprocess_image(image_data)
            
            # Get OCR reader
            reader = get_ocr_reader()
            
            # Run OCR
            logging.info(f"🔍 Running EasyOCR (attempt {attempt + 1}/{max_retries})")
            result = reader.readtext(img, detail=1)
            
            # Clear image from memory immediately
            del img
            gc.collect()
            
            return result
            
        except Exception as e:
            if attempt < max_retries - 1:
                logging.warning(f"OCR attempt {attempt + 1} failed: {e}, retrying...")
                time.sleep(0.5)
                gc.collect()
            else:
                logging.error(f"All OCR attempts failed: {e}")
                raise
    
    return None

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'service': 'Qadam OCR Service (EasyOCR)',
        'status': 'running',
        'version': '3.0',
        'ocr_engine': 'EasyOCR',
        'features': ['math_symbols', 'greek_letters', 'lightweight'],
        'endpoints': {
            'health': '/api/health',
            'extract_text': '/api/extract-text',
            'extract_with_boxes': '/api/extract-text-with-boxes'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logging.info('Health check requested')
    
    # Check if EasyOCR is installed
    easyocr_installed = False
    easyocr_version = None
    try:
        import easyocr
        easyocr_installed = True
        easyocr_version = easyocr.__version__ if hasattr(easyocr, '__version__') else 'unknown'
    except ImportError:
        pass

    return jsonify({
        'status': 'healthy',
        'service': 'OCR Service (EasyOCR on VM)',
        'ocr_engine': 'EasyOCR',
        'easyocr_installed': easyocr_installed,
        'easyocr_version': easyocr_version,
        'features': ['math_detection', 'greek_letters', 'lightweight'],
        'python_version': os.sys.version
    })

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """
    Extract text from an image using EasyOCR
    
    Request:
        - file: Image file (multipart/form-data)
        OR
        - image_base64: Base64 encoded image (JSON)
    
    Response:
        {
            'success': True,
            'text': 'Extracted text...',
            'confidence': 0.95,
            'has_math': False,
            'details': [...]
        }
    """
    try:
        logging.info("📥 Received OCR request")
        
        # Get image data
        image_data = None
        
        # Check for file upload
        if 'file' in request.files:
            file = request.files['file']
            image_data = file.read()
            logging.info(f"📸 Received file upload: {len(image_data)} bytes")
        
        # Check for base64 image
        elif request.json and 'image_base64' in request.json:
            image_base64 = request.json['image_base64']
            image_data = base64.b64decode(image_base64)
            logging.info(f"📸 Received base64 image: {len(image_data)} bytes")
        
        else:
            return jsonify({
                'success': False,
                'error': 'No image provided. Send either file or image_base64',
                'text': ''
            }), 400
        
        # Perform OCR with retry logic
        try:
            result = extract_text_with_retry(image_data)
            
            # Process results
            if not result:
                return jsonify({
                    'success': True,
                    'text': '',
                    'confidence': 0.0,
                    'has_math': False,
                    'details': [],
                    'message': 'No text detected in image'
                })
            
            # Extract text and confidence
            texts = []
            confidences = []
            details = []
            
            for bbox, text, conf in result:
                texts.append(text)
                confidences.append(conf)
                details.append({
                    'text': text,
                    'confidence': round(conf, 3),
                    'box': bbox
                })
            
            # Combine all text
            full_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Detect math content
            has_math = detect_math_content(full_text)
            if has_math:
                logging.info("📐 Math content detected in text")
            
            logging.info(f"✅ OCR completed: {len(texts)} segments detected")
            
            response_data = {
                'success': True,
                'text': full_text,
                'confidence': round(avg_confidence, 3),
                'has_math': has_math,
                'line_count': len(texts)
            }
            
            # Only include details if requested (saves bandwidth)
            if request.args.get('include_details') == 'true':
                response_data['details'] = details
            
            return jsonify(response_data)

        finally:
            # Clean up memory
            gc.collect()
    
    except Exception as e:
        logging.error(f"❌ OCR failed: {str(e)}")
        gc.collect()
        return jsonify({
            'success': False,
            'error': str(e),
            'text': ''
        }), 500

@app.route('/api/extract-text-with-boxes', methods=['POST'])
def extract_text_with_boxes():
    """Same as extract-text but always returns detailed bounding box information"""
    # Force include_details
    request.args = request.args.copy()
    request.args['include_details'] = 'true'
    return extract_text()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logging.info(f"🚀 Starting OCR service on port {port}")
    logging.info(f"📦 Using EasyOCR (lightweight, math-aware)")
    app.run(host='0.0.0.0', port=port, debug=False)
