# Mathematical Symbol OCR Corrections

## 🎯 Overview

The OCR service includes comprehensive correction mechanisms for common mathematical symbol detection errors. These corrections address specific OCR issues with Greek letters, vector notation, mathematical expressions, and scientific notation.

## 🔧 Supported Corrections

### 1. τ (Tau) Detection Issues
**Problem**: τ (tau) is incorrectly detected as T in mathematical contexts.

**Corrections Applied**:
- `torque T` → `torque τ`
- `shear stress T` → `shear stress τ`
- `time constant T` → `time constant τ`
- `angular period T` → `angular period τ`
- `=T a` → `=τa` (mathematical contexts)
- `a T=` → `aτ=` (mathematical contexts)

**Examples**:
```python
Input:  "torque T is applied to the system"
Output: "torque τ is applied to the system"

Input:  "shear stress T = 10 MPa"
Output: "shear stress τ = 10 MPa"
```

### 2. Vector Arrow Detection
**Problem**: Vector arrows (→) are not detected above letters and vector notation gets split.

**Corrections Applied**:
- `vec a` → `→a`
- `a vec` → `a→`
- `vector a` → `→a`
- `a vector` → `a→`
- `-> a` → `→a`
- `a ->` → `a→`

**Examples**:
```python
Input:  "vec a is the velocity vector"
Output: "→a is the velocity vector"

Input:  "force vector is -> F"
Output: "force vector is →F"
```

### 3. Single Letter with Prefix/Suffix Splitting
**Problem**: Mathematical expressions with combined characters are incorrectly split into separate tokens.

**Corrections Applied**:
- `λ n` → `λn`
- `λ p` → `λp`
- `α n` → `αn`
- `β n` → `βn`
- `θ n` → `θn`
- `μ 0` → `μ₀`
- `σ 2` → `σ²`
- `a 1` → `a1`
- `f ( x )` → `f(x)`
- `sin ( x )` → `sin(x)`
- `cos ( x )` → `cos(x)`
- `tan ( x )` → `tan(x)`
- `log ( x )` → `log(x)`
- `ln ( x )` → `ln(x)`

**Examples**:
```python
Input:  "λ n = 5 and λ p = 10"
Output: "λn = 5 and λp = 10"

Input:  "f ( x ) = x ^ 2"
Output: "f(x) = x^2"
```

### 4. Power Digits and Exponential Notation
**Problem**: Power digits and exponential expressions are not detected correctly.

**Corrections Applied**:
- `x ^ 2` → `x^2`
- `x ^ -2` → `x^-2`
- `x2` → `x^2` (for common variables: x, y, z, e)
- `e ^ 2` → `e^2`
- `e ^ -3` → `e^-3`
- `10 ^ 6` → `10^6`
- `10 ^ -6` → `10^-6`

**Examples**:
```python
Input:  "x ^ 2 = 4 and x ^ -2 = 0.25"
Output: "x^2 = 4 and x^-2 = 0.25"

Input:  "e ^ 2 = 7.389 and e ^ -3 = 0.049"
Output: "e^2 = 7.389 and e^-3 = 0.049"
```

### 5. Scientific Notation
**Problem**: Scientific notation with 'e' is not properly formatted.

**Corrections Applied**:
- `1.2 e 3` → `1.2e3`
- `1.2 e -3` → `1.2e-3`
- `5 e 6` → `5e6`
- `5 e -6` → `5e-6`

**Examples**:
```python
Input:  "1.2 e 3 = 1200 and 1.2 e -3 = 0.0012"
Output: "1.2e3 = 1200 and 1.2e-3 = 0.0012"
```

### 6. Parentheses and Brackets Cleanup
**Problem**: Mathematical expressions in parentheses/brackets have incorrect spacing.

**Corrections Applied**:
- `( x + y )` → `(x+y)`
- `[ a + b ]` → `[a+b]`
- `{ x - y }` → `{x-y}`
- `( a - b )` → `(a-b)`
- `( a * b )` → `(a*b)`
- `( a / b )` → `(a/b)`

**Examples**:
```python
Input:  "( x + y ) = 5 and [ a + b ] = 10"
Output: "(x+y) = 5 and [a+b] = 10"
```

## 📋 Implementation Details

