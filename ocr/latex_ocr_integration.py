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

class LatexOCRIntegration:
    """
    LaTeX-OCR integration with EasyOCR fallback
    Prioritizes mathematical expression detection
    """
    
    def __init__(self):
        self.latex_ocr = None
        self.easyocr_reader = None
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
        Detect if image contains mathematical content
        """
        try:
            # Use EasyOCR for quick content detection
            if self.easyocr_reader:
                if isinstance(image_path, str):
                    image = cv2.imread(image_path)
                else:
                    image = image_path
                
                if image is not None:
                    # Quick OCR to detect math indicators
                    result = self.easyocr_reader.readtext(image, detail=0)
                    text = ' '.join(result)
                    
                    # Check for mathematical indicators
                    math_indicators = [
                        r'[=+\-*/]', r'\^', r'_', r'\{', r'\}', r'\[', r'\]',
                        r'\\frac', r'\\sqrt', r'\\int', r'\\sum', r'\\prod',
                        r'alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|tau|phi|omega',
                        r'sin|cos|tan|log|ln|exp|integral|derivative'
                    ]
                    
                    for indicator in math_indicators:
                        if re.search(indicator, text, re.IGNORECASE):
                            return True
            
            return False  # Assume non-mathematical if detection fails
            
        except Exception as e:
            logging.error(f"Error detecting mathematical content: {e}")
            return True  # Default to trying LaTeX-OCR
    
    def extract_text_with_latex_ocr(self, image_path):
        """
        Extract text using LaTeX-OCR (primary engine)
        """
        if not self.latex_ocr:
            return None
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image_for_latex_ocr(image_path)
            if processed_image is None:
                return None
            
            # Extract LaTeX using LaTeX-OCR
            latex_result = self.latex_ocr(processed_image)
            
            if latex_result and latex_result.strip():
                logging.info(f"LaTeX-OCR result: {latex_result}")
                return latex_result
            
            return None
            
        except Exception as e:
            logging.error(f"Error with LaTeX-OCR: {e}")
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
        """
        logging.info("🔍 Starting text extraction with LaTeX-OCR priority")
        
        # Step 1: Detect if content is mathematical
        is_math = self.detect_mathematical_content(image_path)
        logging.info(f"📊 Mathematical content detected: {is_math}")
        
        # Step 2: Try LaTeX-OCR first (especially for mathematical content)
        if is_math or self.latex_ocr:
            logging.info("🧮 Trying LaTeX-OCR (primary engine)")
            latex_result = self.extract_text_with_latex_ocr(image_path)
            
            if latex_result and len(latex_result.strip()) > 0:
                logging.info("✅ LaTeX-OCR succeeded")
                return {
                    'text': latex_result,
                    'engine': 'latex-ocr',
                    'confidence': 'high',
                    'is_mathematical': True
                }
            else:
                logging.info("⚠️ LaTeX-OCR failed or returned empty")
        
        # Step 3: Fallback to EasyOCR
        if self.easyocr_reader:
            logging.info("📝 Trying EasyOCR (fallback engine)")
            easyocr_result = self.extract_text_with_easyocr(image_path)
            
            if easyocr_result and len(easyocr_result.strip()) > 0:
                logging.info("✅ EasyOCR succeeded as fallback")
                return {
                    'text': easyocr_result,
                    'engine': 'easyocr',
                    'confidence': 'medium',
                    'is_mathematical': is_math
                }
            else:
                logging.info("⚠️ EasyOCR also failed")
        
        # Step 4: Complete failure
        logging.error("❌ Both OCR engines failed")
        return {
            'text': '',
            'engine': 'none',
            'confidence': 'none',
            'is_mathematical': False
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

def extract_text_with_latex_priority(image_path):
    """
    Convenience function to extract text with LaTeX-OCR priority
    """
    integration = get_latex_ocr_integration()
    return integration.extract_text(image_path)

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
