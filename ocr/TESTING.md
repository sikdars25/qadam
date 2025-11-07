# OCR Testing Guide

Scripts to verify OCR libraries and functionality, including **math expression recognition**.

## 🔬 Math OCR Testing

The OCR service has been optimized for **mathematical expressions** with Latin letters, Greek symbols, and math operators.

### Quick Math Test
```bash
python test_math_ocr.py
```

**Features:**
- ✅ Tests Latin letters (x, y, z, a, b, c)
- ✅ Tests Greek letters (α, β, γ, θ, π)
- ✅ Tests math symbols (√, ∫, ∑, ±, ×, ÷)
- ✅ Tests equations and formulas

**See:** `MATH_OCR_GUIDE.md` for detailed math OCR documentation.

---

## 📋 Available Test Scripts

### 1. Check Libraries (Windows)
```bash
.\check_libraries.bat
```

**What it does:**
- ✅ Activates virtual environment
- ✅ Shows Python version
- ✅ Lists installed OCR packages
- ✅ Runs comprehensive library check

**Output:**
```
✅ Flask               - Version: 3.0.0
✅ EasyOCR             - Version: 1.7.0
✅ Pillow (PIL)        - Version: 9.5.0
✅ NumPy               - Version: 1.24.3
✅ OpenCV              - Version: 4.8.1
✅ PyMuPDF             - Version: 1.23.0
✅ PyTorch             - Version: 2.0.1
```

### 2. Check Libraries (Python)
```bash
python check_ocr_libraries.py
```

**What it does:**
- ✅ Checks all OCR library installations
- ✅ Shows library versions
- ✅ Tests EasyOCR initialization
- ✅ Tests image processing (PIL, NumPy)
- ✅ Tests PDF processing (PyMuPDF)

**Output:**
```
========================================
OCR Libraries Check
========================================

Core Libraries:
✅ Flask               - Version: 3.0.0
✅ EasyOCR             - Version: 1.7.0
...

Running Functionality Tests
========================================
🖼️  Testing image processing...
   ✅ PIL/Pillow: Can create images
   ✅ NumPy: Can convert to array

📑 Testing PDF processing...
   ✅ PyMuPDF version: 1.23.0

📄 Testing EasyOCR initialization...
   ✅ EasyOCR reader created successfully
```

### 3. Test OCR on Image
```bash
python test_ocr_simple.py <image_path>
```

**Example:**
```bash
python test_ocr_simple.py test_image.png
```

**What it does:**
- ✅ Loads your image
- ✅ Initializes EasyOCR
- ✅ Extracts text from image
- ✅ Shows confidence scores
- ✅ Displays bounding boxes

**Output:**
```
========================================
Simple OCR Test
========================================
✅ EasyOCR version: 1.7.0

📄 Loading image: test_image.png
   Image size: (800, 600)
   Image mode: RGB

🔄 Initializing EasyOCR reader...
   ✅ Reader initialized

🔍 Performing OCR...
   ✅ Detected 3 text region(s)

========================================
Extracted Text:
========================================

[1] Text: Hello World
    Confidence: 98.50%
    Bounding box: [[10, 20], [150, 20], [150, 50], [10, 50]]

[2] Text: This is a test
    Confidence: 95.30%
    Bounding box: [[10, 60], [200, 60], [200, 90], [10, 90]]

========================================
Combined Text:
========================================
Hello World This is a test

Average Confidence: 96.90%
```

## 🚀 Quick Start

### Step 1: Activate Virtual Environment
```bash
cd ocr
venv\Scripts\activate.bat
```

### Step 2: Run Library Check
```bash
.\check_libraries.bat
```

### Step 3: Test OCR (Optional)
```bash
# Create a test image with text or use your own
python test_ocr_simple.py your_image.png
```

## 🐛 Troubleshooting

### "EasyOCR not installed"
```bash
pip install easyocr==1.7.0
```

### "NumPy version error"
```bash
pip uninstall numpy
pip install "numpy<2.0.0"
```

### "Pillow version error"
```bash
pip install Pillow==9.5.0
```

### "PyTorch not found"
```bash
pip install torch torchvision
```

### Reinstall all dependencies
```bash
pip install -r requirements.txt
```

## 📊 Expected Results

All libraries should show ✅ (installed):
- Flask
- Flask-CORS
- EasyOCR
- Pillow (PIL)
- NumPy
- OpenCV
- PyMuPDF
- PyTorch

If any show ❌ (not installed), run:
```bash
pip install -r requirements.txt
```

## 💡 Tips

1. **First OCR run is slow** (~10-15 seconds)
   - EasyOCR downloads models on first use
   - Subsequent runs are faster (~2-5 seconds)

2. **Best image quality**
   - Use high-contrast images
   - Clear, readable text
   - PNG or JPG format
   - Minimum 300 DPI for scanned documents

3. **Test with sample images**
   - Screenshots of text
   - Scanned documents
   - Photos with text

## 🔗 Related Files

- `app.py` - Main Flask OCR service
- `requirements.txt` - Python dependencies
- `.env` - Configuration file
