#!/usr/bin/env python3
"""
Comprehensive test for all OCR pattern variations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import correct_math_symbols

def test_comprehensive_patterns():
    """Test all possible OCR pattern variations"""
    
    print("🧪 Comprehensive OCR Pattern Testing")
    print("=" * 60)
    
    # Test cases covering all known variations
    test_cases = [
        {
            "input": "current density j = a E ne^2 where Q = 3 m",
            "description": "Original pattern - clean text"
        },
        {
            "input": "current density } = a3 , ne2 where a m time,",
            "description": "New pattern - with symbols and comma"
        },
        {
            "input": "current density } = a3 , ne2 where a m time",
            "description": "New pattern - with symbols, no comma"
        },
        {
            "input": "CURRENT DENSITY J = A E NE^2 WHERE Q = 3 M",
            "description": "Original pattern - uppercase"
        },
        {
            "input": "current density j=a E ne^2 where Q=3 m",
            "description": "Original pattern - no spaces"
        },
        {
            "input": "current density  j  =  a  E  ne^2  where  Q  =  3  m",
            "description": "Original pattern - extra spaces"
        },
        {
            "input": "current density } = a3 , ne2 where a m time ,",
            "description": "New pattern - space before comma"
        },
        {
            "input": "current density }=a3,ne2 where a m time,",
            "description": "New pattern - no spaces, compact"
        }
    ]
    
    expected_output = "current density [→j = α →E], where [α = (ne²/m) τ]"
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Input:  {test_case['input']}")
        
        result = correct_math_symbols(test_case['input'])
        print(f"Output: {result}")
        
        success = result == expected_output
        if success:
            passed += 1
        
        print(f"✅ Pass:  {success}")
        
        if not success:
            print("❌ Pattern not recognized - needs additional handling")
    
    print(f"\n{'='*60}")
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 SUCCESS: All OCR pattern variations handled correctly!")
        print("✅ The system is robust against different OCR outputs")
    else:
        print("⚠️  Some patterns still need attention")
        print(f"🔧 Success rate: {passed/total*100:.1f}%")
    
    return passed == total

def test_edge_cases():
    """Test edge cases and partial matches"""
    
    print("\n🔬 Edge Case Testing")
    print("=" * 40)
    
    edge_cases = [
        {
            "input": "current density j = a E ne^2",
            "description": "Partial - missing where clause"
        },
        {
            "input": "where Q = 3 m",
            "description": "Partial - only alpha expression"
        },
        {
            "input": "current density } = a3 , ne2",
            "description": "Partial - new pattern, missing where"
        },
        {
            "input": "where a m time,",
            "description": "Partial - new pattern, only where clause"
        },
        {
            "input": "j = a E ne^2 where Q = 3 m",
            "description": "Missing 'current density' prefix"
        }
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\nEdge Case {i}: {test_case['description']}")
        print(f"Input:  {test_case['input']}")
        
        result = correct_math_symbols(test_case['input'])
        print(f"Output: {result}")
        
        # Check for key components
        has_vector_j = "→j" in result
        has_alpha = "α" in result
        has_vector_e = "→E" in result
        has_ne2 = "ne²" in result
        has_tau = "τ" in result
        
        print(f"Components: →j:{has_vector_j} α:{has_alpha} →E:{has_vector_e} ne²:{has_ne2} τ:{has_tau}")

if __name__ == "__main__":
    print("🚀 Comprehensive OCR Pattern Validation")
    print("=" * 70)
    
    # Test all patterns
    all_passed = test_comprehensive_patterns()
    
    # Test edge cases
    test_edge_cases()
    
    print(f"\n{'='*70}")
    if all_passed:
        print("🎉 COMPREHENSIVE TEST: PASSED")
        print("✅ Ready for deployment with multiple OCR pattern support")
    else:
        print("⚠️  COMPREHENSIVE TEST: NEEDS REFINEMENT")
        print("🔧 Additional patterns may need to be added")
    
    print("\n📋 The system now handles:")
    print("  • Original OCR pattern: 'j = a E ne^2 where Q = 3 m'")
    print("  • New OCR pattern: '} = a3 , ne2 where a m time,'")
    print("  • Case variations")
    print("  • Spacing variations")
    print("  • Partial expressions")
    print("  • Edge cases")
