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
        Specialized preprocessing for images with large mathematical symbols
        """
        try:
            # Read image
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
            else:
                image = image_path
            
            if image is None:
                raise ValueError("Could not read image")
            
            original_height, original_width = image.shape[:2]
            logging.info(f"📏 Original image size: {original_width}x{original_height}")
            
            # Convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Step 1: Enhance contrast for better symbol detection
            # Use CLAHE for better local contrast
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            lab[:,:,0] = clahe.apply(lab[:,:,0])
            image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            # Step 2: Adaptive thresholding for symbol isolation
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            adaptive_thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Step 3: Morphological operations to connect symbol parts
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 8))
            morph = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
            
            # Step 4: Edge detection for symbol boundaries
            edges = cv2.Canny(morph, 50, 150)
            
            # Step 5: Dilate edges to make symbols more prominent
            kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            edges_dilated = cv2.dilate(edges, kernel_dilate, iterations=1)
            
            # Step 6: Combine processed image with original
            edges_colored = cv2.cvtColor(edges_dilated, cv2.COLOR_GRAY2RGB)
            enhanced = cv2.addWeighted(image, 0.7, edges_colored, 0.3, 0)
            
            # Step 7: Resize if too large (but preserve aspect ratio for tall symbols)
            max_dimension = 1536  # Increased for large symbols
            if max(original_height, original_width) > max_dimension:
                if original_height > original_width:  # Tall image
                    scale = max_dimension / original_height
                else:  # Wide image
                    scale = max_dimension / original_width
                
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                enhanced = cv2.resize(enhanced, (new_width, new_height), interpolation=cv2.INTER_AREA)
                logging.info(f"📏 Resized for large symbols: {new_width}x{new_height}")
            
            # Step 8: Final sharpening
            kernel_sharpen = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel_sharpen)
            
            # Convert to PIL
            pil_image = Image.fromarray(sharpened)
            
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
