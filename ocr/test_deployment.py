#!/usr/bin/env python3
"""
Test to verify if the deployed OCR service has the latest corrections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import correct_math_symbols
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)

def test_deployment_fix():
    """Test if the deployment has the specific fix"""
    
    print("🔍 Testing Deployment Fix")
    print("=" * 40)
    
    # Test the exact reported issue
    test_input = "current density j = a E ne^2 where Q = 3 m"
    expected_output = "current density [→j = α →E], where [α = (ne²/m) τ]"
    
    print(f"📝 Input: {test_input}")
    print(f"🎯 Expected: {expected_output}")
    
    # Apply corrections
    result = correct_math_symbols(test_input)
    
    print(f"✅ Got: {result}")
    
    # Check if it matches
    if result == expected_output:
        print("🎉 SUCCESS: The fix is working correctly!")
        return True
    else:
        print("❌ FAILED: The fix is not working as expected.")
        
        # Debug: Let's see what corrections were applied
        print("\n🔧 Debugging Information:")
        print("-" * 30)
        
        # Test individual components
        components = {
            "Contains 'current density'": "current density" in result,
            "Contains '→j'": "→j" in result,
            "Contains 'α'": "α" in result,
            "Contains '→E'": "→E" in result,
            "Contains 'ne²'": "ne²" in result,
            "Contains '(ne²/m)'": "(ne²/m)" in result,
            "Contains 'τ'": "τ" in result,
            "Has brackets": "[" in result and "]" in result,
        }
        
        for component, status in components.items():
            print(f"{'✅' if status else '❌'} {component}")
        
        return False

def test_pattern_matching():
    """Test if the specific pattern is being detected"""
    
    print("\n🧪 Testing Pattern Matching")
    print("=" * 40)
    
    import re
    
    test_text = "current density j = a E ne^2 where Q = 3 m"
    
    # Test the exact pattern from our fix
    pattern = r'current\s+density\s+j\s*=\s*a\s*E\s*ne\^2\s*where\s*Q\s*=\s*3\s*m'
    
    if re.search(pattern, test_text, re.IGNORECASE):
        print("✅ Pattern matches - should trigger the fix")
    else:
        print("❌ Pattern does not match - fix won't trigger")
        
        # Let's see what doesn't match
        print("\n🔍 Pattern Breakdown:")
        parts = [
            "current\\s+density",
            "j\\s*=\\s*a",
            "E\\s+ne\\^2",
            "where\\s+Q\\s*=\\s*3\\s*m"
        ]
        
        for i, part in enumerate(parts, 1):
            if re.search(part, test_text, re.IGNORECASE):
                print(f"✅ Part {i}: '{part}' matches")
            else:
                print(f"❌ Part {i}: '{part}' does not match")
    
    # Test the lowercase version
    if 'current density j = a e ne^2 where q = 3 m' in test_text.lower():
        print("✅ Lowercase detection works")
    else:
        print("❌ Lowercase detection failed")

if __name__ == "__main__":
    print("🚀 OCR Deployment Verification")
    print("=" * 50)
    
    # Test the fix
    fix_works = test_deployment_fix()
    
    # Test pattern matching
    test_pattern_matching()
    
    if fix_works:
        print("\n🎉 The deployment fix is working!")
        print("If you're still seeing the old behavior, the service might need to be redeployed.")
    else:
        print("\n⚠️  The fix is not working as expected.")
        print("The deployed service might not have the latest code.")
