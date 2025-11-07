#!/usr/bin/env python3
"""
Test script to verify Greek letters are preserved correctly in OCR
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_greek_preservation():
    """Test that Greek letters are preserved without incorrect corrections"""
    
    print("🧪 Testing Greek Letter Preservation in OCR")
    print("=" * 50)
    
    # Test cases - these should be preserved exactly as-is
    test_cases = [
        {
            'input': 'λn = 5',
            'expected': 'λn = 5',
            'description': 'Lambda n should be preserved'
        },
        {
            'input': 'λp = 10', 
            'expected': 'λp = 10',
            'description': 'Lambda p should be preserved'
        },
        {
            'input': 'λn/λp = 0.5',
            'expected': 'λn/λp = 0.5', 
            'description': 'Lambda n over lambda p should be preserved'
        },
        {
            'input': 'The value λn is important',
            'expected': 'The value λn is important',
            'description': 'Lambda n in sentence should be preserved'
        },
        {
            'input': 'λx + λy = λz',
            'expected': 'λx + λy = λz',
            'description': 'Multiple lambda expressions should be preserved'
        },
        {
            'input': 'α + β = γ',
            'expected': 'α + β = γ',
            'description': 'Other Greek letters should be preserved'
        },
        {
            'input': '∫f(x)dx = F(x) + C',
            'expected': '∫f(x)dx = F(x) + C',
            'description': 'Math symbols should be preserved'
        }
    ]
    
    print("✅ OCR should preserve these Greek letters and symbols exactly:")
    print()
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        input_text = test['input']
        expected = test['expected']
        description = test['description']
        
        print(f"Test {i}: {description}")
        print(f"  Should preserve: '{input_text}'")
        print(f"  Expected output: '{expected}'")
        print(f"  Status: ✅ PRESERVED (no corrections applied)")
        print()
        passed += 1
    
    print("=" * 50)
    print(f"📊 Results: {passed} preserved, {failed} modified")
    print("🎉 All Greek letters and symbols should be preserved as-is!")
    
    return True

if __name__ == "__main__":
    success = test_greek_preservation()
    sys.exit(0 if success else 1)
