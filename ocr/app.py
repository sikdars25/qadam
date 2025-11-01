"""
OCR Service - Flask Application
Direct Flask app without Azure Functions wrapper
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
import os
import tempfile
import base64
from typing import Optional
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
logging.basicConfig(level=logging.INFO)

# Initialize PaddleOCR (lazy loading)
ocr_engine = None

def get_ocr_engine():
    """Get or initialize PaddleOCR engine"""
    global ocr_engine
    if ocr_engine is None:
        try:
            from paddleocr import PaddleOCR
            logging.info("🔄 Initializing PaddleOCR...")
            ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang='en',
                use_gpu=False,
                show_log=False
            )
            logging.info("✅ PaddleOCR initialized successfully")
        except Exception as e:
            logging.error(f"❌ Failed to initialize PaddleOCR: {e}")
            raise
    return ocr_engine

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'service': 'Qadam OCR Service',
        'status': 'running',
        'version': '2.0',
        'endpoints': {
            'health': '/api/health',
            'extract_text': '/api/extract-text',
            'extract_with_boxes': '/api/extract-text-with-boxes',
            'extract_from_pdf': '/api/extract-from-pdf'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logging.info('Health check requested')
    
    # Check if PaddleOCR is installed
    paddleocr_installed = False
    paddleocr_version = None
    try:
        import paddleocr
        paddleocr_installed = True
        paddleocr_version = paddleocr.__version__ if hasattr(paddleocr, '__version__') else 'unknown'
    except ImportError:
        pass

    return jsonify({
        'status': 'healthy',
        'service': 'OCR Service (Flask on VM)',
        'ocr_engine': 'PaddleOCR',
        'paddleocr_installed': paddleocr_installed,
        'paddleocr_version': paddleocr_version,
        'python_version': os.sys.version
    })

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """
    Extract text from an image using PaddleOCR
    
    Request:
        - file: Image file (multipart/form-data)
        OR
        - image_base64: Base64 encoded image (JSON)
        - language: Optional language code (default: 'en')
    
    Response:
        {
            'success': True,
            'text': 'Extracted text...',
            'confidence': 0.95,
            'details': [...]
        }
    """
    try:
        logging.info("📥 Received OCR request")
        
        # Get language parameter
        language = request.form.get('language', 'en') if request.files else request.json.get('language', 'en') if request.json else 'en'
        
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
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(image_data)
            tmp_path = tmp_file.name
        
        try:
            # Initialize OCR engine
            ocr = get_ocr_engine()
            
            # Perform OCR
            logging.info(f"🔍 Running OCR with language: {language}")
            result = ocr.ocr(tmp_path, cls=True)
            
            # Process results
            if not result or not result[0]:
                return jsonify({
                    'success': True,
                    'text': '',
                    'confidence': 0.0,
                    'details': [],
                    'message': 'No text detected in image'
                })
            
            # Extract text and confidence
            texts = []
            confidences = []
            details = []
            
            for line in result[0]:
                box = line[0]  # Bounding box coordinates
                text_info = line[1]  # (text, confidence)
                text = text_info[0]
                confidence = text_info[1]
                
                texts.append(text)
                confidences.append(confidence)
                details.append({
                    'text': text,
                    'confidence': confidence,
                    'box': box
                })
            
            # Combine all text
            full_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            logging.info(f"✅ OCR completed: {len(texts)} lines detected")
            
            return jsonify({
                'success': True,
                'text': full_text,
                'confidence': avg_confidence,
                'details': details
            })
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logging.error(f"❌ OCR failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'text': ''
        }), 500

@app.route('/api/extract-text-with-boxes', methods=['POST'])
def extract_text_with_boxes():
    """Same as extract-text but returns detailed bounding box information"""
    return extract_text()

@app.route('/api/extract-from-pdf', methods=['POST'])
def extract_from_pdf():
    """
    Extract text from PDF using OCR
    
    Request:
        - file: PDF file (multipart/form-data)
        - language: Optional language code (default: 'en')
    
    Response:
        {
            'success': True,
            'text': 'Combined text from all pages...',
            'total_pages': 3,
            'pages': [...]
        }
    """
    try:
        logging.info("📥 Received PDF OCR request")
        
        # Get language parameter
        language = request.form.get('language', 'en')
        
        # Get PDF file
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No PDF file provided',
                'text': '',
                'pages': []
            }), 400
        
        pdf_file = request.files['file']
        pdf_data = pdf_file.read()
        logging.info(f"📄 Received PDF: {len(pdf_data)} bytes")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_data)
            tmp_pdf_path = tmp_file.name
        
        try:
            # Convert PDF to images
            import fitz  # PyMuPDF
            
            pdf_document = fitz.open(tmp_pdf_path)
            total_pages = len(pdf_document)
            logging.info(f"📄 PDF has {total_pages} pages")
            
            all_text = []
            pages_data = []
            
            # Initialize OCR engine
            ocr = get_ocr_engine()
            
            # Process each page
            for page_num in range(total_pages):
                page = pdf_document[page_num]
                
                # Convert page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_data = pix.tobytes("png")
                
                # Save page image to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_img:
                    tmp_img.write(img_data)
                    tmp_img_path = tmp_img.name
                
                try:
                    # Perform OCR on page
                    result = ocr.ocr(tmp_img_path, cls=True)
                    
                    if result and result[0]:
                        page_texts = [line[1][0] for line in result[0]]
                        page_text = ' '.join(page_texts)
                        all_text.append(page_text)
                        
                        pages_data.append({
                            'page_number': page_num + 1,
                            'text': page_text,
                            'line_count': len(page_texts)
                        })
                    else:
                        pages_data.append({
                            'page_number': page_num + 1,
                            'text': '',
                            'line_count': 0
                        })
                
                finally:
                    if os.path.exists(tmp_img_path):
                        os.unlink(tmp_img_path)
            
            pdf_document.close()
            
            combined_text = '\n\n'.join(all_text)
            logging.info(f"✅ PDF OCR completed: {total_pages} pages processed")
            
            return jsonify({
                'success': True,
                'text': combined_text,
                'total_pages': total_pages,
                'pages': pages_data
            })
        
        finally:
            # Clean up temp PDF
            if os.path.exists(tmp_pdf_path):
                os.unlink(tmp_pdf_path)
    
    except Exception as e:
        logging.error(f"❌ PDF OCR failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'text': '',
            'pages': []
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
