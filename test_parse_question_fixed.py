"""
Test /api/parse-single-question after fix
Should now work WITHOUT GROQ_API_KEY
"""
import requests
from PIL import Image, ImageDraw
import io
import time

print("="*60)
print("Testing /api/parse-single-question (Fixed)")
print("="*60)

# Wait for deployment
print("\n⏳ Waiting 2 minutes for deployment...")
time.sleep(120)

# Create test image
print("\n1️⃣ Creating test image...")
img = Image.new('RGB', (600, 100), color='white')
draw = ImageDraw.Draw(img)
draw.text((20, 30), "What is photosynthesis?", fill='black')

buffer = io.BytesIO()
img.save(buffer, format='PNG')
img_bytes = buffer.getvalue()
print("✅ Image created")

# Test parse-single-question
print("\n2️⃣ Calling /api/parse-single-question...")
url = "https://qadam-backend.azurewebsites.net/api/parse-single-question"

files = {'file': ('test.png', img_bytes, 'image/png')}
data = {
    'input_type': 'file',
    'file_type': 'png'
}

try:
    start = time.time()
    response = requests.post(url, files=files, data=data, timeout=180)
    elapsed = time.time() - start
    
    print(f"⏱️  Response time: {elapsed:.2f}s")
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n🎉 SUCCESS!")
        print("="*60)
        print(f"✅ Success: {result.get('success')}")
        print(f"📝 Question Text: '{result.get('question_text', result.get('extracted_text', ''))}'")
        print(f"🤖 AI Parsing: {result.get('ai_parsing', 'N/A')}")
        print(f"💬 Message: {result.get('message', 'N/A')}")
        print("="*60)
        
        if result.get('ai_parsing') == False:
            print("\n✅ Working correctly WITHOUT GROQ_API_KEY!")
            print("   OCR text is returned without AI parsing")
            print("   Set GROQ_API_KEY to enable AI-powered parsing")
        else:
            print("\n✅ Working with AI parsing (GROQ_API_KEY is set)")
    else:
        print(f"\n❌ Error {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("\n⏳ Request timed out")
    print("   Try again in a few seconds")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60)
