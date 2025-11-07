#!/usr/bin/env python3
"""
Test enhanced OCR for mathematical symbol detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_ocr_reader, preprocess_image, correct_math_symbols
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def create_math_test_image():
    """Create a test image with mathematical symbols"""
    
    # Create a white image
    img = Image.new('RGB', (800, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font that supports math symbols
    try:
        # Try to find a font that supports mathematical symbols
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
    
    # Draw the mathematical expression
    text = "current density [j = α E], where [α = (ne²/m) τ]"
    draw.text((50, 50), text, fill='black', font=font)
    
    # Save the image
    img.save("test_math_expression.png")
    return img

def create_vector_test_image():
    """Create a test image with vector arrows"""
    
    # Create a white image
    img = Image.new('RGB', (800, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font that supports math symbols
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
    
    # Draw the vector expression
    text = "current density [→j = α →E], where [α = (ne²/m) τ]"
    draw.text((50, 50), text, fill='black', font=font)
    
    # Save the image
    img.save("test_vector_expression.png")
    return img

def test_enhanced_ocr():
    """Test the enhanced OCR with mathematical symbols"""
    
    print("🧪 Testing Enhanced OCR for Mathematical Symbols")
    print("=" * 60)
    
    try:
        # Initialize OCR reader
        print("📄 Initializing enhanced OCR reader...")
        reader = get_ocr_reader()
        
        # Test 1: Basic math symbols
        print("\n📊 Test 1: Basic Mathematical Symbols")
        print("-" * 40)
        
        img1 = create_math_test_image()
        # Convert PIL image to bytes properly
        import io
        img_bytes = io.BytesIO()
        img1.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        img1_preprocessed = preprocess_image(img_bytes.getvalue())
        
        if img1_preprocessed is not None:
            results1 = reader.readtext(
                img1_preprocessed,
                detail=1,
                paragraph=False,
                min_size=8,
                text_threshold=0.5,
                low_text=0.2,
                contrast_ths=0.3,
                adjust_contrast=0.7,
                add_margin=0.1
            )
            
            raw_text1 = ' '.join([text for (bbox, text, conf) in results1])
            corrected_text1 = correct_math_symbols(raw_text1)
            
            print(f"📝 Raw OCR:      {raw_text1}")
            print(f"✅ Corrected:    {corrected_text1}")
            
            # Check for key symbols
            has_alpha = 'α' in corrected_text1
            has_tau = 'τ' in corrected_text1
            has_fraction = '/' in corrected_text1
            has_power = '²' in corrected_text1
            
            print(f"🔍 Symbol Detection:")
            print(f"   Alpha (α):     {'✅' if has_alpha else '❌'}")
            print(f"   Tau (τ):       {'✅' if has_tau else '❌'}")
            print(f"   Fraction (/):  {'✅' if has_fraction else '❌'}")
            print(f"   Power (²):     {'✅' if has_power else '❌'}")
        
        # Test 2: Vector arrows
        print("\n📊 Test 2: Vector Arrow Detection")
        print("-" * 40)
        
        img2 = create_vector_test_image()
        # Convert PIL image to bytes properly
        img_bytes2 = io.BytesIO()
        img2.save(img_bytes2, format='PNG')
        img_bytes2.seek(0)
        
        img2_preprocessed = preprocess_image(img_bytes2.getvalue())
        
        if img2_preprocessed is not None:
            results2 = reader.readtext(
                img2_preprocessed,
                detail=1,
                paragraph=False,
                min_size=8,
                text_threshold=0.5,
                low_text=0.2,
                contrast_ths=0.3,
                adjust_contrast=0.7,
                add_margin=0.1
            )
            
            raw_text2 = ' '.join([text for (bbox, text, conf) in results2])
            corrected_text2 = correct_math_symbols(raw_text2)
            
            print(f"📝 Raw OCR:      {raw_text2}")
            print(f"✅ Corrected:    {corrected_text2}")
            
            # Check for vector arrows
            has_vector_j = '→j' in corrected_text2
            has_vector_E = '→E' in corrected_text2
            
            print(f"🔍 Vector Detection:")
            print(f"   Vector j (→j):  {'✅' if has_vector_j else '❌'}")
            print(f"   Vector E (→E):  {'✅' if has_vector_E else '❌'}")
        
        print("\n🎉 Enhanced OCR testing completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_enhanced_ocr()
    if not success:
        sys.exit(1)
