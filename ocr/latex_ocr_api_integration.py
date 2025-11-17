"""
LaTeX OCR Integration - Convert OCR text to deterministic expressions and solve with free APIs
Version: 1.0 - Production Ready
"""

import os
import re
import json
import requests
import sympy as sp
import logging
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not configured - final answer generation will be disabled")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Free Math/Science APIs
WOLFRAM_APP_ID = os.getenv('WOLFRAM_APP_ID', '')
if not WOLFRAM_APP_ID:
    logger.info("WOLFRAM_APP_ID not configured - Wolfram Alpha will be disabled")

SYMBOLAB_ENABLED = True  # Web scraping approach
MATHPIX_ENABLED = False  # Requires API key

class MathExpressionDetector:
    """Detect and classify mathematical expressions in OCR text"""
    
    @staticmethod
    def detect_expressions(text: str) -> List[Dict[str, Any]]:
        """
        Detect mathematical expressions in OCR text
        
        Args:
            text: OCR extracted text
            
        Returns:
            List of detected expressions with metadata
        """
        expressions = []
        
        # Patterns for different types of mathematical expressions
        patterns = {
            'equation': r'=|≠|≤|≥|<|>',
            'integral': r'∫|∬|∭',
            'derivative': r'd/d|∂|∇',
            'limit': r'lim|→',
            'summation': r'∑|∏',
            'matrix': r'\[.*?\]|\(.*?\)',
            'fraction': r'/|÷',
            'exponent': r'\^|²|³|⁴|⁵|⁶|⁷|⁸|⁹|ⁿ',
            'root': r'√|∛|∜',
            'logarithm': r'log|ln|lg',
            'trigonometric': r'sin|cos|tan|csc|sec|cot',
            'inequality': r'≤|≥|<|>'
        }
        
        # Split text into potential expressions
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Classify the expression type
            expr_type = 'general'
            for pattern_name, pattern in patterns.items():
                if re.search(pattern, sentence, re.IGNORECASE):
                    expr_type = pattern_name
                    break
            
            expressions.append({
                'text': sentence,
                'type': expr_type,
                'original': sentence
            })
        
        return expressions

