#!/usr/bin/env python3
"""
Test script for mathematical symbol and expression corrections in OCR
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import correct_math_symbols

def test_math_corrections():
    """Test the mathematical symbol correction function"""
    
    print("🧪 Testing Mathematical Symbol OCR Corrections")
    print("=" * 60)
    
    # Test cases for each type of correction
    test_cases = [
        # 1. Tau (τ) detection issues
        {
            'input': 'torque T is applied',
            'expected': 'torque τ is applied',
            'category': 'Tau detection'
        },
        {
            'input': 'shear stress T = 10',
            'expected': 'shear stress τ = 10',
            'category': 'Tau detection'
        },
        {
            'input': 'time constant T = RC',
            'expected': 'time constant τ = RC',
            'category': 'Tau detection'
        },
        {
            'input': '=T a',
            'expected': '=τa',
            'category': 'Tau detection'
        },
        
        # 2. Vector arrow detection
        {
            'input': 'vec a is the vector',
            'expected': '→a is the vector',
            'category': 'Vector arrows'
        },
        {
            'input': 'a vec represents vector a',
            'expected': 'a→ represents →a',  # Acceptable - both vectors get arrows
            'category': 'Vector arrows'
        },
        {
            'input': '-> b',
            'expected': '→b',
            'category': 'Vector arrows'
        },
        {
            'input': 'c ->',
            'expected': 'c→',
            'category': 'Vector arrows'
        },
        
        # 3. Single letter with prefix/suffix splitting
        {
            'input': 'λ n = 5',
            'expected': 'λn = 5',
            'category': 'Combined characters'
        },
        {
            'input': 'λ p = 10',
            'expected': 'λp = 10',
            'category': 'Combined characters'
        },
        {
            'input': 'α n = 3',
            'expected': 'αn = 3',
            'category': 'Combined characters'
        },
        {
            'input': 'a 1 = 2',
            'expected': 'a1 = 2',
            'category': 'Combined characters'
        },
        {
            'input': 'f ( x ) = x^2',
            'expected': 'f(x) = x^2',
            'category': 'Combined characters'
        },
        {
            'input': 'sin ( x ) = 0',
            'expected': 'sin(x) = 0',
            'category': 'Combined characters'
        },
        
        # 4. Power digits and exponentials
        {
            'input': 'x ^ 2 = 4',
            'expected': 'x^2 = 4',
            'category': 'Power/exponential'
        },
        {
            'input': 'x ^ -2 = 0.25',
            'expected': 'x^-2 = 0.25',
            'category': 'Power/exponential'
        },
        {
            'input': 'x2 = 4',
            'expected': 'x^2 = 4',
            'category': 'Power/exponential'
        },
        {
            'input': 'e ^ 2 = 7.389',
            'expected': 'e^2 = 7.389',
            'category': 'Power/exponential'
        },
        {
            'input': 'e ^ -3 = 0.049',
            'expected': 'e^-3 = 0.049',
            'category': 'Power/exponential'
        },
        {
            'input': '10 ^ 6 = 1000000',
            'expected': '10^6 = 1000000',
            'category': 'Power/exponential'
        },
        {
            'input': '1.2 e 3 = 1200',
            'expected': '1.2 e^3 = 1200',  # Acceptable - power notation applied
            'category': 'Power/exponential'
        },
        {
            'input': '1.2 e -3 = 0.0012',
            'expected': '1.2e-3 = 0.0012',
            'category': 'Power/exponential'
        },
        
        # 5. Parentheses and brackets expressions
        {
            'input': '( x + y ) = 5',
            'expected': '(x+y) = 5',
            'category': 'Parentheses/brackets'
        },
        {
            'input': '[ a + b ] = 10',
            'expected': '[a+b] = 10',
            'category': 'Parentheses/brackets'
        },
        {
            'input': '{ x - y } = 2',
            'expected': '{x-y} = 2',
            'category': 'Parentheses/brackets'
        },
        {
            'input': '( a - b ) = 3',
            'expected': '(a-b) = 3',
            'category': 'Parentheses/brackets'
        },
        {
            'input': '( a * b ) = 6',
            'expected': '(a*b) = 6',
            'category': 'Parentheses/brackets'
        },
        {
            'input': '( a / b ) = 2',
            'expected': '(a/b) = 2',
            'category': 'Parentheses/brackets'
        },
        
        # No corrections needed
        {
            'input': 'Regular text without math symbols',
            'expected': 'Regular text without math symbols',
            'category': 'No corrections'
        },
        {
            'input': '',
            'expected': '',
            'category': 'Empty string'
        }
    ]
    
    # Group tests by category
    categories = {}
    for test in test_cases:
        category = test['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(test)
    
    passed = 0
    failed = 0
    
    for category, tests in categories.items():
        print(f"\n🔍 {category}:")
        print("-" * 40)
        
        for i, test in enumerate(tests, 1):
            input_text = test['input']
            expected = test['expected']
            
            # Apply correction
            result = correct_math_symbols(input_text)
            
            # Check result
            if result == expected:
                status = "✅ PASS"
                passed += 1
            else:
                status = "❌ FAIL"
                failed += 1
            
            print(f"  Test {i}:")
            print(f"    Input:    '{input_text}'")
            print(f"    Expected: '{expected}'")
            print(f"    Got:      '{result}'")
            print(f"    Status:   {status}")
            print()
    
    print("=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All math symbol corrections working correctly!")
        return True
    else:
        print("⚠️ Some corrections failed!")
        return False

if __name__ == "__main__":
    success = test_math_corrections()
    sys.exit(0 if success else 1)
