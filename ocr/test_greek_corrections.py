#!/usr/bin/env python3
"""
Test script for Greek letter OCR corrections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import correct_ocr_greek_letters

def test_greek_corrections():
    """Test the Greek letter correction function"""
    
    print("🧪 Testing Greek Letter OCR Corrections")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            'input': 'λn = 5',
            'expected': '4n = 5',
            'description': 'Lambda n to 4n'
        },
        {
            'input': 'λp = 10', 
            'expected': '2p = 10',
            'description': 'Lambda p to 2p'
        },
        {
            'input': 'λn/λp = 0.5',
            'expected': '^n Ap = 0.5', 
            'description': 'Lambda n over lambda p to ^n Ap'
        },
        {
            'input': 'The value λn is important',
            'expected': 'The value 4n is important',
            'description': 'Lambda n in sentence'
        },
        {
            'input': 'λx + λy = λz',
            'expected': '4x + 4y = 4z',
            'description': 'Multiple lambda corrections'
        },
        {
            'input': 'No corrections needed here',
            'expected': 'No corrections needed here',
            'description': 'No Greek letters'
        },
        {
            'input': '',
            'expected': '',
            'description': 'Empty string'
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        input_text = test['input']
        expected = test['expected']
        description = test['description']
        
        # Apply correction
        result = correct_ocr_greek_letters(input_text)
        
        # Check result
        if result == expected:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"Test {i}: {description}")
        print(f"  Input:    '{input_text}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")
        print(f"  Status:   {status}")
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed!")
        return False

if __name__ == "__main__":
    success = test_greek_corrections()
    sys.exit(0 if success else 1)
