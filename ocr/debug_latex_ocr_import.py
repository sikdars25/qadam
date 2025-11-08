#!/usr/bin/env python3
"""
Debug LaTeX-OCR import issues
"""

import sys
import os

def debug_imports():
    """Debug the import process"""
    print("🔍 Debugging LaTeX-OCR Import Issues")
    print("=" * 50)
    
    # Test 1: Direct pix2tex import
    print("Test 1: Direct pix2tex import")
    try:
        from pix2tex.cli import LatexOCR
        print("✅ pix2tex imported successfully")
        
        # Test initialization
        try:
            ocr = LatexOCR()
            print("✅ LatexOCR initialized successfully")
        except Exception as e:
            print(f"⚠️ LatexOCR initialization failed: {e}")
    except ImportError as e:
        print(f"❌ pix2tex import failed: {e}")
    
    # Test 2: Check integration module path
    print("\nTest 2: Integration module path")
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    ocr_dir = os.path.join(current_dir, 'ocr')
    print(f"OCR directory: {ocr_dir}")
    print(f"OCR directory exists: {os.path.exists(ocr_dir)}")
    
    integration_path = os.path.join(ocr_dir, 'latex_ocr_integration.py')
    print(f"Integration module path: {integration_path}")
    print(f"Integration module exists: {os.path.exists(integration_path)}")
    
    # Test 3: Add path and test import
    print("\nTest 3: Add path and test integration import")
    sys.path.insert(0, ocr_dir)
    print(f"Python path now includes: {ocr_dir}")
    
    try:
        import latex_ocr_integration
        print("✅ latex_ocr_integration imported successfully")
        
        # Test the integration
        from latex_ocr_integration import get_latex_ocr_integration
        integration = get_latex_ocr_integration()
        status = integration.get_engine_status()
        
        print("📊 OCR Engine Status:")
        for engine, available in status.items():
            icon = "✅" if available else "❌"
            print(f"  {icon} {engine}: {available}")
            
    except ImportError as e:
        print(f"❌ latex_ocr_integration import failed: {e}")
        import traceback
        traceback.print_exc()

def test_flask_app_import():
    """Test how Flask app imports the module"""
    print("\n🌐 Test 4: Flask app import simulation")
    print("-" * 40)
    
    # Change to the main directory (like Flask app would)
    original_cwd = os.getcwd()
    try:
        # Simulate Flask app running from main directory
        os.chdir('/opt/qadam-ocr')
        print(f"Changed to: {os.getcwd()}")
        
        # Add OCR directory to path (like app.py does)
        ocr_dir = '/opt/qadam-ocr/ocr'
        if ocr_dir not in sys.path:
            sys.path.insert(0, ocr_dir)
        
        print(f"Python path includes OCR dir: {ocr_dir in sys.path}")
        
        # Try the import like app.py does
        try:
            from latex_ocr_integration import get_latex_ocr_integration
            integration = get_latex_ocr_integration()
            status = integration.get_engine_status()
            
            print("📊 Flask-style OCR Engine Status:")
            for engine, available in status.items():
                icon = "✅" if available else "❌"
                print(f"  {icon} {engine}: {available}")
                
        except Exception as e:
            print(f"❌ Flask-style import failed: {e}")
            import traceback
            traceback.print_exc()
    
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    debug_imports()
    test_flask_app_import()
    
    print("\n" + "=" * 50)
    print("🔧 If LaTeX-OCR shows as unavailable:")
    print("1. Check that pix2tex is installed: pip list | grep pix2tex")
    print("2. Check Python path includes /opt/qadam-ocr/ocr")
    print("3. Restart Flask service: sudo systemctl restart qadam-ocr")
    print("4. Check service logs: sudo journalctl -u qadam-ocr -f")
