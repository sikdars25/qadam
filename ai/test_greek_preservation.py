#!/usr/bin/env python3
"""
Test script to verify Greek letters are preserved correctly in AI service
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import normalize_math_expression, analyze_math_content

def test_ai_greek_preservation():
    """Test that AI service preserves Greek letters without modifications"""
    
    print("🧪 Testing Greek Letter Preservation in AI Service")
    print("=" * 60)
    
    # Test cases for normalization function
    test_cases = [
        {
            'input': 'λn = 5',
            'expected': 'λn = 5',
            'description': 'Lambda n should be preserved exactly'
        },
        {
            'input': 'λp = 10', 
            'expected': 'λp = 10',
            'description': 'Lambda p should be preserved exactly'
        },
        {
            'input': 'λn/λp = 0.5',
            'expected': 'λn/λp = 0.5', 
            'description': 'Lambda division should be preserved exactly'
        },
        {
            'input': 'α + β = γ',
            'expected': 'α + β = γ',
            'description': 'Greek letters should be preserved'
        },
        {
            'input': '∫f(x)dx = F(x) + C',
            'expected': '∫f(x)dx = F(x) + C',
            'description': 'Math symbols should be preserved'
        }
    ]
    
    print("🔧 Testing normalize_math_expression function:")
    print()
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        input_text = test['input']
        expected = test['expected']
        description = test['description']
        
        # Test normalization
        result = normalize_math_expression(input_text)
        
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
    
    # Test math analysis function
    print("📊 Testing analyze_math_content function:")
    print()
    
    analysis_tests = [
        {
            'input': 'λn = 5',
            'expected_greek': True,
            'expected_symbols': False,
            'description': 'Lambda n should detect Greek letters'
        },
        {
            'input': 'x + y = z',
            'expected_greek': False,
            'expected_symbols': False,
            'description': 'Regular variables should not detect Greek'
        },
        {
            'input': '∫f(x)dx',
            'expected_greek': False,
            'expected_symbols': True,
            'description': 'Math symbols should be detected'
        }
    ]
    
    for i, test in enumerate(analysis_tests, 1):
        input_text = test['input']
        expected_greek = test['expected_greek']
        expected_symbols = test['expected_symbols']
        description = test['description']
        
        # Test analysis
        result = analyze_math_content(input_text)
        
        greek_ok = result['has_greek_letters'] == expected_greek
        symbols_ok = result['has_math_symbols'] == expected_symbols
        
        if greek_ok and symbols_ok:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"Analysis Test {i}: {description}")
        print(f"  Input:           '{input_text}'")
        print(f"  Greek detected:  {result['has_greek_letters']} (expected {expected_greek})")
        print(f"  Symbols detected: {result['has_math_symbols']} (expected {expected_symbols})")
        print(f"  Status:          {status}")
        print()
    
    print("=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Greek letters are preserved correctly.")
        return True
    else:
        print("⚠️ Some tests failed!")
        return False

if __name__ == "__main__":
    success = test_ai_greek_preservation()
    sys.exit(0 if success else 1)
