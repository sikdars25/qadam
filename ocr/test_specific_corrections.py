#!/usr/bin/env python3
"""
Test specific OCR corrections for the reported issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import correct_math_symbols

def test_specific_issue():
    """Test the specific issue reported by user"""
    
    print("🧪 Testing Specific OCR Correction Issue")
    print("=" * 50)
    
    # Test case 1: The exact issue reported
    test_input_1 = "current density j =Q E E ne^2 where a = 3 m"
    expected_1 = "current density [→j = α →E], where [α = (ne²/m) τ]"
    
    result_1 = correct_math_symbols(test_input_1)
    
    print(f"📝 Test Case 1:")
    print(f"   Input:    {test_input_1}")
    print(f"   Expected: {expected_1}")
    print(f"   Got:      {result_1}")
    print(f"   ✅ Pass:  {result_1 == expected_1}")
    print()
    
    # Test case 2: Individual components
    test_cases = [
        {
            "input": "vec j = alpha vec E",
            "expected": "→j = α →E",
            "description": "Vector notation with Greek letters"
        },
        {
            "input": "alpha = left (frac ne^2 m right) tau",
            "expected": "α = (ne²/m) τ",
            "description": "Fraction notation with Greek letters"
        },
        {
            "input": "j = Q E ne^2",
            "expected": "→j = α →E ne²",
            "description": "Current density equation components"
        },
        {
            "input": "a = 3 m",
            "expected": "α = (ne²/m) τ",
            "description": "Alpha expression (context-specific)"
        },
        {
            "input": "current density [j = alpha E], where [alpha = (ne^2/m) tau]",
            "expected": "current density [→j = α →E], where [α = (ne²/m) τ]",
            "description": "Complete expression with brackets"
        }
    ]
    
    print("📋 Component Tests:")
    print("-" * 30)
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        result = correct_math_symbols(test_case["input"])
        success = result == test_case["expected"]
        
        if success:
            passed += 1
        
        print(f"Test {i}: {test_case['description']}")
        print(f"   Input:    {test_case['input']}")
        print(f"   Expected: {test_case['expected']}")
        print(f"   Got:      {result}")
        print(f"   ✅ Pass:  {success}")
        print()
    
    print(f"📊 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the corrections.")
        return False

def test_math_symbol_detection():
    """Test detection of various mathematical symbols"""
    
    print("\n🔍 Math Symbol Detection Tests")
    print("=" * 40)
    
    test_cases = [
        "vec j",
        "alpha beta gamma",
        "frac ne^2 m",
        "left ( right )",
        "tau T",
        "ne^2 ne2",
        "Q E",
        "current density"
    ]
    
    for test_case in test_cases:
        result = correct_math_symbols(test_case)
        changed = result != test_case
        print(f"{'✅' if changed else '⚪'} {test_case:20} → {result}")

if __name__ == "__main__":
    success = test_specific_issue()
    test_math_symbol_detection()
    
    if not success:
        sys.exit(1)
