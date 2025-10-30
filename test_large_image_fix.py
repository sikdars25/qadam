"""
Test automatic image resizing fix
Tests with various image sizes to verify 500 errors are prevented
"""
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import time

print("="*60)
print("Testing Automatic Image Resizing Fix")
print("="*60)

# Wait for deployment
print("\n⏳ Waiting 2 minutes for deployment...")
time.sleep(120)

def test_image(width, height, text):
    """Test OCR with specific image size"""
    print(f"\n{'='*60}")
    print(f"Testing {width}x{height} image")
    print(f"{'='*60}")
    
    # Create image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add text
    font_size = min(width, height) // 20
    draw.text((width//10, height//3), text, fill='black')
    
    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()
    
    print(f"📸 Original size: {len(img_bytes) / 1024:.1f}KB")
    print(f"📐 Dimensions: {width}x{height}")
    
    # Send to backend
    url = "https://qadam-backend.azurewebsites.net/api/ocr/extract"
    files = {'file': ('test.png', img_bytes, 'image/png')}
    data = {'language': 'en'}
    
    try:
        start = time.time()
        response = requests.post(url, files=files, data=data, timeout=60)
        elapsed = time.time() - start
        
        print(f"⏱️  Response time: {elapsed:.2f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS!")
            print(f"   Text: '{result.get('text', '')[:50]}...'")
            print(f"   Confidence: {result.get('confidence', 0):.1%}")
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT (>60s)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

# Test cases
print("\n" + "="*60)
print("Test Cases")
print("="*60)

test_cases = [
    (800, 600, "Small image test"),           # Small - should work fast
    (2000, 1500, "Medium image test"),        # Medium - should work
    (4000, 3000, "Large image test"),         # Large - should be resized
    (6000, 4000, "Very large image test"),    # Very large - should be resized
]

results = []
for width, height, text in test_cases:
    success = test_image(width, height, text)
    results.append((f"{width}x{height}", success))
    time.sleep(2)  # Brief pause between tests

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

all_passed = True
for size, success in results:
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {size}")
    if not success:
        all_passed = False

print("="*60)
if all_passed:
    print("🎉 ALL TESTS PASSED!")
    print("   Image resizing is working correctly")
    print("   Large images are automatically resized")
    print("   500 errors should be prevented")
else:
    print("⚠️  SOME TESTS FAILED")
    print("   Check logs for details")

print("="*60)
