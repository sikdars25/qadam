# Quick Start: Math OCR Testing

## 🚀 Setup (One-time)

1. **Pull latest code** (if not already done):
   ```bash
   cd d:\AI\_Programs\CBSE\aqnamic
   git pull origin backend-ocr
   ```

2. **Setup OCR service** (if not already done):
   ```bash
   .\setup_ocr_only.bat
   ```

## ▶️ Start OCR Service

```bash
cd ocr
.\run_ocr_only.bat
```

**First run:** Will download Latin language models (~50-100MB, one-time)
**Wait for:** "✅ EasyOCR initialized with math support"

## 🧪 Test Math Recognition

### Option 1: Quick Test
```bash
python test_math_ocr.py
```
Tests: `2x + 3 = 7`

### Option 2: Multiple Tests
```bash
python test_math_ocr.py --multiple
```
Tests 8 different math expressions

### Option 3: Your Image
```bash
python test_math_ocr.py your_image.png
```

## 📊 What Changed?

| Before | After |
|--------|-------|
| English only | English + Latin |
| Missing x, y, z | ✅ Recognizes variables |
| Missing Greek letters | ✅ Recognizes α, β, θ, π |
| Basic symbols only | ✅ Math symbols (√, ∫, ∑) |

## ✅ Supported Math Content

- **Variables**: x, y, z, a, b, c
- **Greek**: α, β, γ, θ, π, Σ, Ω
- **Operators**: +, -, ×, ÷, =, ≠, ≤, ≥
- **Advanced**: √, ∫, ∑, ∏, ∂, ∇

## 🔍 Check Service Status

```bash
curl http://localhost:5001/api/health
```

Should show:
```json
{
  "status": "healthy",
  "ocr_engine": "EasyOCR",
  "features": ["math_detection", "greek_letters", "lightweight"]
}
```

## 📚 More Info

- **Detailed Guide**: `MATH_OCR_GUIDE.md`
- **All Changes**: `MATH_OCR_CHANGES.md`
- **General Testing**: `TESTING.md`

## 🆘 Troubleshooting

### Service won't start
```bash
# Check if port 5001 is in use
netstat -ano | findstr :5001

# Kill process if needed
taskkill /PID <PID> /F
```

### Latin models not downloading
- Check internet connection
- Check firewall settings
- Models download to `ocr/models/` folder

### Low accuracy
- Use higher resolution images (>800px)
- Ensure good contrast
- Make sure text is horizontal
- Avoid blurry or noisy images

## 💡 Tips

1. **First run is slow**: Latin models download once
2. **Image quality matters**: Higher resolution = better results
3. **Check confidence scores**: Low confidence may indicate issues
4. **Test incrementally**: Start with simple expressions

---

**Ready to test?** Run: `python test_math_ocr.py`
