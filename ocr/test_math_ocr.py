"""
Test OCR service for mathematical expressions
Tests Latin letters, Greek symbols, and math operators
"""

import requests
import base64
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image(text, filename="test_math.png"):
    """Create a test image with mathematical text"""
    # Create image
    img = Image.new('RGB', (800, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a good font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((50, 75), text, fill='black', font=font)
    
    # Save
    img.save(filename)
    print(f"✅ Created test image: {filename}")
    return filename

def test_ocr_service(image_path=None, text=None):
    """Test the OCR service with a math expression"""
    
    # Create test image if text provided
    if text and not image_path:
        image_path = create_test_image(text)
    
    if not image_path or not os.path.exists(image_path):
        print("❌ No image provided or image not found")
        return
    
    print(f"\n🔍 Testing OCR on: {image_path}")
    print("=" * 60)
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Test OCR service
    try:
        url = 'http://localhost:5001/api/extract-text'
        print(f"📡 Sending request to: {url}")
        
        response = requests.post(
            url,
            json={'image_base64': image_data},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"\n✅ OCR SUCCESS")
                print(f"📝 Extracted Text: {result['text']}")
                print(f"📊 Confidence: {result.get('confidence', 0):.2%}")
                print(f"📐 Has Math: {result.get('has_math', 'N/A')}")
                print(f"📄 Line Count: {result.get('line_count', 'N/A')}")
                
                # Show details if available
                if 'details' in result:
                    print(f"\n📋 Detailed Results ({len(result['details'])} segments):")
                    for i, item in enumerate(result['details'], 1):
                        print(f"  {i}. '{item['text']}' (confidence: {item['confidence']:.2%})")
            else:
                print(f"\n❌ OCR FAILED")
                print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: OCR service not running")
        print("💡 Start the service with: .\\run_ocr_only.bat")
    except requests.exceptions.Timeout:
        print("\n❌ Request Timeout: Service took too long to respond")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def test_multiple_expressions():
    """Test multiple math expressions"""
    
    test_cases = [
        "x + y = z",
        "2x + 3 = 7",
        "a² + b² = c²",
        "θ = 45°",
        "α + β = γ",
        "∫ f(x) dx",
        "Σ (n=1 to ∞)",
        "√(x² + y²)",
    ]
    
    print("\n" + "=" * 60)
    print("🧪 TESTING MULTIPLE MATH EXPRESSIONS")
    print("=" * 60)
    
    for i, expression in enumerate(test_cases, 1):
        print(f"\n\n📝 Test {i}/{len(test_cases)}: {expression}")
        print("-" * 60)
        
        # Create test image
        filename = f"test_math_{i}.png"
        create_test_image(expression, filename)
        
        # Test OCR
        test_ocr_service(filename)
        
        # Clean up
        try:
            os.remove(filename)
        except:
            pass

def check_service_health():
    """Check if OCR service is running"""
    try:
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ OCR Service is running")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   OCR Engine: {data.get('ocr_engine', 'Unknown')}")
            print(f"   EasyOCR Version: {data.get('easyocr_version', 'Unknown')}")
            
            if 'features' in data:
                print(f"   Features: {', '.join(data['features'])}")
            
            return True
        else:
            print("⚠️ OCR Service returned unexpected status")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ OCR Service is NOT running")
        print("💡 Start it with: .\\run_ocr_only.bat")
        return False
    except Exception as e:
        print(f"❌ Error checking service: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🔬 MATH OCR TESTING TOOL")
    print("=" * 60)
    
    # Check service health
    print("\n1️⃣ Checking OCR Service...")
    if not check_service_health():
        return
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--multiple':
            # Test multiple expressions
            test_multiple_expressions()
        else:
            # Test specific image
            image_path = sys.argv[1]
            test_ocr_service(image_path)
    else:
        # Default: test a simple expression
        print("\n2️⃣ Testing default expression...")
        test_ocr_service(text="2x + 3 = 7")
        
        print("\n" + "=" * 60)
        print("💡 Usage:")
        print("   python test_math_ocr.py                    # Test default expression")
        print("   python test_math_ocr.py image.png          # Test specific image")
        print("   python test_math_ocr.py --multiple         # Test multiple expressions")
        print("=" * 60)

if __name__ == "__main__":
    main()
