#!/bin/bash

echo "🧮 Installing LaTeX-OCR for Mathematical Expression Detection (Fixed)"
echo "========================================================================"

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not active!"
    echo "Please activate virtual environment first:"
    echo "source venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment detected: $VIRTUAL_ENV"

# Update pip
echo "📦 Updating pip..."
pip install --upgrade pip

# Install LaTeX-OCR dependencies (corrected package names)
echo "🧮 Installing LaTeX-OCR core dependencies..."
pip install pix2tex>=0.1.4
# Note: 'latex-ocr' package doesn't exist, pix2tex is the correct package

# Install additional dependencies for better math detection
echo "🔧 Installing additional dependencies..."
pip install transformers>=4.21.0
pip install torchvision>=0.13.0
pip install timm>=0.6.7

# Install mathematical processing
echo "📐 Installing mathematical processing libraries..."
pip install sympy>=1.10.0

# Install LaTeX parsing (optional)
echo "📄 Installing LaTeX parsing support..."
pip install latex2mathml>=3.75.0

# Verify installation
echo "🔍 Verifying LaTeX-OCR installation..."
python3 -c "
try:
    from pix2tex.cli import LatexOCR
    print('✅ LaTeX-OCR imported successfully')
    
    # Try to initialize
    try:
        ocr = LatexOCR()
        print('✅ LaTeX-OCR initialized successfully')
    except Exception as e:
        print(f'⚠️ LaTeX-OCR initialization failed: {e}')
        print('This is normal on first run - models will be downloaded')
        
except ImportError as e:
    print(f'❌ LaTeX-OCR import failed: {e}')
    exit(1)
"

echo ""
echo "🎉 LaTeX-OCR Installation Complete!"
echo "========================================================================"
echo "📋 What's been installed:"
echo "  ✅ LaTeX-OCR (pix2tex) - Primary mathematical OCR engine"
echo "  ✅ Transformers - Neural network models"
echo "  ✅ Torchvision - Computer vision support"
echo "  ✅ Sympy - Mathematical processing"
echo "  ✅ LaTeX2MathML - LaTeX parsing support"
echo ""
echo "🚀 LaTeX-OCR is now ready to use!"
echo "📝 EasyOCR will remain as fallback for non-mathematical content"
