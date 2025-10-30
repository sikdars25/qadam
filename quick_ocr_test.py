"""
Quick OCR test - Option 1: Simple OCR Extraction
"""
import requests
from PIL import Image, ImageDraw
import io
import time

print("="*60)
print("Testing /api/ocr/extract (Simple OCR - No API Key)")
print("="*60)

# Create test image
print("\n1️⃣ Creating test image...")
img = Image.new('RGB', (500, 100), color='white')
draw = ImageDraw.Draw(img)
draw.text((20, 30), "Sample question text for OCR", fill='black')

buffer = io.BytesIO()
img.save(buffer, format='PNG')
img_bytes = buffer.getvalue()
print("✅ Image created")

# Test OCR extraction
print("\n2️⃣ Calling /api/ocr/extract...")
url = "https://qadam-backend.azurewebsites.net/api/ocr/extract"

files = {'file': ('test.png', img_bytes, 'image/png')}
data = {'language': 'en'}

try:
    start = time.time()
    response = requests.post(url, files=files, data=data, timeout=30)
    elapsed = time.time() - start
    
    print(f"⏱️  Response time: {elapsed:.2f}s")
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n🎉 SUCCESS!")
        print("="*60)
        print(f"✅ Success: {result.get('success')}")
        print(f"📝 Text: '{result.get('text', '')}'")
        print(f"🎯 Confidence: {result.get('confidence', 0):.1%}")
        print(f"📄 Lines: {result.get('lines_detected', 0)}")
        print("="*60)
        print("\n✅ /api/ocr/extract is working perfectly!")
        print("   Use this endpoint for OCR in your application")
    else:
        print(f"\n❌ Error {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("\n⏳ Request timed out")
    print("   OCR service might be cold starting")
    print("   Try again in a few seconds")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60)
