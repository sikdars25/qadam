#!/usr/bin/env python3
"""
Specialized processor for large mathematical symbols
Handles tall parentheses, brackets, and other large symbols
"""

import cv2
import numpy as np
from PIL import Image
import logging
import os

class LargeSymbolProcessor:
    """
    Specialized processor for large mathematical symbols
    Improves detection of tall parentheses, brackets, and delimiters
    """
    
    def __init__(self):
        self.large_symbol_patterns = [
            r'\\left\(', r'\\right\)',  # Large parentheses
            r'\\left\[', r'\\right\]',  # Large brackets
            r'\\left\{', r'\\right\}',  # Large braces
            r'\\left|', r'\\right|',    # Large vertical bars
            r'\\left\|', r'\\right\|',  # Large double bars
            r'\\left\langle', r'\\right\rangle',  # Angle brackets
        ]
    
    def preprocess_for_large_symbols(self, image_path):
        """
        Enhanced preprocessing for large mathematical symbols
        Uses Otsu thresholding, median blur, and border padding for better OCR
        Optimized for: integration, summation, large brackets, fractions, differentials
        """
        try:
            # Read image in grayscale for better mathematical symbol detection
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
            
            original_height, original_width = image.shape[:2]
            logging.info(f"📏 Original image size: {original_width}x{original_height}")
            logging.info(f"🔧 Applying enhanced preprocessing for large math symbols")
            
            # Step 1: Otsu's thresholding for optimal binarization
            # This automatically finds the best threshold value
            _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            logging.info(f"✅ Applied Otsu thresholding for optimal binarization")
            
            # Step 2: Median blur to reduce noise while preserving edges
            # Critical for large symbols like ∫, ∑, and tall brackets
            denoised = cv2.medianBlur(binary, 3)
            logging.info(f"✅ Applied median blur (kernel=3) for noise reduction")
            
            # Step 3: Add white border padding
            # Helps OCR engines detect symbols at image edges
            padded = cv2.copyMakeBorder(
                denoised, 
                10, 10, 10, 10,  # top, bottom, left, right padding
                cv2.BORDER_CONSTANT, 
                value=255  # White border
            )
            logging.info(f"✅ Added 10px white border padding")
            
            # Step 4: Morphological operations to connect broken symbol parts
            # Especially useful for large brackets and integration symbols
            kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
            connected = cv2.morphologyEx(padded, cv2.MORPH_CLOSE, kernel_vertical)
            logging.info(f"✅ Applied morphological closing for symbol connectivity")
            
            # Step 5: Enhance contrast with CLAHE (optional, for low-contrast images)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(connected)
            logging.info(f"✅ Applied CLAHE for contrast enhancement")
            
            # Step 6: Resize if too large (preserve aspect ratio for tall symbols)
            max_dimension = 2048  # Larger for complex mathematical expressions
            if max(original_height, original_width) > max_dimension:
                if original_height > original_width:  # Tall image (common for integrals)
                    scale = max_dimension / original_height
                else:  # Wide image
                    scale = max_dimension / original_width
                
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                enhanced = cv2.resize(enhanced, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                logging.info(f"📏 Resized for large symbols: {new_width}x{new_height}")
            
            # Step 7: Final sharpening to enhance symbol edges
            kernel_sharpen = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel_sharpen)
            logging.info(f"✅ Applied sharpening filter")
            
            # Convert grayscale to RGB for PIL compatibility
            rgb_image = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2RGB)
            
            # Convert to PIL
            pil_image = Image.fromarray(rgb_image)
            
            logging.info(f"✅ Preprocessing complete - optimized for large math symbols")
            return pil_image
            
        except Exception as e:
            logging.error(f"Error in large symbol preprocessing: {e}")
            return None
    
    def detect_large_symbols(self, image_path):
        """
        Detect if image contains large mathematical symbols
        """
        try:
            # Read image
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
            else:
                image = image_path
            
            if image is None:
                return False
            
            height, width = image.shape[:2]
            
            # Check aspect ratio - tall images likely have large symbols
            aspect_ratio = height / width
            if aspect_ratio > 2.0:  # Very tall image
                logging.info(f"📏 Tall image detected (aspect ratio: {aspect_ratio:.2f})")
                return True
            
            # Check for large vertical structures using edge detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours and check for tall, thin structures
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if h > 100 and w < 50 and h/w > 3:  # Tall and thin
                    logging.info(f"🔍 Large symbol structure detected: {w}x{h}")
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error detecting large symbols: {e}")
            return False
    
    def create_symbol_enhancement_layers(self, image):
        """
        Create multiple enhancement layers for better symbol detection
        """
        try:
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            layers = []
            
            # Layer 1: Original
            layers.append(image)
            
            # Layer 2: High contrast
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            high_contrast = cv2.convertScaleAbs(gray, alpha=2.0, beta=20)
            high_contrast_rgb = cv2.cvtColor(high_contrast, cv2.COLOR_GRAY2RGB)
            layers.append(high_contrast_rgb)
            
            # Layer 3: Edge enhanced
            edges = cv2.Canny(gray, 30, 100)
            edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            layers.append(edges_rgb)
            
            # Layer 4: Thickened symbols
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 4))
            thickened = cv2.dilate(gray, kernel, iterations=1)
            thickened_rgb = cv2.cvtColor(thickened, cv2.COLOR_GRAY2RGB)
            layers.append(thickened_rgb)
            
            return layers
            
        except Exception as e:
            logging.error(f"Error creating enhancement layers: {e}")
            return [image]
    
    def test_large_symbol_detection(self):
        """Test the large symbol detection capabilities"""
        
        print("🔍 Testing Large Symbol Detection")
        print("=" * 50)
        
        # Create a test image with large parentheses (simulated)
        test_image = np.ones((400, 200, 3), dtype=np.uint8) * 255
        
        # Draw large parentheses
        cv2.line(test_image, (50, 50), (30, 200), (0, 0, 0), 3)  # Left parenthesis
        cv2.line(test_image, (70, 50), (90, 200), (0, 0, 0), 3)  # Left parenthesis
        cv2.line(test_image, (150, 50), (130, 200), (0, 0, 0), 3)  # Right parenthesis
        cv2.line(test_image, (170, 50), (190, 200), (0, 0, 0), 3)  # Right parenthesis
        
        # Save test image
        test_path = "/tmp/test_large_symbols.png"
        cv2.imwrite(test_path, test_image)
        
        # Test detection
        processor = LargeSymbolProcessor()
        has_large_symbols = processor.detect_large_symbols(test_path)
        
        print(f"📊 Large symbol detection: {'✅ DETECTED' if has_large_symbols else '❌ NOT DETECTED'}")
        
        # Test preprocessing
        processed = processor.preprocess_for_large_symbols(test_path)
        if processed:
            print("✅ Large symbol preprocessing completed successfully")
        else:
            print("❌ Large symbol preprocessing failed")
        
        # Clean up
        if os.path.exists(test_path):
            os.remove(test_path)
        
        return has_large_symbols and processed is not None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🔧 Large Symbol Processor for Mathematical OCR")
    print("=" * 60)
    
    processor = LargeSymbolProcessor()
    
    # Test the processor
    test_passed = processor.test_large_symbol_detection()
    
    print(f"\n{'='*60}")
    print("📋 Large Symbol Processing Features:")
    print("  ✅ Enhanced contrast for tall symbols")
    print("  ✅ Adaptive thresholding")
    print("  ✅ Morphological operations")
    print("  ✅ Edge detection and enhancement")
    print("  ✅ Aspect ratio preservation")
    print("  ✅ Multiple enhancement layers")
    print("  ✅ Specialized for \\left(, \\right), etc.")
    
    print(f"\n🎯 Target Symbols:")
    for pattern in processor.large_symbol_patterns:
        print(f"  • {pattern}")
    
    if test_passed:
        print(f"\n🎉 Large symbol processor is ready!")
    else:
        print(f"\n⚠️ Large symbol processor needs refinement")
