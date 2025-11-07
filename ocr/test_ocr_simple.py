"""
Simple OCR Test Script
Tests EasyOCR on a sample image
"""

import sys
import os
from PIL import Image
import numpy as np

def test_ocr(image_path=None):
    """Test OCR on an image"""
    
    print("=" * 60)
    print("Simple OCR Test")
    print("=" * 60)
    
    # Check if EasyOCR is installed
    try:
        import easyocr
        print(f"✅ EasyOCR version: {easyocr.__version__ if hasattr(easyocr, '__version__') else 'unknown'}")
    except ImportError:
        print("❌ EasyOCR not installed!")
        print("   Install with: pip install easyocr")
        return
    
    # Create or load image
    if image_path and os.path.exists(image_path):
        print(f"\n📄 Loading image: {image_path}")
        try:
            img = Image.open(image_path)
            print(f"   Image size: {img.size}")
            print(f"   Image mode: {img.mode}")
        except Exception as e:
            print(f"❌ Failed to load image: {e}")
            return
    else:
        print("\n📄 No image provided, creating test image...")
        # Create a simple test image with text
        img = Image.new('RGB', (400, 100), color='white')
        print("   ℹ️  Created blank test image (400x100)")
        print("   Note: Blank images won't have text to extract")
        print("\n💡 Usage: python test_ocr_simple.py <image_path>")
    
    # Convert to numpy array
    img_np = np.array(img)
    
    # Initialize EasyOCR
    print("\n🔄 Initializing EasyOCR reader...")
    print("   (This may take 10-15 seconds on first run)")
    try:
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        print("   ✅ Reader initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize reader: {e}")
        return
    
    # Perform OCR
    print("\n🔍 Performing OCR...")
    try:
        results = reader.readtext(img_np)
        
        if not results:
            print("   ⚠️  No text detected in image")
            if not image_path:
                print("   (This is expected for a blank test image)")
        else:
            print(f"   ✅ Detected {len(results)} text region(s)")
            print("\n" + "=" * 60)
            print("Extracted Text:")
            print("=" * 60)
            
            for i, (bbox, text, confidence) in enumerate(results, 1):
                print(f"\n[{i}] Text: {text}")
                print(f"    Confidence: {confidence:.2%}")
                print(f"    Bounding box: {bbox}")
            
            # Combined text
            combined_text = ' '.join([text for (_, text, _) in results])
            print("\n" + "=" * 60)
            print("Combined Text:")
            print("=" * 60)
            print(combined_text)
            
            # Average confidence
            avg_conf = sum([conf for (_, _, conf) in results]) / len(results)
            print(f"\nAverage Confidence: {avg_conf:.2%}")
    
    except Exception as e:
        print(f"   ❌ OCR failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✅ OCR Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    # Get image path from command line argument
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    if image_path and not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        print("\nUsage: python test_ocr_simple.py <image_path>")
        sys.exit(1)
    
    test_ocr(image_path)
