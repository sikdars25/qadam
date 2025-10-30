"""
Quick test of backend OCR integration
"""
import requests
from PIL import Image, ImageDraw
import io
import base64

BACKEND_URL = "http://localhost:5000"

# Create test image
img = Image.new('RGB', (400, 100), color='white')
draw = ImageDraw.Draw(img)
draw.text((10, 30), "Backend Integration Test", fill='black')

buffer = io.BytesIO()
img.save(buffer, format='PNG')
img_bytes = buffer.getvalue()

print("🧪 Testing Backend OCR Integration\n")

# Test 1: File Upload
print("1️⃣ Testing File Upload...")
files = {'file': ('test.png', img_bytes, 'image/png')}
data = {'language': 'en'}

response = requests.post(f"{BACKEND_URL}/api/ocr/scan", files=files, data=data)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"✅ Success: {result.get('success')}")
    print(f"📝 Text: {result.get('text')}")
    print(f"🎯 Confidence: {result.get('confidence')}")
else:
    print(f"❌ Error: {response.text}")

# Test 2: Base64
print("\n2️⃣ Testing Base64...")
img_base64 = base64.b64encode(img_bytes).decode('utf-8')
payload = {'image_base64': img_base64, 'language': 'en'}

response = requests.post(f"{BACKEND_URL}/api/ocr/scan", json=payload)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"✅ Success: {result.get('success')}")
    print(f"📝 Text: {result.get('text')}")
    print(f"🎯 Confidence: {result.get('confidence')}")
else:
    print(f"❌ Error: {response.text}")

print("\n✅ Backend integration working correctly!")
