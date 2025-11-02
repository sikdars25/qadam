"""
OCR Service using EasyOCR
Provides text extraction from images and PDFs
"""

from flask import Flask, request, jsonify
import easyocr
import base64
import io
from PIL import Image
import numpy as np
import os

app = Flask(__name__)

# Initialize EasyOCR reader (English by default)
# This will download models on first run (~100MB)
print("🔄 Initializing EasyOCR...")
reader = easyocr.Reader(['en'], gpu=False)
print("✅ EasyOCR initialized")

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'OCR',
        'engine': 'EasyOCR',
        'version': '1.0.0',
        'languages': ['en']
    })

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """
    Extract text from image using EasyOCR
    
    Request body:
    {
        "image_base64": "base64_encoded_image",
        "language": "en"  # optional, default: en
    }
    
    Or multipart/form-data with 'file' field
    """
    try:
        # Get image from request
        if request.is_json:
            data = request.get_json()
            image_base64 = data.get('image_base64')
            
            if not image_base64:
                return jsonify({'error': 'No image_base64 provided'}), 400
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))
            
        elif 'file' in request.files:
            file = request.files['file']
            image = Image.open(file.stream)
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        # Convert PIL Image to numpy array for EasyOCR
        image_np = np.array(image)
        
        # Perform OCR
        print("🔍 Performing OCR...")
        results = reader.readtext(image_np)
        
        # Extract text from results
        # EasyOCR returns: [(bbox, text, confidence), ...]
        extracted_text = ' '.join([text for (bbox, text, conf) in results])
        
        print(f"✅ OCR completed: {len(extracted_text)} characters")
        
        return jsonify({
            'success': True,
            'text': extracted_text,
            'confidence': sum([conf for (_, _, conf) in results]) / len(results) if results else 0,
            'details': [
                {
                    'text': text,
                    'confidence': float(conf),
                    'bbox': bbox
                }
                for (bbox, text, conf) in results
            ]
        })
        
    except Exception as e:
        print(f"❌ OCR error: {e}")
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
    
    Multipart/form-data with 'file' field
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # For PDF, we'll need to convert pages to images first
        # This requires pdf2image or PyMuPDF
        try:
            import fitz  # PyMuPDF
            
            # Read PDF
            pdf_bytes = file.read()
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            all_text = []
            
            # Process each page
            for page_num in range(len(pdf_document)):
                print(f"🔍 Processing page {page_num + 1}/{len(pdf_document)}")
                page = pdf_document[page_num]
                
                # Convert page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                image_np = np.array(image)
                
                # Perform OCR
                results = reader.readtext(image_np)
                page_text = ' '.join([text for (bbox, text, conf) in results])
                all_text.append(page_text)
            
            pdf_document.close()
            
            combined_text = '\n\n'.join(all_text)
            
            print(f"✅ PDF OCR completed: {len(combined_text)} characters")
            
            return jsonify({
                'success': True,
                'text': combined_text,
                'pages': len(all_text)
            })
            
        except ImportError:
            return jsonify({
                'error': 'PyMuPDF not installed. Cannot process PDF files.'
            }), 500
            
    except Exception as e:
        print(f"❌ PDF OCR error: {e}")
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
        'languages': ['en'],
        'note': 'To add more languages, update the EasyOCR Reader initialization'
    })

if __name__ == '__main__':
    # For development only
    app.run(host='0.0.0.0', port=8000, debug=False)
