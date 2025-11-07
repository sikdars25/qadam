# Greek Letter OCR Corrections

## 🎯 Overview

The OCR service includes automatic correction for common Greek letter detection errors, specifically addressing issues where the lambda symbol (λ) is incorrectly detected in mathematical expressions.

## 🔧 Supported Corrections

### Primary Corrections
- **λn → 4n** - Lambda with "n" becomes digit 4 with "n"
- **λp → 2p** - Lambda with "p" becomes digit 2 with "p"  
- **λn/λp → ^n Ap** - Lambda division becomes exponent notation

### Extended Corrections
- **λx → 4x**, **λy → 4y**, **λz → 4z** - Lambda with variables
- **λa → 4a**, **λb → 4b**, **λc → 4c** - Lambda with constants
- **λ/ → 4/**, **/λ → /4** - Lambda in division contexts

## 📋 Implementation Details

### Correction Algorithm
1. **Order-Sensitive Processing**: Combined patterns (like `λn/λp`) are processed before individual replacements
2. **Non-Destructive**: Original OCR text is preserved as `raw_text` for debugging
3. **Logging**: All corrections are logged with `🔧 OCR corrections applied:` prefix
4. **UTF-8 Safe**: All processing maintains UTF-8 encoding

### Response Format
```json
{
  "success": true,
  "text": "4n + 2p = ^n Ap",      // Corrected text
  "raw_text": "λn + λp = λn/λp",   // Original OCR text
  "confidence": 0.95,
  "corrections_applied": true,     // Indicates if corrections were made
  "details": [...]
}
```

## 🧪 Testing

Run the test suite to verify corrections:

```bash
cd ocr
python test_greek_corrections.py
```

### Test Cases
- ✅ Lambda n to 4n: `λn = 5` → `4n = 5`
- ✅ Lambda p to 2p: `λp = 10` → `2p = 10`
- ✅ Lambda division: `λn/λp = 0.5` → `^n Ap = 0.5`
- ✅ Multiple corrections: `λx + λy = λz` → `4x + 4y = 4z`
- ✅ No corrections needed: Text without lambda symbols

## 🔍 Health Check

The OCR service health check now includes correction information:

```bash
curl http://localhost:8000/api/health
```

Response includes:
```json
{
  "features": [
    "greek_math_support",
    "utf8_encoding", 
    "lambda_corrections",
    "symbol_recognition"
  ],
  "supported_corrections": [
    "λn → 4n",
    "λp → 2p", 
    "λn/λp → ^n Ap",
    "λx, λy, λz → 4x, 4y, 4z"
  ]
}
```

## 🚀 Usage

### Direct OCR with Corrections
```bash
curl -X POST -F "file=@math_image.png" \
  http://localhost:8000/api/extract-text
```

### Via Proxy Service
```bash
curl -X POST -F "file=@math_image.png" \
  http://localhost:5001/api/extract-text
```

Both endpoints will automatically apply Greek letter corrections.

## ⚙️ Configuration

Corrections are built into the `correct_ocr_greek_letters()` function in `ocr/app.py`. To add new corrections:

1. Add the pattern to the `corrections` list
2. Place more specific patterns first
3. Run the test suite to verify
4. Update this documentation

## 📝 Troubleshooting

### Corrections Not Applied
- Check if the pattern exists in the `corrections` list
- Verify pattern order (specific patterns must come first)
- Check logs for correction messages

### False Corrections
- Review the pattern matching logic
- Consider adding more specific patterns
- Test with the provided test suite

### Performance Impact
- Corrections are applied after OCR processing
- Minimal performance overhead (string replacement)
- Can be disabled by commenting out the correction call

## 🔄 Integration

The correction system integrates seamlessly with:
- **Proxy Service**: Maintains corrections through request routing
- **AI Service**: Receives corrected text for processing
- **Pipeline**: Full end-to-end correction support

All services maintain UTF-8 encoding and preserve the correction metadata throughout the processing pipeline.
