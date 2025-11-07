#!/usr/bin/env python3
"""
Test the specific OCR issue reported by the user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import correct_math_symbols

def test_specific_issue():
    """Test the exact issue reported by the user"""
    
    print("🎯 Testing Specific OCR Issue")
    print("=" * 50)
    
    # The exact input reported by the user
    input_text = "current density j = a E ne^2 where Q = 3 m"
    
    # The expected output
    expected_output = "current density [→j = α →E], where [α = (ne²/m) τ]"
    
    print(f"📝 Input:    {input_text}")
    print(f"🎯 Expected: {expected_output}")
    
    # Apply corrections
    result = correct_math_symbols(input_text)
    
    print(f"✅ Got:      {result}")
    print(f"🔍 Match:    {'✅ SUCCESS' if result == expected_output else '❌ FAILED'}")
    
    # Test individual components
    print("\n🔧 Component Analysis:")
    print("-" * 30)
    
    components = {
        "Current density preserved": "current density" in result,
        "Vector j (→j)": "→j" in result,
        "Alpha (α)": "α" in result,
        "Vector E (→E)": "→E" in result,
        "Power notation (ne²)": "ne²" in result,
        "Fraction format": "(ne²/m)" in result,
        "Tau (τ)": "τ" in result,
        "Bracket formatting": "[" in result and "]" in result,
    }
    
    for component, status in components.items():
        print(f"{'✅' if status else '❌'} {component}")
    
    # Test variations
    print("\n🧪 Testing Variations:")
    print("-" * 30)
    
    variations = [
        "current density j = a E ne^2 where Q = 3 m",
        "current density j=a E ne^2 where Q=3 m",
        "CURRENT DENSITY J = A E NE^2 WHERE Q = 3 M",
        "Current density j = a E ne^2 where Q = 3 m",
        "current density j = a E ne^2 where Q = 3 m",
    ]
    
    for i, variation in enumerate(variations, 1):
        result_var = correct_math_symbols(variation)
        success = result_var == expected_output
        print(f"Test {i}: {'✅' if success else '❌'}")
        if not success:
            print(f"   Input:  {variation}")
            print(f"   Got:    {result_var}")
    
    return result == expected_output

def test_other_common_issues():
    """Test other common mathematical OCR issues"""
    
    print("\n🔬 Testing Other Common Issues:")
    print("-" * 40)
    
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
            "description": "Current density components"
        },
        {
            "input": "a = 3 m",
            "expected": "α = (ne²/m) τ",
            "description": "Alpha expression context"
        }
    ]
    
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
    return passed == total

if __name__ == "__main__":
    print("🧪 Comprehensive OCR Correction Testing")
    print("=" * 60)
    
    # Test the specific issue
    specific_success = test_specific_issue()
    
    # Test other common issues
    other_success = test_other_common_issues()
    
    # Overall result
    print("\n🏁 Final Results:")
    print("=" * 30)
    print(f"Specific Issue: {'✅ FIXED' if specific_success else '❌ FAILED'}")
    print(f"Other Issues:   {'✅ FIXED' if other_success else '❌ PARTIAL'}")
    
    if specific_success:
        print("\n🎉 The specific OCR issue has been resolved!")
        print("The system will now correctly convert:")
        print("  'current density j = a E ne^2 where Q = 3 m'")
        print("  to:")
        print("  'current density [→j = α →E], where [α = (ne²/m) τ]'")
    else:
        print("\n⚠️  The issue still needs further refinement.")
    
    sys.exit(0 if specific_success else 1)
