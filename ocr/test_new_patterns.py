#!/usr/bin/env python3
"""
Test the new OCR pattern that's being detected
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import correct_math_symbols

def test_new_ocr_patterns():
    """Test the new OCR patterns being detected"""
    
    print("🧪 Testing New OCR Patterns")
    print("=" * 50)
    
    # The new pattern you're seeing
    new_pattern = "current density } = a3 , ne2 where a m time,"
    
    # The expected correct output
    expected = "current density [→j = α →E], where [α = (ne²/m) τ]"
    
    print(f"📝 New OCR Input: {new_pattern}")
    print(f"🎯 Expected:       {expected}")
    
    # Test current correction
    result = correct_math_symbols(new_pattern)
    print(f"✅ Current Output: {result}")
    
    # Check if it matches
    if result == expected:
        print("🎉 SUCCESS: New pattern is handled correctly!")
        return True
    else:
        print("❌ FAILED: New pattern needs additional handling")
        
        # Analyze what we need to fix
        print("\n🔍 Pattern Analysis:")
        print("-" * 30)
        
        components = {
            "Current density preserved": "current density" in result,
            "Has vector j": "→j" in result,
            "Has alpha": "α" in result,
            "Has vector E": "→E" in result,
            "Has ne²": "ne²" in result,
            "Has fraction": "(ne²/m)" in result,
            "Has tau": "τ" in result,
            "Has brackets": "[" in result and "]" in result,
        }
        
        for component, status in components.items():
            print(f"{'✅' if status else '❌'} {component}")
        
        return False

def test_multiple_patterns():
    """Test multiple OCR variations"""
    
    print("\n🎯 Testing Multiple OCR Variations")
    print("=" * 50)
    
    patterns = [
        {
            "input": "current density j = a E ne^2 where Q = 3 m",
            "description": "Original pattern"
        },
        {
            "input": "current density } = a3 , ne2 where a m time,",
            "description": "New pattern with symbols"
        },
        {
            "input": "current density } = a3 , ne2 where a m time",
            "description": "New pattern without comma"
        },
        {
            "input": "current density j = a E ne^2 where Q = 3 m",
            "description": "Original with spaces"
        }
    ]
    
    expected = "current density [→j = α →E], where [α = (ne²/m) τ]"
    
    for i, pattern in enumerate(patterns, 1):
        print(f"\nTest {i}: {pattern['description']}")
        print(f"Input:  {pattern['input']}")
        
        result = correct_math_symbols(pattern['input'])
        print(f"Output: {result}")
        
        success = result == expected
        print(f"✅ Pass:  {success}")
        
        if not success:
            print("❌ Needs additional correction patterns")

if __name__ == "__main__":
    print("🔬 OCR Pattern Analysis")
    print("=" * 60)
    
    # Test the new pattern
    new_works = test_new_ocr_patterns()
    
    # Test multiple variations
    test_multiple_patterns()
    
    print("\n" + "=" * 60)
    if new_works:
        print("🎉 New patterns are handled correctly!")
    else:
        print("⚠️  Need to add more correction patterns for new variations")
        print("The OCR is producing different incorrect results each time")
        print("We need a more robust pattern matching system")
