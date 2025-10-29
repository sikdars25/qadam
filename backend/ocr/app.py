"""
OCR Function App - Separate Azure Function for OCR Processing
Uses PaddleOCR for better accuracy and no system dependencies
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import tempfile
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
CORS(app, resources={
    r"/api/*": {
        "origins": [FRONTEND_URL, "https://*.azurestaticapps.net"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize PaddleOCR (lazy loading)
ocr_engine = None

def get_ocr_engine():
    """Get or initialize PaddleOCR engine"""
    global ocr_engine
    if ocr_engine is None:
        try:
            from paddleocr import PaddleOCR
            print("🔄 Initializing PaddleOCR...")
            ocr_engine = PaddleOCR(
                use_angle_cls=True,  # Enable text angle classification
                lang='en',  # Default to English
                use_gpu=False,  # CPU only (Azure doesn't provide GPU)
                show_log=False  # Reduce logging
            )
            print("✅ PaddleOCR initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize PaddleOCR: {e}")
            raise
    return ocr_engine

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'OCR Function App',
        'ocr_engine': 'PaddleOCR'
    })

@app.route('/api/ocr/image', methods=['POST'])
def ocr_image():
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
    try:
        ocr = get_ocr_engine()
        
        # Get language parameter
        lang = request.form.get('language', 'en') if request.files else request.json.get('language', 'en')
        
        # Get image from request
        image_path = None
        temp_file = None
        
        if 'file' in request.files:
            # File upload
            file = request.files['file']
            
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            file.save(temp_file.name)
            image_path = temp_file.name
            temp_file.close()
            
        elif request.json and 'image_base64' in request.json:
            # Base64 encoded image
            image_data = base64.b64decode(request.json['image_base64'])
            
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_file.write(image_data)
            temp_file.close()
            image_path = temp_file.name
            
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        # Perform OCR
        print(f"🔍 Performing OCR on image (language: {lang})...")
        result = ocr.ocr(image_path, cls=True)
        
        # Clean up temp file
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        
        # Parse results
        if not result or not result[0]:
            return jsonify({
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
        
        print(f"✅ OCR completed: {len(text_lines)} lines detected")
        
        return jsonify({
            'success': True,
            'text': full_text,
            'confidence': round(avg_confidence, 3),
            'lines_detected': len(text_lines),
            'details': details
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ocr/pdf', methods=['POST'])
def ocr_pdf():
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
    try:
        import fitz  # PyMuPDF
        from PIL import Image
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        lang = request.form.get('language', 'en')
        
        # Save PDF to temp file
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        file.save(temp_pdf.name)
        temp_pdf.close()
        
        # Open PDF
        doc = fitz.open(temp_pdf.name)
        
        ocr = get_ocr_engine()
        pages_text = []
        
        print(f"📄 Processing {len(doc)} pages...")
        
        for page_num, page in enumerate(doc, 1):
            print(f"  Processing page {page_num}/{len(doc)}...")
            
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
        
        print(f"✅ PDF OCR completed: {len(doc)} pages processed")
        
        return jsonify({
            'success': True,
            'text': full_text,
            'total_pages': len(pages_text),
            'pages': pages_text
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ocr/languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported languages"""
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
    
    return jsonify({
        'success': True,
        'languages': languages
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
