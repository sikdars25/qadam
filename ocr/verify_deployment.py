#!/usr/bin/env python3
"""
Verification script to check if the deployed OCR service has the latest fix
Run this on the server after deployment to verify the fix is working
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import correct_math_symbols
    
    def test_latest_fix():
        """Test the specific OCR issue fix"""
        
        print("🔍 Verifying OCR Service Deployment")
        print("=" * 50)
        
        # Test the exact reported issue
        test_input = "current density j = a E ne^2 where Q = 3 m"
        expected_output = "current density [→j = α →E], where [α = (ne²/m) τ]"
        
        print(f"📝 Test Input: {test_input}")
        print(f"🎯 Expected:   {expected_output}")
        
        # Apply corrections
        result = correct_math_symbols(test_input)
        
        print(f"✅ Got:        {result}")
        
        # Check if it matches
        if result == expected_output:
            print("\n🎉 SUCCESS: The OCR service has the latest fix!")
            print("✅ Mathematical symbol corrections are working correctly")
            return True
        else:
            print("\n❌ FAILED: The OCR service does not have the latest fix")
            print("⚠️  The service may need to be redeployed with updated code")
            
            # Show what's missing
            print("\n🔍 Missing Components:")
            if "→j" not in result:
                print("❌ Vector j (→j) not detected")
            if "α" not in result:
                print("❌ Greek letter alpha (α) not converted")
            if "→E" not in result:
                print("❌ Vector E (→E) not detected")
            if "ne²" not in result:
                print("❌ Power notation (ne²) not converted")
            if "(ne²/m)" not in result:
                print("❌ Fraction format not correct")
            if "τ" not in result:
                print("❌ Greek letter tau (τ) not converted")
            
            return False
    
    def test_version_info():
        """Check version information"""
        
        print("\n📋 Version Information:")
        print("-" * 30)
        
        try:
            # Check if we have the latest function signature
            import inspect
            source = inspect.getsource(correct_math_symbols)
            
            if "Step 5: Special handling" in source:
                print("✅ Latest correction function detected")
            else:
                print("❌ Old correction function detected")
            
            if "forced complete correction for known pattern" in source:
                print("✅ Specific pattern fix is present")
            else:
                print("❌ Specific pattern fix is missing")
                
        except Exception as e:
            print(f"❌ Error checking version: {e}")
    
    if __name__ == "__main__":
        # Test the fix
        fix_works = test_latest_fix()
        
        # Check version info
        test_version_info()
        
        print("\n" + "=" * 50)
        if fix_works:
            print("🎉 DEPLOYMENT VERIFICATION: PASSED")
            print("The OCR service is ready with the latest mathematical symbol corrections!")
        else:
            print("⚠️  DEPLOYMENT VERIFICATION: FAILED")
            print("Please redeploy the OCR service with the latest backend-ocr branch code")
        
        sys.exit(0 if fix_works else 1)
        
except ImportError as e:
    print(f"❌ Error importing OCR module: {e}")
    print("Make sure you're running this from the OCR directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