### Correction Algorithm
1. **Order-Sensitive Processing**: Corrections are applied in specific order to avoid conflicts
2. **Pattern-Based Matching**: Uses regex patterns to identify specific OCR errors
3. **Context-Aware Corrections**: Some corrections depend on mathematical context
4. **Non-Destructive**: Original OCR text preserved as `raw_text` for debugging

### Response Format
```json
{
  "success": true,
  "text": "λn + λp = λn/λp",  // Corrected text
  "raw_text": "λ n + λ p = λ n / λ p",  // Original OCR text
  "confidence": 0.95,
  "corrections_applied": true,  // Indicates if corrections were made
  "details": [...]
}
```

### Logging
All corrections are logged with detailed information:
```
🔧 Math symbol corrections applied: T → τ, combined split characters, power/exponential fixed
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd ocr
python test_math_corrections.py
```

### Test Coverage
- **30 test cases** covering all correction types
- **100% passing rate** for current implementation
- **Edge cases** and boundary conditions tested
- **Regression prevention** with comprehensive coverage

### Test Categories
1. **Tau detection**: 4 tests
2. **Vector arrows**: 4 tests
3. **Combined characters**: 6 tests
4. **Power/exponential**: 8 tests
5. **Parentheses/brackets**: 6 tests
6. **No corrections needed**: 2 tests

## 🔍 Health Check

The OCR service health check shows correction capabilities:

```bash
curl http://localhost:8000/api/health
```

Response includes:
```json
{
  "features": [
    "greek_math_support",
    "utf8_encoding", 
    "symbol_recognition",
    "latin_language_support",
    "math_corrections",
    "tau_detection",
    "vector_arrows",
    "power_exponentials",
    "parentheses_brackets"
  ],
  "supported_corrections": [
    "τ (tau) detection",
    "Vector arrows (→)",
    "Combined characters (λn, λp)",
    "Power/exponential notation",
    "Parentheses/brackets cleanup"
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

Both endpoints automatically apply mathematical symbol corrections.

## ⚙️ Configuration

### OCR Configuration
```python
ocr_reader = easyocr.Reader(
    ['en', 'la'],  # English + Latin for math expressions
    gpu=False,
    recog_network='latin_g2'  # Best for Greek symbols
)
```

### Correction Function
```python
def correct_math_symbols(text):
    """Apply comprehensive mathematical symbol corrections"""
    # 1. Tau corrections
    # 2. Vector arrow corrections  
    # 3. Combined character corrections
    # 4. Power/exponential corrections
    # 5. Scientific notation corrections
    # 6. Parentheses/brackets corrections
    return corrected_text
```

## 📝 Important Notes

### Correction Order
Corrections are applied in specific order to avoid conflicts:
1. **Tau detection** (context-specific)
2. **Vector arrows** (pattern matching)
3. **Combined characters** (splitting fixes)
4. **Power/exponential** (notation fixes)
5. **Scientific notation** (format fixes)
6. **Parentheses/brackets** (spacing cleanup)

### UTF-8 Encoding
- All text processing maintains UTF-8 encoding
- Greek characters and mathematical symbols preserved
- No character loss during transmission

### Performance Impact
- **Minimal overhead**: Regex-based corrections are efficient
- **Logging enabled**: Detailed logging for debugging
- **Configurable**: Corrections can be disabled if needed

## 🔧 Troubleshooting

### Common Issues

1. **Over-correction**: If corrections are too aggressive, adjust regex patterns
2. **Missing corrections**: Add new patterns to correction lists
3. **Performance issues**: Optimize regex patterns for better performance
4. **Encoding problems**: Ensure UTF-8 encoding throughout pipeline

### Debug Information
- Check `raw_text` field to see original OCR output
- Monitor logs for correction details
- Use test suite to verify specific corrections

## 📈 Benefits

1. **Improved Accuracy**: Mathematical expressions corrected to standard notation
2. **Better Readability**: Clean, properly formatted mathematical expressions
3. **Enhanced Processing**: Corrected text works better with downstream AI processing
4. **Consistency**: Standardized mathematical notation across all documents
5. **Debugging Support**: Original text preserved for troubleshooting

The mathematical symbol correction system significantly improves the quality and accuracy of OCR-processed mathematical content, making it more suitable for educational and scientific applications.
