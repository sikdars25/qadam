"""
OCR Function App - Native Azure Functions
Uses PaddleOCR for better accuracy and no system dependencies
"""

import azure.functions as func
import logging
import json
import os
import tempfile
import base64
from typing import Optional

# Create the function app
app = func.FunctionApp()

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
                use_angle_cls=True,  # Enable text angle classification
                lang='en',  # Default to English
                use_gpu=False,  # CPU only (Azure doesn't provide GPU)
                show_log=False  # Reduce logging
            )
            logging.info("✅ PaddleOCR initialized successfully")
        except Exception as e:
            logging.error(f"❌ Failed to initialize PaddleOCR: {e}")
            raise
    return ocr_engine

def create_cors_response(body: dict, status_code: int = 200) -> func.HttpResponse:
    """Create HTTP response with CORS headers"""
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    return func.HttpResponse(
        body=json.dumps(body),
        status_code=status_code,
        headers=headers,
        mimetype='application/json'
    )

@app.route(route="health", methods=["GET", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    logging.info('Health check requested')
    
    # Handle OPTIONS for CORS preflight
    if req.method == "OPTIONS":
        return create_cors_response({})
    
    # Check if PaddleOCR is installed
    paddleocr_installed = False
    paddleocr_version = None
    try:
        import paddleocr
        paddleocr_installed = True
        paddleocr_version = paddleocr.__version__ if hasattr(paddleocr, '__version__') else 'unknown'
    except ImportError:
        pass
    
    return create_cors_response({
        'status': 'healthy',
        'service': 'OCR Function App',
        'ocr_engine': 'PaddleOCR',
        'paddleocr_installed': paddleocr_installed,
        'paddleocr_version': paddleocr_version,
        'python_version': os.sys.version
    })

@app.route(route="ocr/image", methods=["POST", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def ocr_image(req: func.HttpRequest) -> func.HttpResponse:
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
            'details': [...]  # Detailed OCR results with bounding boxes
        }
    """
    logging.info('OCR image request received')
    
    # Handle OPTIONS for CORS preflight
    if req.method == "OPTIONS":
        return create_cors_response({})
    
    try:
        ocr = get_ocr_engine()
        
        # Get language parameter
        lang = 'en'
        image_path = None
        
        # Check if it's a file upload or JSON request
        content_type = req.headers.get('Content-Type', '')
        
        if 'multipart/form-data' in content_type:
            # File upload
            try:
                files = req.files
                if 'file' in files:
                    file = files['file']
                    
                    # Get language from form
                    params = req.params
                    lang = params.get('language', 'en')
                    
                    # Save to temp file
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    temp_file.write(file.read())
                    temp_file.close()
                    image_path = temp_file.name
                else:
                    return create_cors_response({'error': 'No file provided'}, 400)
            except Exception as e:
                logging.error(f"Error processing file upload: {e}")
                return create_cors_response({'error': f'File upload error: {str(e)}'}, 400)
        else:
            # JSON request with base64
            try:
                req_body = req.get_json()
                if 'image_base64' in req_body:
                    lang = req_body.get('language', 'en')
                    image_data = base64.b64decode(req_body['image_base64'])
                    
                    # Save to temp file
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    temp_file.write(image_data)
                    temp_file.close()
                    image_path = temp_file.name
                else:
                    return create_cors_response({'error': 'No image_base64 provided'}, 400)
            except ValueError:
                return create_cors_response({'error': 'Invalid JSON body'}, 400)
        
        if not image_path:
            return create_cors_response({'error': 'No image provided'}, 400)
        
        # Perform OCR
        logging.info(f"🔍 Performing OCR on image (language: {lang})...")
        result = ocr.ocr(image_path, cls=True)
        
        # Clean up temp file
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        
        # Parse results
        if not result or not result[0]:
            return create_cors_response({
                'success': True,
                'text': '',
                'confidence': 0.0,
                'details': [],
                'message': 'No text detected in image'
            })
        
        # Extract text and confidence
        text_lines = []
        details = []
        total_confidence = 0
        
        for line in result[0]:
            bbox = line[0]  # Bounding box coordinates
            text = line[1][0]  # Extracted text
            confidence = line[1][1]  # Confidence score
            
            text_lines.append(text)
            total_confidence += confidence
            
            details.append({
                'text': text,
                'confidence': round(confidence, 3),
                'bbox': bbox
            })
        
        # Combine all text
        full_text = '\n'.join(text_lines)
        avg_confidence = total_confidence / len(result[0]) if result[0] else 0
        
        logging.info(f"✅ OCR completed: {len(text_lines)} lines detected")
        
        return create_cors_response({
            'success': True,
            'text': full_text,
            'confidence': round(avg_confidence, 3),
            'lines_detected': len(text_lines),
            'details': details
        })
        
    except Exception as e:
        logging.error(f"OCR error: {str(e)}", exc_info=True)
        return create_cors_response({
            'success': False,
            'error': str(e)
        }, 500)

@app.route(route="ocr/pdf", methods=["POST", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def ocr_pdf(req: func.HttpRequest) -> func.HttpResponse:
    """
    Extract text from PDF using OCR
    
    Request:
        - file: PDF file (multipart/form-data)
        - language: Optional language code (default: 'en')
    
    Response:
        {
            'success': True,
            'text': 'Extracted text...',
            'pages': [...]  # Text per page
        }
    """
    logging.info('OCR PDF request received')
    
    # Handle OPTIONS for CORS preflight
    if req.method == "OPTIONS":
        return create_cors_response({})
    
    try:
        import fitz  # PyMuPDF
        
        content_type = req.headers.get('Content-Type', '')
        
        if 'multipart/form-data' not in content_type:
            return create_cors_response({'error': 'PDF must be uploaded as multipart/form-data'}, 400)
        
        files = req.files
        if 'file' not in files:
            return create_cors_response({'error': 'No file provided'}, 400)
        
        file = files['file']
        params = req.params
        lang = params.get('language', 'en')
        
        # Save PDF to temp file
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf.write(file.read())
        temp_pdf.close()
        
        # Open PDF
        doc = fitz.open(temp_pdf.name)
        
        ocr = get_ocr_engine()
        pages_text = []
        
        logging.info(f"📄 Processing {len(doc)} pages...")
        
        for page_num, page in enumerate(doc, 1):
            logging.info(f"  Processing page {page_num}/{len(doc)}...")
            
            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_data = pix.tobytes("png")
            
            # Save to temp file
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_img.write(img_data)
            temp_img.close()
            
            # Perform OCR
            result = ocr.ocr(temp_img.name, cls=True)
            
            # Extract text
            page_text = []
            if result and result[0]:
                for line in result[0]:
                    page_text.append(line[1][0])
            
            pages_text.append('\n'.join(page_text))
            
            # Clean up temp image
            os.remove(temp_img.name)
        
        # Clean up temp PDF
        doc.close()
        os.remove(temp_pdf.name)
        
        # Combine all pages
        full_text = '\n\n'.join(pages_text)
        
        logging.info(f"✅ PDF OCR completed: {len(doc)} pages processed")
        
        return create_cors_response({
            'success': True,
            'text': full_text,
            'total_pages': len(pages_text),
            'pages': pages_text
        })
        
    except Exception as e:
        logging.error(f"PDF OCR error: {str(e)}", exc_info=True)
        return create_cors_response({
            'success': False,
            'error': str(e)
        }, 500)

@app.route(route="ocr/languages", methods=["GET", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def get_supported_languages(req: func.HttpRequest) -> func.HttpResponse:
    """Get list of supported languages"""
    logging.info('Languages list requested')
    
    # Handle OPTIONS for CORS preflight
    if req.method == "OPTIONS":
        return create_cors_response({})
    
    languages = {
        'en': 'English',
        'ch': 'Chinese',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ka': 'Kannada',
        'hi': 'Hindi',
        'mr': 'Marathi',
        'ne': 'Nepali',
        'ur': 'Urdu',
        'ar': 'Arabic',
        'fr': 'French',
        'de': 'German',
        'es': 'Spanish',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean'
    }
    
    return create_cors_response({
        'success': True,
        'languages': languages
    })
