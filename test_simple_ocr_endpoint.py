"""
Test the new simple OCR endpoint
This bypasses question parsing and tests OCR integration directly
"""
import requests
from PIL import Image, ImageDraw
import io
import time

# Create test image
print("Creating test image...")
img = Image.new('RGB', (600, 150), color='white')
draw = ImageDraw.Draw(img)
draw.text((20, 50), "What is the capital of France?", fill='black')

buffer = io.BytesIO()
img.save(buffer, format='PNG')
img_bytes = buffer.getvalue()

print("✅ Image created\n")

# Wait for deployment
print("⏳ Waiting for backend deployment to complete...")
print("   (GitHub Actions takes ~2-3 minutes)")
time.sleep(10)

# Test the new simple OCR endpoint
print("\n" + "="*60)
print("Testing /api/ocr/extract endpoint")
print("="*60)

url = "https://qadam-backend.azurewebsites.net/api/ocr/extract"

files = {'file': ('test.png', img_bytes, 'image/png')}
data = {'language': 'en'}

try:
    print("\n📤 Sending request...")
    print("   This tests: Frontend → Backend → OCR Service → Backend")
    print("   Expected time: 2-10 seconds\n")
    
    start_time = time.time()
    response = requests.post(url, files=files, data=data, timeout=180)
    elapsed = time.time() - start_time
    
    print(f"⏱️  Response time: {elapsed:.2f} seconds")
    print(f"📊 Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        
        print("🎉 SUCCESS! OCR Integration is Working!")
        print("="*60)
        print(f"✅ Success: {result.get('success')}")
        print(f"📝 Extracted Text: '{result.get('text', '')}'")
        print(f"🎯 Confidence: {result.get('confidence', 0):.1%}")
        print(f"📄 Lines Detected: {result.get('lines_detected', 0)}")
        print(f"💬 Message: {result.get('message', '')}")
        
        if result.get('details'):
            print(f"\n📋 Details:")
            for i, detail in enumerate(result.get('details', []), 1):
                print(f"   Line {i}: '{detail.get('text', '')}' (confidence: {detail.get('confidence', 0):.1%})")
        
        print("\n" + "="*60)
        print("✅ Backend → OCR Service integration is WORKING!")
        print("="*60)
        
    elif response.status_code == 404:
        print("❌ Endpoint not found (404)")
        print("   The deployment might not be complete yet.")
        print("   Wait a few minutes and try again.")
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out after 180 seconds")
    print("   The OCR service might be downloading models")
    print("   This should only happen on first run")
    
except requests.exceptions.ConnectionError:
    print("❌ Connection error")
    print("   Check if the backend is running")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("Test complete!")
print("="*60)
