# KaTeX Integration for Mathematical Expression Display

## 🎯 Overview

The AQNAMIC frontend has been enhanced with KaTeX support to display mathematical expressions in beautiful, professional-quality typography. This integration allows users to input mathematical questions using LaTeX syntax and see them rendered as proper mathematical expressions.

## ✨ Features Added

### 📦 Dependencies
- `katex@^0.16.8` - Fast math typesetting library
- `react-katex@^3.0.1` - React components for KaTeX

### 🧮 Mathematical Expression Support

#### LaTeX Syntax Examples

**Inline Math** (using `$...$`):
```latex
$x^2 + y^2 = z^2$
$\frac{a}{b}$
$\sqrt{x^2 + y^2}$
$\alpha + \beta = \gamma$
```

**Display Math** (using `$$...$$`):
```latex
$$\int_0^{\pi} \sin(x) dx$$
$$\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}$$
$$\begin{pmatrix} a & b \\ c & d \end{pmatrix}$$
```

#### Supported Mathematical Elements

**Greek Letters**:
- Lowercase: `\alpha, \beta, \gamma, \delta, \epsilon, \theta, \lambda, \mu, \pi, \sigma, \phi, \omega`
- Uppercase: `\Gamma, \Delta, \Theta, \Lambda, \Pi, \Sigma, \Phi, \Omega`

**Operators**:
- Arithmetic: `+, -, \times, \div, \pm, \mp`
- Relations: `=, \neq, \approx, \equiv, <, >, \leq, \geq`
- Logic: `\forall, \exists, \neg, \land, \lor`

**Calculus**:
- Integrals: `\int, \iint, \iiint, \oint`
- Sums/Products: `\sum, \prod`
- Derivatives: `\partial, \nabla`
- Limits: `\lim`

**Structures**:
- Fractions: `\frac{numerator}{denominator}`
- Roots: `\sqrt{expression}` or `\sqrt[n]{expression}`
- Powers: `x^2` or `x^{n}`
- Subscripts: `x_1` or `x_{n}`

## 🔧 Implementation Details

### Files Modified

1. **`package.json`** - Added KaTeX dependencies
2. **`public/index.html`** - Added KaTeX CSS and Google Fonts
3. **`src/components/SingleQuestionUpload.js`** - Enhanced with math rendering
4. **`src/components/SingleQuestionUpload.css`** - Added math styling
5. **`src/components/MathDisplay.js`** - Created reusable math component
6. **`src/utils/MathProcessor.js`** - Created math processing utilities

### Key Components

#### MathDisplay Component
```javascript
import MathDisplay from './components/MathDisplay';

// Usage
<MathDisplay 
  expression="x^2 + y^2 = z^2" 
  displayMode={false} 
  errorColor="#cc0000"
/>
```

#### MathProcessor Utilities
```javascript
import { 
  renderTextWithMath, 
  containsMathExpressions,
  processSolutionForMath 
} from './utils/MathProcessor';

// Detect math in text
if (containsMathExpressions(text)) {
  // Render with KaTeX
  return renderTextWithMath(text);
}
```

### Enhanced Features

#### 🎨 Visual Improvements
- Professional mathematical typography using KaTeX
- Responsive design for mobile devices
- Enhanced solution display with math highlighting
- Color-coded mathematical expressions

#### 💡 User Experience
- LaTeX syntax hints and examples
- Real-time math expression detection
- Toggle-able example guide
- Enhanced input placeholders with math examples

#### 🔍 Smart Processing
- Automatic detection of mathematical expressions
- LaTeX to Unicode conversion for common symbols
- Error handling for invalid expressions
- Graceful fallback for non-math text

## 📱 Usage Examples

### Example 1: Quadratic Equation
**Input**: `Solve the equation: $$x^2 + 5x + 6 = 0$$`
**Output**: Beautifully rendered quadratic equation with solution steps

### Example 2: Calculus Integral
**Input**: `Find the integral: $$\int_0^{\pi} \sin(x) dx$$`
**Output**: Professional integral notation with step-by-step solution

### Example 3: Algebraic Simplification
**Input**: `Simplify: $\frac{a^2 - b^2}{a - b}$`
**Output**: Proper fraction notation with simplified result

## 🎯 Benefits

1. **Professional Display**: Mathematical expressions look like they're from a textbook
2. **Easy Input**: Users can type standard LaTeX syntax
3. **Automatic Detection**: System automatically identifies and renders math
4. **Error Handling**: Invalid expressions show helpful error messages
5. **Responsive**: Works perfectly on all screen sizes
6. **Fast Rendering**: KaTeX is optimized for speed and quality

## 🚀 Installation and Setup

### Prerequisites
- Node.js 14+ and npm
- Existing React frontend

### Installation Commands
```bash
# Navigate to frontend directory
cd frontend

# Install new dependencies
npm install katex@0.16.8 react-katex@3.0.1

# Start development server
npm start
```

### Verification
1. Open the Single Question Upload modal
2. Click on "Text Input" method
3. Type a mathematical expression like `$x^2 + y^2 = z^2$`
4. See the "🧮 Math expressions detected" indicator
5. Submit the question to see beautifully rendered math

## 🔧 Customization

### CSS Variables
```css
:root {
  --math-font-size: 1.1em;
  --math-color: #2563eb;
  --math-background: #f8f9fa;
}
```

### KaTeX Configuration
```javascript
// Custom KaTeX options
const katexOptions = {
  displayMode: false,
  throwOnError: false,
  errorColor: '#cc0000',
  strict: false
};
```

## 📊 Supported LaTeX Commands

### Basic Math
- `x^2`, `x^{n}` - Powers
- `x_1`, `x_{n}` - Subscripts
- `\frac{a}{b}` - Fractions
- `\sqrt{x}` - Square roots
- `\sqrt[n]{x}` - Nth roots

### Greek Letters
- `\alpha, \beta, \gamma, \delta, \epsilon, \zeta, \eta, \theta`
- `\iota, \kappa, \lambda, \mu, \nu, \xi, \pi, \rho, \sigma, \tau`
- `\upsilon, \phi, \chi, \psi, \omega`
- Uppercase variants available

### Operators
- `\times, \div, \pm, \mp` - Arithmetic
- `\leq, \geq, \neq, \approx, \equiv` - Relations
- `\forall, \exists, \neg, \land, \lor` - Logic
- `\in, \notin, \subset, \supset, \cup, \cap` - Sets

### Calculus
- `\int, \iint, \iiint, \oint` - Integrals
- `\sum, \prod` - Sums and products
- `\partial, \nabla` - Derivatives
- `\lim` - Limits

## 🐛 Troubleshooting

### Common Issues

1. **Math not rendering**:
   - Check that KaTeX CSS is loaded in index.html
   - Verify LaTeX syntax is correct
   - Check browser console for errors

2. **Invalid LaTeX errors**:
   - Use the provided examples as reference
   - Check for missing braces or backslashes
   - Use the "Show Examples" toggle for help

3. **Performance issues**:
   - KaTeX is optimized for speed
   - Large expressions may take longer to render
   - Consider breaking down complex expressions

### Debug Mode
Enable debug logging by checking the browser console for KaTeX rendering messages.

## 📄 License

This KaTeX integration is part of the AQNAMIC educational platform and follows the same licensing terms.

## 🤝 Contributing

To add new mathematical features:
1. Update `MathProcessor.js` utilities
2. Add new examples to the hints section
3. Test with various mathematical expressions
4. Update documentation

---

**Result**: The AQNAMIC frontend now displays mathematical expressions with professional-quality typography, making it perfect for educational content in mathematics, physics, chemistry, and other STEM subjects!