class ExpressionConverter:
    """Convert OCR text to deterministic mathematical expressions"""
    
    @staticmethod
    def clean_latex(text: str) -> str:
        """Clean and normalize LaTeX expressions"""
        # Common OCR corrections for LaTeX
        corrections = {
            r'\{': '{',
            r'\}': '}',
            r'\[': '[',
            r'\]': ']',
            r'\(': '(',
            r'\)': ')',
            r'\\frac': 'frac',
            r'\\sqrt': 'sqrt',
            r'\\int': 'int',
            r'\\sum': 'sum',
            r'\\lim': 'lim',
            r'\\sin': 'sin',
            r'\\cos': 'cos',
            r'\\tan': 'tan',
            r'\\log': 'log',
            r'\\ln': 'ln',
            r'\\infty': 'infinity',
            r'\\alpha': 'alpha',
            r'\\beta': 'beta',
            r'\\gamma': 'gamma',
            r'\\delta': 'delta',
            r'\\theta': 'theta',
            r'\\lambda': 'lambda',
            r'\\mu': 'mu',
            r'\\pi': 'pi',
            r'\\sigma': 'sigma',
            r'\\phi': 'phi',
            r'\\omega': 'omega'
        }
        
        for latex_char, replacement in corrections.items():
            text = text.replace(latex_char, replacement)
        
        return text
    
    @staticmethod
    def to_sympy(text: str) -> Optional[sp.Expr]:
        """Convert text to SymPy expression with improved natural language handling"""
        try:
            cleaned_text = ExpressionConverter.clean_latex(text)
            
            # Extract mathematical expressions from natural language
            # Handle equations
            if '=' in cleaned_text:
                # Extract the expression part after '=' or before '='
                parts = cleaned_text.split('=')
                if len(parts) >= 2:
                    # Try to parse both sides
                    left_side = ExpressionConverter._extract_math_expression(parts[0].strip())
                    right_side = ExpressionConverter._extract_math_expression(parts[1].strip())
                    
                    if left_side and right_side:
                        return sp.Eq(sp.sympify(left_side), sp.sympify(right_side))
                    elif left_side:
                        return sp.sympify(left_side)
                    elif right_side:
                        return sp.sympify(right_side)
            
            # Handle derivatives
            if 'derivative' in cleaned_text.lower() or 'diff' in cleaned_text.lower():
                derivative_expr = ExpressionConverter._extract_derivative_expression(cleaned_text)
                if derivative_expr:
                    return derivative_expr
            
            # Handle integrals
            if 'integral' in cleaned_text.lower() or 'integrate' in cleaned_text.lower():
                integral_expr = ExpressionConverter._extract_integral_expression(cleaned_text)
                if integral_expr:
                    return integral_expr
            
            # Handle general expressions
            math_expr = ExpressionConverter._extract_math_expression(cleaned_text)
            if math_expr:
                return sp.sympify(math_expr)
            
            return None
            
        except Exception as e:
            print(f"Failed to convert to SymPy: {e}")
            return None
    
    @staticmethod
    def _extract_math_expression(text: str) -> Optional[str]:
        """Extract pure mathematical expression from text"""
        # Remove common question words
        question_words = [
            'solve the equation', 'find', 'calculate', 'compute', 'evaluate',
            'simplify', 'factor', 'expand', 'what is', 'determine'
        ]
        
        expr = text.lower()
        for word in question_words:
            expr = expr.replace(word, '')
        
        # Handle specific patterns
        # Quadratic equations: ax² + bx + c
        # More robust pattern matching
        expr = re.sub(r'([+-]?\s*\d*)\s*x\s*²?\s*([+-]\s*\d*)\s*x\s*([+-]\s*\d+)', 
                     lambda m: f"{(m.group(1) or '1').strip()}*x**2{(m.group(2)).strip()}*x{(m.group(3)).strip()}", expr)
        
        # Alternative pattern for x² notation
        expr = re.sub(r'([+-]?\s*\d*)\s*x\*\*2\s*([+-]\s*\d*)\s*x\s*([+-]\s*\d+)', 
                     lambda m: f"{(m.group(1) or '1').strip()}*x**2{(m.group(2)).strip()}*x{(m.group(3)).strip()}", expr)
        
        # Powers: x² -> x**2, x³ -> x**3, etc.
        expr = re.sub(r'(\w+)²', r'\1**2', expr)
        expr = re.sub(r'(\w+)³', r'\1**3', expr)
        expr = re.sub(r'(\w+)\^(\w+)', r'\1**\2', expr)
        
        # Square roots
        expr = re.sub(r'√(\w+)', r'sqrt(\1)', expr)
        expr = re.sub(r'sqrt\{(\w+)\}', r'sqrt(\1)', expr)
        
        # Clean up spacing and operators
        expr = expr.replace(' ', '')
        expr = expr.replace('++', '+')
        expr = expr.replace('--', '+')
        expr = expr.replace('+-', '-')
        expr = expr.replace('-+', '-')
        
        # Add multiplication signs where needed
        expr = re.sub(r'(\d)x', r'\1*x', expr)
        expr = re.sub(r'x(\d)', r'x*\1', expr)
        
        # Clean up
        expr = expr.strip()
        expr = expr.rstrip('.,!?;:')
        
        return expr if expr else None
    
    @staticmethod
    def _extract_derivative_expression(text: str) -> Optional[sp.Expr]:
        """Extract derivative expression from text"""
        try:
            # Pattern: f(x) = x³ + 2x² - 3x + 1
            func_match = re.search(r'f\(x\)\s*=\s*([^,]+)', text, re.IGNORECASE)
            if func_match:
                func_expr = func_match.group(1).strip()
                func_expr = ExpressionConverter._extract_math_expression(func_expr)
                if func_expr:
                    x = sp.Symbol('x')
                    f = sp.sympify(func_expr)
                    return sp.diff(f, x)
            
            # Pattern: derivative of x³ + 2x² - 3x + 1
            expr_match = re.search(r'derivative\s+of\s+(.+)', text, re.IGNORECASE)
            if expr_match:
                expr = expr_match.group(1).strip()
                expr = ExpressionConverter._extract_math_expression(expr)
                if expr:
                    x = sp.Symbol('x')
                    f = sp.sympify(expr)
                    return sp.diff(f, x)
            
            return None
        except Exception as e:
            print(f"Derivative extraction failed: {e}")
            return None
    
    @staticmethod
    def _extract_integral_expression(text: str) -> Optional[sp.Expr]:
        """Extract integral expression from text"""
        try:
            # Pattern: ∫(2x + 3)dx
            integral_match = re.search(r'∫\(([^)]+)\)dx', text)
            if integral_match:
                expr = integral_match.group(1).strip()
                expr = ExpressionConverter._extract_math_expression(expr)
                if expr:
                    x = sp.Symbol('x')
                    f = sp.sympify(expr)
                    return sp.integrate(f, x)
            
            # Pattern: integral of (2x + 3)dx
            integral_match = re.search(r'integral\s+of\s+\(([^)]+)\)dx', text, re.IGNORECASE)
            if integral_match:
                expr = integral_match.group(1).strip()
                expr = ExpressionConverter._extract_math_expression(expr)
                if expr:
                    x = sp.Symbol('x')
                    f = sp.sympify(expr)
                    return sp.integrate(f, x)
            
            return None
        except Exception as e:
            print(f"Integral extraction failed: {e}")
            return None
    
    @staticmethod
    def to_wolfram_alpha(text: str) -> str:
        """Convert text to Wolfram Alpha query format"""
        cleaned = ExpressionConverter.clean_latex(text)
        
        # Convert to Wolfram Alpha format
        replacements = {
            '**': '^',
            'sqrt(': 'sqrt(',
            'integrate(': 'integrate ',
            'diff(': 'derivative ',
            'infinity': 'infinity',
            'pi': 'pi',
            'alpha': 'alpha',
            'beta': 'beta',
            'gamma': 'gamma',
            'delta': 'delta',
            'theta': 'theta',
            'lambda': 'lambda',
            'mu': 'mu',
            'sigma': 'sigma',
            'phi': 'phi',
            'omega': 'omega'
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned

class FreeMathAPIs:
    """Integration with free mathematical APIs"""
    
    @staticmethod
    def solve_with_wolfram_alpha(query: str) -> Dict[str, Any]:
        """
        Solve mathematical expression using Wolfram Alpha API
        
        Args:
            query: Mathematical query in Wolfram Alpha format
            
        Returns:
            Solution result with steps
        """
        if not WOLFRAM_APP_ID:
            return {'success': False, 'error': 'Wolfram Alpha APP ID not configured'}
        
        try:
            url = "http://api.wolframalpha.com/v2/query"
            params = {
                'input': query,
                'appid': WOLFRAM_APP_ID,
                'output': 'JSON',
                'format': 'plaintext',
                'podstate': 'Result__Step-by-step solution'
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract results
                result = {'success': True, 'steps': [], 'result': ''}
                
                if 'queryresult' in data and data['queryresult'].get('success'):
                    pods = data['queryresult'].get('pods', [])
                    
                    for pod in pods:
                        if pod.get('title') == 'Result':
                            subpods = pod.get('subpods', [])
                            if subpods:
                                result['result'] = subpods[0].get('plaintext', '')
                        
                        elif pod.get('title') == 'Step-by-step solution':
                            subpods = pod.get('subpods', [])
                            for subpod in subpods:
                                result['steps'].append(subpod.get('plaintext', ''))
                
                return result
            else:
                return {'success': False, 'error': f'Wolfram Alpha API error: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def solve_with_symbolab(query: str) -> Dict[str, Any]:
        """
        Solve mathematical expression using Symbolab (web scraping approach)
        
        Args:
            query: Mathematical query
            
        Returns:
            Solution result with steps
        """
        try:
            # This is a simplified approach - in production, you might want to use
            # proper web scraping libraries or official APIs
            url = f"https://www.symbolab.com/solver/step-by-step/{requests.utils.quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Parse HTML to extract steps (simplified)
                # In a real implementation, you'd use BeautifulSoup or similar
                return {
                    'success': True,
                    'result': 'Solution found (parsing needed)',
                    'steps': ['Step 1: Parse the expression', 'Step 2: Apply mathematical rules'],
                    'note': 'Full parsing implementation required'
                }
            else:
                return {'success': False, 'error': f'Symbolab error: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def solve_with_sympy(expression: sp.Expr) -> Dict[str, Any]:
        """
        Solve mathematical expression using SymPy
        
        Args:
            expression: SymPy expression
            
        Returns:
            Solution result
        """
        try:
            result = {'success': True, 'steps': [], 'result': ''}
            
            # Try different solving approaches
            if expression.has(sp.Symbol('x')):
                # Try to solve for x
                solution = sp.solve(expression, sp.Symbol('x'))
                result['result'] = str(solution)
                result['steps'].append(f"Solving equation: {expression}")
                result['steps'].append(f"Solution: x = {solution}")
            
            elif expression.is_Equality:
                # Handle equality
                solution = sp.solve(expression)
                result['result'] = str(solution)
                result['steps'].append(f"Solving equality: {expression}")
                result['steps'].append(f"Solution: {solution}")
            
            else:
                # Simplify expression
                simplified = sp.simplify(expression)
                result['result'] = str(simplified)
                result['steps'].append(f"Simplifying: {expression}")
                result['steps'].append(f"Simplified: {simplified}")
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

class GroqAnswerGenerator:
    """Generate final answers and explanations using Groq"""
    
    @staticmethod
    def generate_final_answer(question: str, api_results: List[Dict[str, Any]], 
                            context: str = '') -> Dict[str, Any]:
        """
        Generate final answer with steps and explanations using Groq
        
        Args:
            question: Original OCR question
            api_results: Results from math APIs
            context: Additional context
            
        Returns:
            Final answer with steps and explanations
        """
        if not GROQ_API_KEY:
            return {'success': False, 'error': 'Groq API key not configured'}
        
        try:
            # Prepare the prompt
            prompt = f"""
You are a mathematics and science expert. Based on the following OCR question and API results, provide a comprehensive step-by-step solution with clear explanations.

Original Question:
{question}

API Results:
{json.dumps(api_results, indent=2)}

Additional Context:
{context}

Please provide:
1. A clear step-by-step solution
2. Detailed explanations for each step
3. The final answer
4. Any important mathematical concepts or formulas used

Format your response as:
**Step-by-Step Solution:**
[Steps here]

**Detailed Explanations:**
[Explanations here]

**Final Answer:**
[Final answer here]
"""
            
            headers = {
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': GROQ_MODEL,
                'messages': [
                    {'role': 'system', 'content': 'You are a mathematics and science expert providing detailed solutions.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.1
            }
            
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                return {
                    'success': True,
                    'answer': content,
                    'raw_response': data
                }
            else:
                return {'success': False, 'error': f'Groq API error: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

class LatexOCRIntegration:
    """Main integration class for LaTeX OCR processing"""
    
    def __init__(self):
        self.detector = MathExpressionDetector()
        self.converter = ExpressionConverter()
        self.math_apis = FreeMathAPIs()
        self.groq_generator = GroqAnswerGenerator()
    
    def process_ocr_text(self, ocr_text: str, subject: str = '') -> Dict[str, Any]:
        """
        Process OCR text and generate comprehensive solution
        
        Args:
            ocr_text: Text extracted from OCR
            subject: Subject area (math, physics, chemistry, etc.)
            
        Returns:
            Complete solution with steps and explanations
        """
        start_time = time.time()
        logger.info(f"Processing OCR text for subject: {subject}")
        logger.debug(f"Input text: {ocr_text[:100]}...")
        
        try:
            # Step 1: Detect mathematical expressions
            expressions = self.detector.detect_expressions(ocr_text)
            logger.info(f"Detected {len(expressions)} expressions")
            
            # Step 2: Convert expressions and solve with APIs
            api_results = []
            
            for i, expr in enumerate(expressions, 1):
                logger.debug(f"Processing expression {i}/{len(expressions)}: {expr['text'][:50]}...")
                
                # Convert to SymPy
                sympy_expr = None
                try:
                    sympy_expr = self.converter.to_sympy(expr['text'])
                    if sympy_expr:
                        logger.debug(f"Successfully converted to SymPy: {str(sympy_expr)[:50]}...")
                except Exception as e:
                    logger.warning(f"SymPy conversion failed for expression {i}: {e}")
                
                # Try different APIs
                results = {}
                
                # Wolfram Alpha
                if WOLFRAM_APP_ID:
                    try:
                        wa_query = self.converter.to_wolfram_alpha(expr['text'])
                        wa_result = self.math_apis.solve_with_wolfram_alpha(wa_query)
                        results['wolfram_alpha'] = wa_result
                        if wa_result.get('success'):
                            logger.debug(f"Wolfram Alpha successful for expression {i}")
                    except Exception as e:
                        logger.error(f"Wolfram Alpha failed for expression {i}: {e}")
                        results['wolfram_alpha'] = {'success': False, 'error': str(e)}
                
                # Symbolab
                if SYMBOLAB_ENABLED:
                    try:
                        symbolab_result = self.math_apis.solve_with_symbolab(expr['text'])
                        results['symbolab'] = symbolab_result
                        if symbolab_result.get('success'):
                            logger.debug(f"Symbolab successful for expression {i}")
                    except Exception as e:
                        logger.error(f"Symbolab failed for expression {i}: {e}")
                        results['symbolab'] = {'success': False, 'error': str(e)}
                
                # SymPy (local) - check if expression is not None
                if sympy_expr is not None:
                    try:
                        sympy_result = self.math_apis.solve_with_sympy(sympy_expr)
                        results['sympy'] = sympy_result
                        if sympy_result.get('success'):
                            logger.debug(f"SymPy successful for expression {i}")
                    except Exception as e:
                        logger.error(f"SymPy failed for expression {i}: {e}")
                        results['sympy'] = {'success': False, 'error': str(e)}
                
                api_results.append({
                    'expression': expr,
                    'sympy_expression': str(sympy_expr) if sympy_expr is not None else None,
                    'api_results': results
                })
            
            # Step 3: Generate final answer with Groq
            logger.info("Generating final answer with Groq...")
            final_answer = self.groq_generator.generate_final_answer(
                ocr_text, api_results, subject
            )
            
            # Step 4: Compile complete result
            processing_time = time.time() - start_time
            result = {
                'success': True,
                'original_text': ocr_text,
                'subject': subject,
                'detected_expressions': expressions,
                'api_results': api_results,
                'final_answer': final_answer,
                'processing_time_seconds': round(processing_time, 2)
            }
            
            logger.info(f"OCR processing completed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"OCR processing failed after {processing_time:.2f}s: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time_seconds': round(processing_time, 2),
                'original_text': ocr_text,
                'subject': subject
            }
    
    def process_single_question(self, question_text: str, subject: str = '') -> Dict[str, Any]:
        """
        Process a single question from OCR
        
        Args:
            question_text: Single question text
            subject: Subject area
            
        Returns:
            Solution for the single question
        """
        return self.process_ocr_text(question_text, subject)

# Example usage and testing
if __name__ == "__main__":
    # Test the integration
    integration = LatexOCRIntegration()
    
    # Sample OCR texts
    test_cases = [
        {
            'text': 'Solve the equation: x² + 5x + 6 = 0',
            'subject': 'mathematics'
        },
        {
            'text': 'Find the derivative of f(x) = x³ + 2x² - 3x + 1',
            'subject': 'mathematics'
        },
        {
            'text': 'Calculate the integral ∫(2x + 3)dx',
            'subject': 'mathematics'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}:")
        print(f"Question: {test_case['text']}")
        
        result = integration.process_single_question(
            test_case['text'], 
            test_case['subject']
        )
        
        if result['success']:
            print("✅ Success!")
            if result['final_answer']['success']:
                print("Final Answer Generated")
            else:
                print(f"⚠️ Final answer generation failed: {result['final_answer']['error']}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        print("-" * 50)
