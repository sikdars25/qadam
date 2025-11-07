#!/usr/bin/env python3
"""
Test script for mathematical expression libraries in OCR service
"""

import sys
import os
import json
import base64
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import (
    mathml_processor, 
    latex_processor, 
    unicode_processor, 
    opentype_processor,
    MATPLOTLIB_AVAILABLE,
    SYMPY_AVAILABLE,
    LATEX2MATHML_AVAILABLE
)

def test_unicode_math_processor():
    """Test Unicode mathematical symbol processing"""
    print("🔍 Testing Unicode Math Processor")
    print("-" * 40)
    
    test_cases = [
        {
            'input': 'x² + y³ = z⁵',
            'expected_normalized': 'x2 + y3 = z5',
            'description': 'Superscript conversion'
        },
        {
            'input': 'H₂O + CO₂ → H₂CO₃',
            'expected_normalized': 'H2O + CO2 → H2CO3',
            'description': 'Subscript conversion'
        },
        {
            'input': 'λn + λp = λn/λp',
            'expected_symbols': ['λ', 'n', 'λ', 'p', 'λ', 'n', '/', 'λ', 'p'],
            'description': 'Greek letter extraction'
        },
        {
            'input': '∫₀^∞ e^(-x²) dx = √π/2',
            'description': 'Complex mathematical expression'
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        input_text = test['input']
        
        # Test normalization
        normalized = unicode_processor.normalize_math_unicode(input_text)
        
        # Test symbol extraction
        symbols = unicode_processor.extract_math_symbols(input_text)
        
        print(f"  Test {i}: {test['description']}")
        print(f"    Input:     '{input_text}'")
        print(f"    Normalized: '{normalized}'")
        print(f"    Symbols:   {len(symbols)} found")
        
        # Check expected normalization
        if 'expected_normalized' in test:
            if normalized == test['expected_normalized']:
                print(f"    ✅ Normalization: PASS")
                passed += 1
            else:
                print(f"    ❌ Normalization: FAIL (expected '{test['expected_normalized']}')")
                failed += 1
        else:
            passed += 1  # No specific expectation
        
        # Check symbol extraction
        if symbols:
            print(f"    ✅ Symbol extraction: PASS ({len(symbols)} symbols)")
            passed += 1
        else:
            print(f"    ⚠️  Symbol extraction: No symbols found")
        
        print()
    
    return passed, failed

def test_latex_processor():
    """Test LaTeX processing with AMS extensions"""
    print("🔍 Testing LaTeX Processor")
    print("-" * 40)
    
    test_cases = [
        {
            'input': r'\frac{a}{b} + \sqrt{x^2 + y^2}',
            'description': 'Fractions and square roots'
        },
        {
            'input': r'\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}',
            'description': 'Integrals with limits'
        },
        {
            'input': r'\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}',
            'description': 'Summation with infinity'
        },
        {
            'input': r'\alpha + \beta = \gamma',
            'description': 'Greek letters'
        },
        {
            'input': r'\vec{v} = \langle v_x, v_y, v_z \rangle',
            'description': 'Vector notation'
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        input_latex = test['input']
        
        # Test validation
        is_valid = latex_processor.validate_latex(input_latex)
        
        # Test conversion
        converted = latex_processor.latex_to_text(input_latex)
        
        print(f"  Test {i}: {test['description']}")
        print(f"    Input:     '{input_latex}'")
        print(f"    Valid:     {is_valid}")
        print(f"    Converted: '{converted}'")
        
        if is_valid:
            print(f"    ✅ Validation: PASS")
            passed += 1
        else:
            print(f"    ❌ Validation: FAIL")
            failed += 1
        
        if converted != input_latex:  # Should be different for valid LaTeX
            print(f"    ✅ Conversion: PASS")
            passed += 1
        else:
            print(f"    ⚠️  Conversion: No change made")
        
        print()
    
    return passed, failed

def test_mathml_processor():
    """Test MathML processing"""
    print("🔍 Testing MathML Processor")
    print("-" * 40)
    
    test_cases = [
        {
            'input': '<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>',
            'expected': '(a/b)',
            'description': 'Simple fraction'
        },
        {
            'input': '<math><msup><mi>x</mi><mn>2</mn></msup></math>',
            'expected': 'x^2',
            'description': 'Superscript'
        },
        {
            'input': '<math><msub><mi>x</mi><mn>1</mn></msub></math>',
            'expected': 'x_1',
            'description': 'Subscript'
        },
        {
            'input': '<math><msqrt><mi>x</mi><mo>+</mo><mi>y</mi></msqrt></math>',
            'expected': '√(x+y)',
            'description': 'Square root'
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        input_mathml = test['input']
        expected = test['expected']
        
        # Test validation
        is_valid = mathml_processor.validate_mathml(input_mathml)
        
        # Test conversion
        converted = mathml_processor.mathml_to_text(input_mathml)
        
        print(f"  Test {i}: {test['description']}")
        print(f"    Input:     '{input_mathml}'")
        print(f"    Valid:     {is_valid}")
        print(f"    Converted: '{converted}'")
        print(f"    Expected:  '{expected}'")
        
        if is_valid:
            print(f"    ✅ Validation: PASS")
            passed += 1
        else:
            print(f"    ❌ Validation: FAIL")
            failed += 1
        
        if converted == expected:
            print(f"    ✅ Conversion: PASS")
            passed += 1
        else:
            print(f"    ❌ Conversion: FAIL")
            failed += 1
        
        print()
    
    return passed, failed

def test_opentype_math_processor():
    """Test OpenType MATH processing"""
    print("🔍 Testing OpenType MATH Processor")
    print("-" * 40)
    
    test_cases = [
        {
            'input': 'x^2 + y^2 = z^2',
            'description': 'Simple equation'
        },
        {
            'input': r'\frac{a}{b} = \frac{c}{d}',
            'description': 'LaTeX fraction'
        },
        {
            'input': '\int_0^1 x^2 dx',
            'description': 'Integral'
        },
        {
            'input': '\sqrt{x^2 + y^2}',
            'description': 'Square root'
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        input_expr = test['input']
        
        # Test validation
        is_valid = opentype_processor.validate_math_expression(input_expr)
        
        print(f"  Test {i}: {test['description']}")
        print(f"    Input:  '{input_expr}'")
        print(f"    Valid:  {is_valid}")
        
        if is_valid:
            print(f"    ✅ Validation: PASS")
            passed += 1
            
            # Test rendering (only if matplotlib is available)
            if MATPLOTLIB_AVAILABLE:
                try:
                    buffer = opentype_processor.render_math_expression(input_expr)
                    if buffer:
                        print(f"    ✅ Rendering: PASS")
                        passed += 1
                    else:
                        print(f"    ❌ Rendering: FAIL")
                        failed += 1
                except Exception as e:
                    print(f"    ❌ Rendering: FAIL ({e})")
                    failed += 1
            else:
                print(f"    ⚠️  Rendering: Skipped (matplotlib not available)")
        else:
            print(f"    ❌ Validation: FAIL")
            failed += 1
        
        print()
    
    return passed, failed

def test_library_status():
    """Test library availability and status"""
    print("🔍 Testing Library Status")
    print("-" * 40)
    
    libraries = {
        'unicodedata': True,  # Built-in
        'latex2mathml': LATEX2MATHML_AVAILABLE,
        'sympy': SYMPY_AVAILABLE,
        'matplotlib': MATPLOTLIB_AVAILABLE
    }
    
    print("  Library Availability:")
    for lib, available in libraries.items():
        status = "✅ Available" if available else "❌ Not Available"
        print(f"    {lib}: {status}")
    
    print()
    
    # Test font setup
    if MATPLOTLIB_AVAILABLE:
        font_setup = opentype_processor.setup_math_fonts()
        print(f"  Math Font Setup: {'✅ Success' if font_setup else '❌ Failed'}")
    else:
        print(f"  Math Font Setup: ⚠️ Skipped (matplotlib not available)")
    
    print()
    
    return sum(libraries.values()), len(libraries) - sum(libraries.values())

def main():
    """Run all mathematical library tests"""
    print("🧪 Testing Mathematical Expression Libraries in OCR Service")
    print("=" * 65)
    
    total_passed = 0
    total_failed = 0
    
    # Run all tests
    tests = [
        test_unicode_math_processor,
        test_latex_processor,
        test_mathml_processor,
        test_opentype_math_processor,
        test_library_status
    ]
    
    for test_func in tests:
        passed, failed = test_func()
        total_passed += passed
        total_failed += failed
    
    print("=" * 65)
    print(f"📊 Overall Results: {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("🎉 All mathematical library tests passed!")
        return True
    else:
        print("⚠️ Some mathematical library tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
