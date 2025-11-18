#!/usr/bin/env python3
"""
LaTeX-OCR Integration Module
Primary OCR engine for mathematical expressions with EasyOCR fallback
"""

import os
import logging
import numpy as np
from PIL import Image
import cv2
import re
import time
import threading

# Cross-platform timeout handling
class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

def run_with_timeout(func, args=(), kwargs={}, timeout_seconds=30):
    """
    Run a function with timeout using threading (cross-platform)
    """
    result_container = []
    exception_container = []
    
    def target():
        try:
            result = func(*args, **kwargs)
            result_container.append(result)
        except Exception as e:
            exception_container.append(e)
    
    # Create and start thread
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    
    # Wait for completion or timeout
    thread.join(timeout_seconds)
    
    if thread.is_alive():
        logging.error(f"❌ Function timed out after {timeout_seconds}s")
        raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
    
    # Check for exceptions
    if exception_container:
        raise exception_container[0]
    
    # Return result
    if result_container:
        return result_container[0]
    else:
        return None

# Try to import LaTeX-OCR
try:
    from pix2tex.cli import LatexOCR
    # Note: HuggingFaceModel import removed as it doesn't exist in current pix2tex version
    LATEX_OCR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LaTeX-OCR not available: {e}")
    LATEX_OCR_AVAILABLE = False

# Try to import EasyOCR as fallback
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"EasyOCR not available: {e}")
    EASYOCR_AVAILABLE = False

# Large symbol processing
try:
    from large_symbol_processor import LargeSymbolProcessor
    LARGE_SYMBOL_PROCESSOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Large symbol processor not available: {e}")
    LARGE_SYMBOL_PROCESSOR_AVAILABLE = False

