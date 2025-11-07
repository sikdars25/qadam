"""
Check OCR Libraries Installation and Versions
Tests all major OCR libraries used in the project
"""

import sys
import importlib.util

def check_library(library_name, import_name=None):
    """Check if a library is installed and get its version"""
    if import_name is None:
        import_name = library_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {library_name:20s} - Version: {version}")
        return True
    except ImportError:
        print(f"❌ {library_name:20s} - NOT INSTALLED")
        return False
    except Exception as e:
        print(f"⚠️  {library_name:20s} - Error: {e}")
        return False

def test_easyocr():
    """Test EasyOCR functionality"""
    try:
        import easyocr
        print("\n📄 Testing EasyOCR initialization...")
        print("   Creating reader (this may take a moment)...")
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        print("   ✅ EasyOCR reader created successfully")
        return True
    except Exception as e:
        print(f"   ❌ EasyOCR test failed: {e}")
        return False

def test_image_processing():
    """Test image processing libraries"""
    try:
        from PIL import Image
        import numpy as np
        import io
        
        print("\n🖼️  Testing image processing...")
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='white')
        img_array = np.array(img)
        
        print(f"   ✅ PIL/Pillow: Can create images")
        print(f"   ✅ NumPy: Can convert to array (shape: {img_array.shape})")
        return True
    except Exception as e:
        print(f"   ❌ Image processing test failed: {e}")
        return False

def test_pdf_processing():
    """Test PDF processing library"""
    try:
        import fitz  # PyMuPDF
        print("\n📑 Testing PDF processing...")
        print(f"   ✅ PyMuPDF version: {fitz.version}")
        return True
    except Exception as e:
        print(f"   ❌ PDF processing test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("OCR Libraries Check")
    print("=" * 60)
    print(f"\nPython Version: {sys.version}")
    print(f"Python Path: {sys.executable}")
    print("\n" + "-" * 60)
    print("Core Libraries:")
    print("-" * 60)
    
    # Core OCR libraries
    libraries = [
        ('Flask', 'flask'),
        ('Flask-CORS', 'flask_cors'),
        ('EasyOCR', 'easyocr'),
        ('Pillow (PIL)', 'PIL'),
        ('NumPy', 'numpy'),
        ('OpenCV', 'cv2'),
        ('PyMuPDF', 'fitz'),
        ('PyTorch', 'torch'),
    ]
    
    installed_count = 0
    for lib_name, import_name in libraries:
        if check_library(lib_name, import_name):
            installed_count += 1
    
    print("\n" + "-" * 60)
    print(f"Summary: {installed_count}/{len(libraries)} libraries installed")
    print("-" * 60)
    
    # Run functionality tests
    if installed_count == len(libraries):
        print("\n" + "=" * 60)
        print("Running Functionality Tests")
        print("=" * 60)
        
        test_image_processing()
        test_pdf_processing()
        test_easyocr()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
    else:
        print("\n⚠️  Some libraries are missing. Install them with:")
        print("   pip install -r requirements.txt")
    
    print("\n💡 To test OCR on an actual image:")
    print("   python test_ocr_simple.py <image_path>")

if __name__ == "__main__":
    main()
