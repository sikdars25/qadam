"""
OCR Service - Flask Application using EasyOCR
Direct Flask app without Azure Functions wrapper
Last deployed: 2025-11-07 20:00:00
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import base64
import io
from PIL import Image
import numpy as np
import easyocr

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
logging.basicConfig(level=logging.INFO)

# Initialize EasyOCR (lazy loading)
ocr_reader = None

def convert_numpy_types(obj):
    """Convert NumPy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    return obj

def get_ocr_reader():
    """Get or initialize EasyOCR reader"""
    global ocr_reader
    if ocr_reader is None:
        try:
            logging.info("📄 Initializing EasyOCR with math support...")
            # Use both English and Latin for better math symbol recognition
            ocr_reader = easyocr.Reader(
                ['en', 'la'],  # English + Latin for math expressions
                gpu=False,
                recog_network='latin_g2'  # Latin character recognition network
            )
            logging.info("✅ EasyOCR initialized successfully with math support")
        except Exception as e:
            logging.error(f"❌ Failed to initialize EasyOCR: {e}")
            raise
    return ocr_reader

def preprocess_image(image_data):
    """Optimize image for OCR - resize and enhance for math content"""
    try:
        # Load image
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large (max 2400px width for better math symbol recognition)
        max_width = 2400
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            logging.info(f"📐 Resized image to {new_size}")
        elif img.width < 800:
            # Upscale small images for better recognition
            ratio = 800 / img.width
            new_size = (800, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            logging.info(f"📐 Upscaled image to {new_size}")
        
        # Convert to numpy array
        img_np = np.array(img)
        
        return img_np
    except Exception as e:
        logging.error(f"Image preprocessing failed: {e}")
        return None

@app.route('/api/health', methods=['GET'])
def health():
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
        'service': 'OCR Service (Flask on VM)',
        'ocr_engine': 'EasyOCR',
        'easyocr_installed': easyocr_installed,
        'easyocr_version': easyocr_version if easyocr_installed else 'unknown',
        'python_version': os.sys.version,
        'features': [
            'greek_math_support',
            'utf8_encoding', 
            'symbol_recognition',
            'latin_language_support'
        ],
        'supported_symbols': [
            'Greek letters: α, β, γ, δ, θ, π, σ, Σ, λ, etc.',
            'Math symbols: √, ∫, ∑, ±, ×, ÷, ≤, ≥, ≠, etc.',
            'Variables: λn, λp, λn/λp preserved as-is'
        ]
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
            "success": true,
            "text": "extracted text",
            "confidence": 0.95
        }
    """
    try:
        # Get image from request
        if 'file' in request.files:
            file = request.files['file']
            image_data = file.read()
        elif request.is_json:
            data = request.get_json()
            image_base64 = data.get('image_base64', '')
            image_data = base64.b64decode(image_base64)
        else:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        # Preprocess image
        img_np = preprocess_image(image_data)
        if img_np is None:
            return jsonify({'success': False, 'error': 'Failed to process image'}), 500
        
        # Get OCR reader
        reader = get_ocr_reader()
        
        # Perform OCR with optimized parameters for math content
        logging.info("🔍 Performing OCR with math optimization...")
        results = reader.readtext(
            img_np,
            detail=1,
            paragraph=False,  # Detect individual text elements
            min_size=10,      # Detect smaller text (math symbols)
            text_threshold=0.6,  # Lower threshold for math symbols
            low_text=0.3      # Detect faint text
        )
        
        # Extract text from results
        # EasyOCR returns: [(bbox, text, confidence), ...]
        extracted_text = ' '.join([text for (bbox, text, conf) in results])
        avg_confidence = sum([conf for (_, _, conf) in results]) / len(results) if results else 0
        
        logging.info(f"✅ OCR completed: {len(extracted_text)} characters, confidence: {avg_confidence:.2f}")
        
        # Convert NumPy types to Python native types for JSON serialization
        details = [
            {
                'text': text,
                'confidence': float(conf),
                'bbox': convert_numpy_types(bbox)
            }
            for (bbox, text, conf) in results
        ]
        
        return jsonify({
            'success': True,
            'text': extracted_text,
            'confidence': float(avg_confidence),
            'details': details
        })
        
    except Exception as e:
        logging.error(f"❌ OCR error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/extract-from-pdf', methods=['POST'])
def extract_from_pdf():
    """
    Extract text from PDF using EasyOCR
    
    Request:
        - file: PDF file (multipart/form-data)
    
    Response:
        {
            "success": true,
            "text": "extracted text from all pages",
            "pages": 5
        }
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        try:
            import fitz  # PyMuPDF
            
            # Read PDF
            pdf_bytes = file.read()
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            all_text = []
            reader = get_ocr_reader()
            
            # Process each page
            for page_num in range(len(pdf_document)):
                logging.info(f"🔍 Processing page {page_num + 1}/{len(pdf_document)}")
                page = pdf_document[page_num]
                
                # Convert page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_data = pix.tobytes("png")
                
                # Preprocess and perform OCR
                img_np = preprocess_image(img_data)
                if img_np is not None:
                    results = reader.readtext(img_np)
                    page_text = ' '.join([text for (bbox, text, conf) in results])
                    all_text.append(page_text)
            
            pdf_document.close()
            
            combined_text = '\n\n'.join(all_text)
            
            logging.info(f"✅ PDF OCR completed: {len(combined_text)} characters from {len(all_text)} pages")
            
            return jsonify({
                'success': True,
                'text': combined_text,
                'pages': len(all_text)
            })
            
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'PyMuPDF not installed. Cannot process PDF files.'
            }), 500
            
    except Exception as e:
        logging.error(f"❌ PDF OCR error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages"""
    return jsonify({
        'languages': ['en', 'la'],
        'features': ['math_symbols', 'greek_letters', 'latin_characters'],
        'note': 'Optimized for mathematical expressions and educational content'
    })

if __name__ == '__main__':
    # For development only
    app.run(host='0.0.0.0', port=8000, debug=False)