class LatexOCRIntegration:
    """
    LaTeX-OCR integration with EasyOCR fallback
    Prioritizes mathematical expression detection
    """
    
    def __init__(self):
        self.latex_ocr = None
        self.easyocr_reader = None
        self.large_symbol_processor = None
        self.initialize_engines()
    
    def initialize_engines(self):
        """Initialize both OCR engines"""
        
        # Initialize LaTeX-OCR (primary)
        if LATEX_OCR_AVAILABLE:
            try:
                logging.info("🔍 Attempting to initialize LaTeX-OCR...")
                self.latex_ocr = LatexOCR()
                logging.info("✅ LaTeX-OCR initialized successfully")
            except Exception as e:
                logging.error(f"❌ Failed to initialize LaTeX-OCR: {e}")
                logging.error(f"LaTeX-OCR will be unavailable, using EasyOCR fallback")
                self.latex_ocr = None
        else:
            logging.warning("⚠️ LaTeX-OCR not available at import time")
        
        # Initialize EasyOCR (fallback)
        if EASYOCR_AVAILABLE:
            try:
                logging.info("🔍 Attempting to initialize EasyOCR...")
                self.easyocr_reader = easyocr.Reader(['en', 'la', 'fr', 'de'])
                logging.info("✅ EasyOCR initialized successfully as fallback")
            except Exception as e:
                logging.error(f"❌ Failed to initialize EasyOCR: {e}")
                self.easyocr_reader = None
        else:
            logging.warning("⚠️ EasyOCR not available at import time")
        
        # Initialize large symbol processor
        if LARGE_SYMBOL_PROCESSOR_AVAILABLE:
            try:
                logging.info("🔍 Initializing large symbol processor...")
                self.large_symbol_processor = LargeSymbolProcessor()
                logging.info("✅ Large symbol processor initialized successfully")
            except Exception as e:
                logging.error(f"❌ Failed to initialize large symbol processor: {e}")
                self.large_symbol_processor = None
        else:
            logging.warning("⚠️ Large symbol processor not available at import time")
    
    def preprocess_image_for_latex_ocr(self, image_path):
        """
        Preprocess image specifically for LaTeX-OCR
        """
        try:
            # Read image
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
            else:
                image = image_path
            
            if image is None:
                raise ValueError("Could not read image")
            
            # Convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Enhance for mathematical expressions
            # 1. Increase contrast
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            image = cv2.merge([l, a, b])
            image = cv2.cvtColor(image, cv2.COLOR_LAB2RGB)
            
            # 2. Denoise
            image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
            
            # 3. Sharpen
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            image = cv2.filter2D(image, -1, kernel)
            
            # Convert back to PIL
            pil_image = Image.fromarray(image)
            
            return pil_image
            
        except Exception as e:
            logging.error(f"Error preprocessing image for LaTeX-OCR: {e}")
            return None
    
    def detect_mathematical_content(self, image_path):
        """
        Detect if image contains primarily mathematical content (formulas/equations)
        Returns True only for pure math formulas, False for text with some math
        """
        try:
            # Quick check using EasyOCR if available
            if self.easyocr_reader:
                results = self.easyocr_reader.readtext(image_path, detail=1)
                
                if results:
                    # Extract text
                    text = ' '.join([result[1] for result in results])
                    total_chars = len(text)
                    
                    # If text is too long (>100 chars), it's likely a question, not pure math
                    if total_chars > 100:
                        logging.info(f"📝 Text length {total_chars} chars - likely a question, not pure math")
                        return False
                    
                    # Count words - if more than 10 words, it's likely text
                    word_count = len(text.split())
                    if word_count > 10:
                        logging.info(f"📝 Word count {word_count} - likely text with math, not pure math")
                        return False
                    
                    # Count mathematical symbols (strong indicators of pure math)
                    pure_math_indicators = [
                        r'[∫∑∏√∂∇±×÷≠≤≥∞]',  # Math symbols
                        r'\\frac|\\sqrt|\\int|\\sum|\\lim',  # LaTeX math commands
                        r'\^\{[^}]+\}',  # Complex superscripts
                        r'_\{[^}]+\}',  # Complex subscripts
                    ]
                    
                    math_symbol_count = 0
                    for indicator in pure_math_indicators:
                        math_symbol_count += len(re.findall(indicator, text, re.IGNORECASE))
                    
                    # If math symbols are more than 20% of content, it's pure math
                    if total_chars > 0 and (math_symbol_count / total_chars) > 0.2:
                        logging.info(f"🧮 High math symbol density - pure mathematical content")
                        return True
                    
                    logging.info(f"📝 Low math density - text question with some math")
                    return False
            
            # If EasyOCR not available, default to False (use EasyOCR for extraction)
            return False
            
        except Exception as e:
            logging.error(f"Error detecting mathematical content: {e}")
            return False  # Default to EasyOCR for better text recognition
    
    def extract_text_with_latex_ocr(self, image_path):
        """
        Extract text using LaTeX-OCR (primary engine) with timeout handling
        """
        if not self.latex_ocr:
            return None
        
        try:
            # Check if image contains large symbols and use specialized preprocessing
            if self.large_symbol_processor and self.large_symbol_processor.detect_large_symbols(image_path):
                logging.info("🔍 Large symbols detected - using specialized preprocessing")
                processed_image = self.large_symbol_processor.preprocess_for_large_symbols(image_path)
            else:
                # Use standard fast preprocessing
                processed_image = self.fast_preprocess_image_for_latex_ocr(image_path)
            
            if processed_image is None:
                return None
            
            # Use cross-platform timeout to prevent hanging
            timeout_seconds = 30  # 30 second timeout
            logging.info(f"🧮 Attempting LaTeX-OCR with {timeout_seconds}s timeout...")
            
            start_time = time.time()
            
            try:
                # Run LaTeX-OCR with timeout
                latex_result = run_with_timeout(
                    self.latex_ocr, 
                    args=(processed_image,), 
                    timeout_seconds=timeout_seconds
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                if latex_result and latex_result.strip():
                    logging.info(f"✅ LaTeX-OCR succeeded in {duration:.2f}s: {latex_result[:50]}...")
                    return latex_result
                else:
                    logging.warning(f"⚠️ LaTeX-OCR returned empty result in {duration:.2f}s")
                    return None
                    
            except TimeoutError as e:
                end_time = time.time()
                duration = end_time - start_time
                logging.error(f"❌ LaTeX-OCR timed out after {duration:.2f}s: {e}")
                return None
            
        except Exception as e:
            logging.error(f"Error with LaTeX-OCR: {e}")
            return None
    
    def fast_preprocess_image_for_latex_ocr(self, image_path):
        """
        Enhanced preprocessing for LaTeX-OCR with Otsu thresholding
        Optimized for mathematical symbols including large symbols
        """
        try:
            # Read image in grayscale
            if isinstance(image_path, str):
                image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            else:
                # Convert to grayscale if already loaded
                if len(image_path.shape) == 3:
                    image = cv2.cvtColor(image_path, cv2.COLOR_BGR2GRAY)
                else:
                    image = image_path
            
            if image is None:
                raise ValueError("Could not read image")
            
            height, width = image.shape[:2]
            logging.info(f"📏 Image size: {width}x{height}")
            
            # Step 1: Otsu's thresholding for optimal binarization
            _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Step 2: Median blur to reduce noise while preserving edges
            denoised = cv2.medianBlur(binary, 3)
            
            # Step 3: Add white border padding (helps with edge symbols)
            padded = cv2.copyMakeBorder(
                denoised, 
                10, 10, 10, 10,
                cv2.BORDER_CONSTANT, 
                value=255
            )
            
            # Step 4: Resize if needed (max 1536px for better quality)
            new_height, new_width = padded.shape[:2]
            if max(new_height, new_width) > 1536:
                scale = 1536 / max(new_height, new_width)
                new_width = int(new_width * scale)
                new_height = int(new_height * scale)
                padded = cv2.resize(padded, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                logging.info(f"📏 Resized to {new_width}x{new_height}")
            
            # Convert grayscale to RGB for PIL
            rgb_image = cv2.cvtColor(padded, cv2.COLOR_GRAY2RGB)
            
            # Convert to PIL
            pil_image = Image.fromarray(rgb_image)
            
            return pil_image
            
        except Exception as e:
            logging.error(f"Error in preprocessing for LaTeX-OCR: {e}")
            return None
    
    def extract_text_with_easyocr(self, image_path):
        """
        Extract text using EasyOCR (fallback engine)
        """
        if not self.easyocr_reader:
            return None
        
        try:
            # Use multi-language support for better symbol detection
            results = self.easyocr_reader.readtext(
                image_path, 
                detail=0,
                paragraph=True,
                width_ths=0.8,
                height_ths=0.8,
                x_ths=1,
                y_ths=0.5
            )
            
            if results:
                text = ' '.join(results)
                logging.info(f"EasyOCR result: {text}")
                return text
            
            return None
            
        except Exception as e:
            logging.error(f"Error with EasyOCR: {e}")
            return None
    
    def extract_text(self, image_path):
        """
        Extract text using LaTeX-OCR first, then EasyOCR as fallback
        Includes timeout handling and performance monitoring
        """
        start_time = time.time()
        logging.info("🔍 Starting text extraction with LaTeX-OCR priority")
        
        # Step 1: Detect if content is mathematical
        is_math = self.detect_mathematical_content(image_path)
        logging.info(f"📊 Mathematical content detected: {is_math}")
        
        # Step 2: Try LaTeX-OCR ONLY if content is pure mathematical
        if is_math and self.latex_ocr:
            logging.info("🧮 Pure math detected - trying LaTeX-OCR (primary engine)")
            latex_result = self.extract_text_with_latex_ocr(image_path)
            
            if latex_result and len(latex_result.strip()) > 0:
                end_time = time.time()
                duration = end_time - start_time
                logging.info(f"✅ LaTeX-OCR succeeded in {duration:.2f}s total")
                return {
                    'text': latex_result,
                    'engine': 'latex-ocr',
                    'confidence': 'high',
                    'is_mathematical': True,
                    'processing_time': duration
                }
            else:
                logging.info("⚠️ LaTeX-OCR failed or returned empty - falling back to EasyOCR")
        else:
            logging.info("📝 Text content detected - skipping LaTeX-OCR, using EasyOCR directly")
        
        # Step 3: Fallback to EasyOCR
        if self.easyocr_reader:
            logging.info("📝 Trying EasyOCR (fallback engine)")
            easyocr_result = self.extract_text_with_easyocr(image_path)
            
            if easyocr_result and len(easyocr_result.strip()) > 0:
                end_time = time.time()
                duration = end_time - start_time
                logging.info(f"✅ EasyOCR succeeded as fallback in {duration:.2f}s total")
                return {
                    'text': easyocr_result,
                    'engine': 'easyocr',
                    'confidence': 'medium',
                    'is_mathematical': is_math,
                    'processing_time': duration
                }
            else:
                logging.info("⚠️ EasyOCR also failed")
        
        # Step 4: Complete failure
        end_time = time.time()
        duration = end_time - start_time
        logging.error(f"❌ Both OCR engines failed after {duration:.2f}s")
        return {
            'text': '',
            'engine': 'none',
            'confidence': 'none',
            'is_mathematical': False,
            'processing_time': duration,
            'error': 'Both OCR engines failed or timed out'
        }
    
    def get_engine_status(self):
        """Get status of both OCR engines"""
        latex_available = LATEX_OCR_AVAILABLE and self.latex_ocr is not None
        easy_available = EASYOCR_AVAILABLE and self.easyocr_reader is not None
        
        # Add debug logging
        logging.info(f"🔍 Engine Status Debug:")
        logging.info(f"  LATEX_OCR_AVAILABLE: {LATEX_OCR_AVAILABLE}")
        logging.info(f"  self.latex_ocr is not None: {self.latex_ocr is not None}")
        logging.info(f"  EASYOCR_AVAILABLE: {EASYOCR_AVAILABLE}")
        logging.info(f"  self.easyocr_reader is not None: {self.easyocr_reader is not None}")
        
        return {
            'latex_ocr_available': latex_available,
            'easyocr_available': easy_available,
            'primary_engine': 'latex-ocr' if latex_available else 'easyocr',
            'fallback_engine': 'easyocr' if easy_available else 'none',
            'debug': {
                'latex_import_available': LATEX_OCR_AVAILABLE,
                'latex_initialized': self.latex_ocr is not None,
                'easyocr_import_available': EASYOCR_AVAILABLE,
                'easyocr_initialized': self.easyocr_reader is not None
            }
        }

# Global instance
latex_ocr_integration = None

def get_latex_ocr_integration():
    """Get or create global LaTeX-OCR integration instance"""
    global latex_ocr_integration
    if latex_ocr_integration is None:
        latex_ocr_integration = LatexOCRIntegration()
    return latex_ocr_integration

def post_process_latex_ocr_result(latex_result):
    """
    Post-process LaTeX-OCR result
    Uses latex_postprocessor to clean and correct LaTeX output
    """
    try:
        from latex_postprocessor import post_process_latex_ocr_result as process_latex
        processed = process_latex(latex_result)
        # Return the corrected text if available, otherwise cleaned latex
        return processed.get('corrected_text') or processed.get('cleaned_latex') or latex_result
    except ImportError:
        # If latex_postprocessor not available, return raw result
        import logging
        logging.warning("latex_postprocessor not available, returning raw result")
        return latex_result
    except Exception as e:
        # On any error, return the original result
        import logging
        logging.error(f"Error in post-processing: {e}")
        return latex_result

def extract_text_with_latex_priority(image_path):
    """
    Convenience function to extract text with LaTeX-OCR priority
    """
    integration = get_latex_ocr_integration()
    result = integration.extract_text(image_path)
    
    if result['engine'] == 'latex-ocr' and result['text']:
        result['text'] = post_process_latex_ocr_result(result['text'])
    
    return result

if __name__ == "__main__":
    # Test the LaTeX-OCR integration
    logging.basicConfig(level=logging.INFO)
    
    print("🧮 LaTeX-OCR Integration Test")
    print("=" * 50)
    
    integration = get_latex_ocr_integration()
    status = integration.get_engine_status()
    
    print("📊 Engine Status:")
    for engine, available in status.items():
        status_icon = "✅" if available else "❌"
        print(f"  {status_icon} {engine}: {available}")
    
    print("\n🎯 LaTeX-OCR is set as primary engine!")
    print("📝 EasyOCR is available as fallback")
    print("🚀 Ready for mathematical expression detection!")
