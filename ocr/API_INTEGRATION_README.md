# LaTeX OCR API Integration

This module provides comprehensive OCR text processing for mathematical and scientific questions, converting them to deterministic expressions and solving with free APIs.

## Features

- **Math Expression Detection**: Automatically identifies mathematical expressions in OCR text
- **Multiple API Support**: Integrates with Wolfram Alpha, Symbolab, and SymPy
- **Natural Language Processing**: Handles math problems written in natural language
- **Step-by-Step Solutions**: Generates detailed explanations using Groq AI
- **Multiple Subject Support**: Works for mathematics, physics, chemistry, and more

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Groq API Key (required for final answer generation)
GROQ_API_KEY=your_groq_api_key_here

# Wolfram Alpha App ID (optional but recommended)
WOLFRAM_APP_ID=your_wolfram_app_id_here
```

### Getting API Keys

#### Groq API Key
1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

#### Wolfram Alpha App ID
1. Visit [https://products.wolframalpha.com/api](https://products.wolframalpha.com/api)
2. Sign up for a free account
3. Create a new app
4. Copy the App ID to your `.env` file

## Installation

Install the required dependencies:

```bash
pip install -r proxy/requirements.txt
```

## Usage

### Direct Usage

```python
from latex_ocr_api_integration import LatexOCRIntegration

# Initialize the integration
integration = LatexOCRIntegration()

# Process OCR text
result = integration.process_single_question(
    "Solve the equation: x² + 5x + 6 = 0",
    subject="mathematics"
)

if result['success']:
    print("Solution generated successfully!")
    print(result['final_answer']['answer'])
```

### API Endpoint

Send POST requests to `/api/latex-ocr-solve`:

```json
{
    "ocr_text": "Solve the equation: x² + 5x + 6 = 0",
    "subject": "mathematics"
}
```

## Supported Expression Types

- **Equations**: Linear, quadratic, polynomial equations
- **Derivatives**: Single and multivariable derivatives
- **Integrals**: Definite and indefinite integrals
- **Limits**: Limit calculations
- **Matrices**: Matrix operations
- **Trigonometry**: Sin, cos, tan functions
- **Logarithms**: Log and ln functions
- **Inequalities**: Linear and nonlinear inequalities

## Example Inputs and Outputs

### Input: Quadratic Equation
```
"Solve the equation: x² + 5x + 6 = 0"
```

### Output:
```json
{
    "success": true,
    "original_text": "Solve the equation: x² + 5x + 6 = 0",
    "subject": "mathematics",
    "detected_expressions": [
        {
            "text": "Solve the equation: x² + 5x + 6 = 0",
            "type": "equation",
            "original": "Solve the equation: x² + 5x + 6 = 0"
        }
    ],
    "final_answer": {
        "success": true,
        "answer": "**Step-by-Step Solution:**\n1. Identify the quadratic equation: x² + 5x + 6 = 0\n2. Factor the equation: (x + 2)(x + 3) = 0\n3. Set each factor to zero: x + 2 = 0 or x + 3 = 0\n4. Solve for x: x = -2 or x = -3\n\n**Final Answer:**\nx = -2 or x = -3"
    }
}
```

## Error Handling

The system includes comprehensive error handling:

- **Missing API Keys**: Graceful fallback to available APIs
- **Invalid Expressions**: Attempts multiple parsing strategies
- **Network Errors**: Automatic retry with exponential backoff
- **API Failures**: Falls back to alternative APIs

## Testing

Run the test suite:

```bash
cd ocr
python latex_ocr_api_integration.py
```

This will test the integration with sample mathematical problems.

## Architecture

The system consists of several components:

1. **MathExpressionDetector**: Identifies mathematical expressions in text
2. **ExpressionConverter**: Converts text to mathematical formats
3. **FreeMathAPIs**: Interfaces with external math APIs
4. **GroqAnswerGenerator**: Creates final explanations
5. **LatexOCRIntegration**: Main orchestrator class

## Integration with Existing OCR System

This API integration module is designed to work alongside the existing LaTeX OCR system:

- `latex_ocr_integration.py`: Core OCR processing (existing)
- `latex_ocr_api_integration.py`: API-based solving (new)
- `proxy/app.py`: Flask API endpoint (new)

The two systems can be used independently or together for comprehensive mathematical problem solving.

## Production Deployment

For production deployment:

1. Set up proper JWT authentication in the Flask app
2. Configure rate limiting for API endpoints
3. Set up monitoring and logging
4. Configure reverse proxy (nginx)
5. Set up SSL/TLS certificates
6. Configure environment variables for production

## License

This module is part of the Qadam educational platform project.
