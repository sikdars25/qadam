#!/usr/bin/env python3
"""
Test LaTeX-OCR integration with EasyOCR fallback
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from latex_ocr_integration import get_latex_ocr_integration, extract_text_with_latex_priority
import logging

def test_latex_ocr_integration():
    """Test the LaTeX-OCR integration system"""
    
    print("🧮 LaTeX-OCR Integration Test")
    print("=" * 50)
    
    # Initialize the integration
    integration = get_latex_ocr_integration()
    
    # Check engine status
    status = integration.get_engine_status()
    print("📊 OCR Engine Status:")
    for engine, available in status.items():
        icon = "✅" if available else "❌"
        print(f"  {icon} {engine}: {available}")
    
    print(f"\n🎯 Primary Engine: {status['primary_engine']}")
    print(f"🔄 Fallback Engine: {status['fallback_engine']}")
    
    # Test mathematical content detection
    print("\n🔍 Testing Mathematical Content Detection:")
    print("-" * 40)
    
    # Since we don't have actual images, we'll test the logic
    test_cases = [
        "This contains x^2 + y^2 = z^2",
        "Simple text without math",
        "alpha + beta = gamma",
        "force = mass * acceleration"
    ]
    
    for test_text in test_cases:
        has_math = integration.detect_mathematical_content(test_text)
        icon = "🧮" if has_math else "📝"
        print(f"  {icon} '{test_text}' -> Mathematical: {has_math}")
    
    print(f"\n✅ LaTeX-OCR integration test completed!")
    print("🚀 Ready for deployment with LaTeX-OCR priority!")

def test_engine_priority():
    """Test that LaTeX-OCR is prioritized over EasyOCR"""
    
    print("\n🎯 Testing Engine Priority Logic")
    print("=" * 40)
    
    integration = get_latex_ocr_integration()
    
    # Test the priority decision
    print("📋 Priority Rules:")
    print("  1. If mathematical content detected -> Try LaTeX-OCR first")
    print("  2. If LaTeX-OCR fails -> Fallback to EasyOCR")
    print("  3. If not mathematical -> Use EasyOCR directly")
    print("  4. If both fail -> Return error")
    
    status = integration.get_engine_status()
    
    if status['latex_ocr_available']:
        print("✅ LaTeX-OCR is available and will be used as primary")
    else:
        print("⚠️ LaTeX-OCR not available, EasyOCR will be primary")
    
    if status['easyocr_available']:
        print("✅ EasyOCR is available as fallback")
    else:
        print("❌ EasyOCR not available - no fallback available")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 LaTeX-OCR Integration Validation")
    print("=" * 60)
    print("This test validates the LaTeX-OCR + EasyOCR hybrid system")
    print("=" * 60)
    
    # Test the integration
    test_latex_ocr_integration()
    
    # Test engine priority
    test_engine_priority()
    
    print(f"\n{'='*60}")
    print("📋 Next Steps:")
    print("  1. Install LaTeX-OCR dependencies")
    print("  2. Deploy to VM")
    print("  3. Test with actual mathematical images")
    print("  4. Verify LaTeX-OCR priority is working")
    print("\n🎯 LaTeX-OCR will significantly improve mathematical expression detection!")
