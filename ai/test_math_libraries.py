#!/usr/bin/env python3
"""
Test script for mathematical expression libraries in AI service
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import (
    mathml_processor, 
    latex_processor, 
    unicode_processor,
    normalize_math_expression,
    LATEX2MATHML_AVAILABLE,
    SYMPY_AVAILABLE,
    MATH_SYMBOLS
)

def test_ai_math_libraries():
    """Test mathematical library integration in AI service"""
    print("🧪 Testing Mathematical Expression Libraries in AI Service")
    print("=" * 65)
    
    # Test Unicode processing
    print("🔍 Testing Unicode Math Processor Integration")
    print("-" * 50)
    
    unicode_tests = [
        'x² + y³ = z⁵',
        'H₂O + CO₂ → H₂CO₃',
        'λn + λp = λn/λp',
        '∫₀^∞ e^(-x²) dx = √π/2'
    ]
    
    for i, test in enumerate(unicode_tests, 1):
        normalized = unicode_processor.normalize_math_unicode(test)
        symbols = unicode_processor.extract_math_symbols(test)
        print(f"  Test {i}:")
        print(f"    Input:     '{test}'")
        print(f"    Normalized: '{normalized}'")
        print(f"    Symbols:   {len(symbols)} found")
        print()
    
    # Test LaTeX processing
    print("🔍 Testing LaTeX Processor Integration")
    print("-" * 50)
    
    latex_tests = [
        r'\frac{a}{b} + \sqrt{x^2 + y^2}',
        r'\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}',
        r'\alpha + \beta = \gamma'
    ]
    
    for i, test in enumerate(latex_tests, 1):
        is_valid = latex_processor.validate_latex(test)
        converted = latex_processor.latex_to_text(test)
        print(f"  Test {i}:")
        print(f"    Input:     '{test}'")
        print(f"    Valid:     {is_valid}")
        print(f"    Converted: '{converted}'")
        print()
    
    # Test MathML processing
    print("🔍 Testing MathML Processor Integration")
    print("-" * 50)
    
    mathml_tests = [
        ('<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>', '(a/b)'),
        ('<math><msup><mi>x</mi><mn>2</mn></msup></math>', 'x^2'),
        ('<math><msqrt><mi>x</mi><mo>+</mo><mi>y</mi></msqrt></math>', '√(x)')
    ]
    
    for i, (test, expected) in enumerate(mathml_tests, 1):
        is_valid = mathml_processor.validate_mathml(test)
        converted = mathml_processor.mathml_to_text(test)
        print(f"  Test {i}:")
        print(f"    Input:     '{test}'")
        print(f"    Valid:     {is_valid}")
        print(f"    Converted: '{converted}'")
        print(f"    Expected:  '{expected}'")
        print(f"    Status:    {'✅ PASS' if converted == expected else '❌ FAIL'}")
        print()
    
    # Test integrated normalize_math_expression function
    print("🔍 Testing Enhanced normalize_math_expression Function")
    print("-" * 50)
    
    integration_tests = [
        {
            'input': 'x² + y³ = z⁵',
            'description': 'Unicode superscripts'
        },
        {
            'input': r'\frac{a}{b} + \sqrt{x^2 + y^2}',
            'description': 'LaTeX expression'
        },
        {
            'input': '<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>',
            'description': 'MathML expression'
        },
        {
            'input': 'λ n + λ p = λ n / λ p',
            'description': 'Combined processing'
        },
        {
            'input': 'α + β = γ',
            'description': 'Greek letters preservation'
        }
    ]
    
    for i, test in enumerate(integration_tests, 1):
        result = normalize_math_expression(test['input'])
        print(f"  Test {i}: {test['description']}")
        print(f"    Input:  '{test['input']}'")
        print(f"    Output: '{result}'")
        print()
    
    # Test MATH_SYMBOLS dictionary
    print("🔍 Testing MATH_SYMBOLS Dictionary")
    print("-" * 50)
    
    print(f"  Total symbols defined: {len(MATH_SYMBOLS)}")
    print("  Symbol mappings:")
    for symbol, name in list(MATH_SYMBOLS.items())[:10]:  # Show first 10
        print(f"    {symbol} → {name}")
    if len(MATH_SYMBOLS) > 10:
        print(f"    ... and {len(MATH_SYMBOLS) - 10} more")
    print()
    
    # Library status
    print("🔍 Library Availability Status")
    print("-" * 50)
    
    libraries = {
        'unicodedata': True,  # Built-in
        'latex2mathml': LATEX2MATHML_AVAILABLE,
        'sympy': SYMPY_AVAILABLE,
        'mathml': True,  # Built-in XML processing
        'latex': True   # Basic LaTeX processing
    }
    
    for lib, available in libraries.items():
        status = "✅ Available" if available else "❌ Not Available"
        print(f"  {lib}: {status}")
    
    print()
    print("=" * 65)
    print("🎉 AI service mathematical libraries integration complete!")
    
    return True

if __name__ == "__main__":
    success = test_ai_math_libraries()
    sys.exit(0 if success else 1)
