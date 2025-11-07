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
import re
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

def correct_math_symbols(text):
    """
    Correct common OCR detection errors for mathematical symbols and expressions
    
    Issues addressed:
    1. τ (tau) detected as T
    2. Vector arrows (→) not detected above letters
    3. Single letter with prefix/suffix split incorrectly
    4. Power digits (exponential) not detected correctly
    5. Expressions in parentheses/brackets not detected correctly
    """
    if not text:
        return text
    
    corrected_text = text
    corrections_made = []
    
    # 1. Fix τ (tau) detection issues
    tau_corrections = [
        # Common contexts where τ is misdetected as T
        (r'\btorque\s+T\b', 'torque τ'),
        (r'\bshear\s+stress\s+T\b', 'shear stress τ'),
        (r'\btime\s+constant\s+T\b', 'time constant τ'),
        (r'\bangular\s+period\s+T\b', 'angular period τ'),
        (r'\bT\s+(constant|period|torque)\b', r'τ \1'),
        # Direct T to τ in math contexts
        (r'([=+\-*/(])T([a-zA-Z])', r'\1τ\2'),
        (r'([a-zA-Z])T([=+\-*/)])', r'\1τ\2'),
        # Handle T between variables
        (r'([=+\-*/(])T\s+([a-zA-Z])', r'\1τ\2'),
        (r'([a-zA-Z])\s+T([=+\-*/)])', r'\1τ\2'),
    ]
    
    for pattern, replacement in tau_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append(f"T → τ")
    
    # 2. Fix vector arrow detection
    vector_corrections = [
        # Common vector notations that get split - be more specific
        (r'\bvec\s+([a-zA-Z])\b', r'→\1'),  # vec a → →a
        (r'\b([a-zA-Z])\s+vec\b(?!\s+vec)', r'\1→'),  # a vec → a→ (not if followed by another vec)
        (r'\b([a-zA-Z])\s+vector\b', r'\1→'),  # a vector → a→
        (r'\bvector\s+([a-zA-Z])\b', r'→\1'),  # vector a → →a
        # Arrow combinations
        (r'->\s*([a-zA-Z])', r'→\1'),  # -> a → →a
        (r'([a-zA-Z])\s*->', r'\1→'),  # a -> → a→
    ]
    
    for pattern, replacement in vector_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("vector arrow fixed")
    
    # 3. Fix single letter with prefix/suffix splitting
    # Combine common math notation that gets incorrectly split
    combination_corrections = [
        # Greek letters with subscripts/superscripts - be more specific
        (r'λ\s+n\b', 'λn'),
        (r'λ\s+p\b', 'λp'),
        (r'α\s+n\b', 'αn'),
        (r'β\s+n\b', 'βn'),
        (r'θ\s+n\b', 'θn'),
        (r'μ\s+0\b', 'μ₀'),
        (r'σ\s+2\b', 'σ²'),
        # Variables with subscripts - be more specific to avoid power conflicts
        (r'([a-zA-Z])\s+(\d+)\b', r'\1\2'),  # a 1 → a1 (only at word boundary)
        (r'([a-zA-Z])\s+_(\d+)', r'\1_\2'),  # a _1 → a_1
        # Function notation
        (r'f\s*\(\s*x\s*\)', 'f(x)'),  # f ( x ) → f(x)
        (r'g\s*\(\s*x\s*\)', 'g(x)'),
        (r'sin\s*\(\s*x\s*\)', 'sin(x)'),
        (r'cos\s*\(\s*x\s*\)', 'cos(x)'),
        (r'tan\s*\(\s*x\s*\)', 'tan(x)'),
        (r'log\s*\(\s*x\s*\)', 'log(x)'),
        (r'ln\s*\(\s*x\s*\)', 'ln(x)'),
    ]
    
    for pattern, replacement in combination_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("combined split characters")
    
    # 4. Fix power digits and exponentials - fix negative exponent issue
    power_corrections = [
        # Superscript patterns - fix negative exponent issue
        (r'\^\s*-(\d+)', r'^-\1'),  # ^ -2 → ^-2
        (r'\^\s*(\d+)', r'^\1'),  # ^ 2 → ^2
        (r'([a-zA-Z])\s*\^\s*-(\d+)', r'\1^-\2'),  # x ^ -2 → x^-2
        (r'([a-zA-Z])\s*\^\s*(\d+)', r'\1^\2'),  # x ^ 2 → x^2
        # Only apply x2 → x^2 for common variables, not all letters
        (r'([xyze])\s*(\d+)\b', r'\1^\2'),  # x2 → x^2, y3 → y^3, etc.
        (r'e\s*\^\s*-(\d+)', r'e^-\1'),  # e ^ -2 → e^-2
        (r'e\s*\^\s*(\d+)', r'e^\1'),  # e ^ 2 → e^2
        (r'10\s*\^\s*-(\d+)', r'10^-\1'),  # 10 ^ -2 → 10^-2
        (r'10\s*\^\s*(\d+)', r'10^\1'),  # 10 ^ 2 → 10^2
    ]
    
    for pattern, replacement in power_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("power/exponential fixed")
    
    # 5. Scientific notation - apply after power corrections
    scientific_corrections = [
        # Scientific notation - be more specific, avoid conflicts with power corrections
        (r'(\d+\.\d+)\s+e\s+(\d+)(?!\s*\w)', r'\1e\2'),  # 1.2 e 3 → 1.2e3
        (r'(\d+\.\d+)\s+e\s+-(\d+)(?!\s*\w)', r'\1e-\2'),  # 1.2 e -3 → 1.2e-3
        (r'(\d+)\s+e\s+(\d+)(?!\s*\w)', r'\1e\2'),  # 1 e 3 → 1e3
        (r'(\d+)\s+e\s+-(\d+)(?!\s*\w)', r'\1e-\2'),  # 1 e -3 → 1e-3
    ]
    
    for pattern, replacement in scientific_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("scientific notation fixed")
    
    # 5. Fix parentheses and brackets expressions
    bracket_corrections = [
        # Fix spacing in mathematical expressions
        (r'\(\s*([^)]+?)\s*\)', r'(\1)'),  # ( x + y ) → (x+y)
        (r'\[\s*([^\]]+?)\s*\]', r'[\1]'),  # [ x + y ] → [x+y]
        (r'\{\s*([^}]+?)\s*\}', r'{\1}'),  # { x + y } → {x+y}
        # Remove extra spaces around operators in parentheses
        (r'\(\s*([^)]+?)\s*\+\s*([^)]+?)\s*\)', r'(\1+\2)'),  # ( a + b ) → (a+b)
        (r'\(\s*([^)]+?)\s*\-\s*([^)]+?)\s*\)', r'(\1-\2)'),  # ( a - b ) → (a-b)
        (r'\(\s*([^)]+?)\s*\*\s*([^)]+?)\s*\)', r'(\1*\2)'),  # ( a * b ) → (a*b)
        (r'\(\s*([^)]+?)\s*\/\s*([^)]+?)\s*\)', r'(\1/\2)'),  # ( a / b ) → (a/b)
        # Similar for brackets
        (r'\[\s*([^\]]+?)\s*\+\s*([^\]]+?)\s*\]', r'[\1+\2]'),  # [ a + b ] → [a+b]
        (r'\[\s*([^\]]+?)\s*\-\s*([^\]]+?)\s*\]', r'[\1-\2]'),  # [ a - b ] → [a-b]
        (r'\{\s*([^}]+?)\s*\+\s*([^}]+?)\s*\}', r'{\1+\2}'),  # { a + b } → {a+b}
        (r'\{\s*([^}]+?)\s*\-\s*([^}]+?)\s*\}', r'{\1-\2}'),  # { a - b } → {a-b}
    ]
    
    for pattern, replacement in bracket_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("parentheses/brackets fixed")
    
    # Log corrections for debugging
    if corrections_made:
        logging.info(f"🔧 Math symbol corrections applied: {', '.join(set(corrections_made))}")
    
    return corrected_text

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
            'latin_language_support',
            'math_corrections',
            'tau_detection',
            'vector_arrows',
            'power_exponentials',
            'parentheses_brackets'
        ],
        'supported_corrections': [
            'τ (tau) detection',
            'Vector arrows (→)',
            'Combined characters (λn, λp)',
            'Power/exponential notation',
            'Parentheses/brackets cleanup'
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
        raw_text = ' '.join([text for (bbox, text, conf) in results])
        avg_confidence = sum([conf for (_, _, conf) in results]) / len(results) if results else 0
        
        # Apply mathematical symbol and expression corrections
        corrected_text = correct_math_symbols(raw_text)
        
        logging.info(f"✅ OCR completed: {len(corrected_text)} characters, confidence: {avg_confidence:.2f}")
        
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
            'text': corrected_text,
            'raw_text': raw_text,  # Include original for debugging
            'confidence': float(avg_confidence),
            'corrections_applied': corrected_text != raw_text,
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
