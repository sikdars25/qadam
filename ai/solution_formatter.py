"""
Solution Formatter - Clean and format mathematical expressions in AI-generated solutions
"""

import re


def clean_math_expression(text):
    """
    Clean up garbled mathematical expressions in the solution text.
    
    Fixes common issues like:
    - π π 1 2 1 2 → πr²
    - 1 3 1 3 → r³
    - d C d r dr dC → dC/dr
    - \left( \right) → ( )
    - \frac{a}{b} → a/b
    - Duplicate symbols and spacing issues
    """
    if not text:
        return text
    
    # Store original text for comparison
    original = text
    
    # Remove LaTeX delimiters first
    text = re.sub(r'\\?\\\(', '', text)  # Remove \(
    text = re.sub(r'\\?\\\)', '', text)  # Remove \)
    text = re.sub(r'\\?\\\[', '', text)  # Remove \[
    text = re.sub(r'\\?\\\]', '', text)  # Remove \]
    
    # Remove \left and \right
    text = re.sub(r'\\left\s*', '', text)
    text = re.sub(r'\\right\s*', '', text)
    
    # Fix common LaTeX rendering issues
    
    # Fix pi r squared: π π 1 2 1 2 → πr²
    text = re.sub(r'π\s*π\s*1\s*2\s*1\s*2', 'πr²', text)
    text = re.sub(r'π\s*π\s*r\s*2', 'πr²', text)
    
    # Fix r cubed: 1 3 1 3 → r³
    text = re.sub(r'(?<!\d)1\s*3\s*1\s*3(?!\d)', 'r³', text)
    text = re.sub(r'r\s*3(?!\d)', 'r³', text)
    
    # Fix r squared: 1 2 1 2 → r²
    text = re.sub(r'(?<!\d)1\s*2\s*1\s*2(?!\d)', 'r²', text)
    text = re.sub(r'(?<![\d/])1\s*\^\s*\{?\s*2\s*\}?', 'r²', text)
    
    # Fix derivatives: d C d r dr dC → dC/dr
    text = re.sub(r'd\s+C\s+d\s+r\s+dr\s+dC\s*​?\s*', 'dC/dr', text)
    text = re.sub(r'dr\s+dC\s*​?\s*', 'dC/dr', text)
    
    # Fix fractions with weird spacing: 2000 r r 2000 → 2000/r
    text = re.sub(r'(\d+)\s+r\s+r\s+\1\s*​?\s*', r'\1/r', text)
    text = re.sub(r'(\d+)\s+1\s+1\s+\1\s*​?\s*', r'\1/r', text)
    
    # Fix cube root: \sqrt[3]{ → ∛ (handle nested braces)
    text = re.sub(r'\\sqrt\[3\]\{([^}]+)\}', r'∛(\1)', text)
    text = re.sub(r'∛\(\\frac\{([^}]+)\}\{([^}]+)\}\)', r'∛((\1)/(\2))', text)
    
    # Fix square root: \sqrt{ → √
    text = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', text)
    
    # Fix fractions: \frac{a}{b} → a/b (multiple passes for nested fractions)
    for _ in range(3):  # Handle up to 3 levels of nesting
        text = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'(\1)/(\2)', text)
    
    # Fix malformed fractions with missing braces
    text = re.sub(r'∛\(\\frac\{?(\d+)\}?\{?([^})\s]+)\}?\)', r'∛(\1/\2)', text)
    text = re.sub(r'∛\(\((\d+)\)\(([^)]+)\)\)', r'∛(\1/\2)', text)
    
    # Fix exponents in text: 1^{2} → r²
    text = re.sub(r'1\^\{2\}', 'r²', text)
    text = re.sub(r'1\^\{3\}', 'r³', text)
    
    # Fix pi symbol duplicates
    text = re.sub(r'π\s*π+', 'π', text)
    
    # Fix common volume formula: V = π π 1 2 1 2 h → V = πr²h
    text = re.sub(r'V\s*=\s*π\s*π\s*1\s*2\s*1\s*2\s*h', 'V = πr²h', text)
    
    # Fix surface area formula: A = 2 π π 1 2 1 2 + 2 π π rh → A = 2πr² + 2πrh
    text = re.sub(r'A\s*=\s*2\s*π\s*π\s*1\s*2\s*1\s*2\s*\+\s*2\s*π\s*π\s*rh', 'A = 2πr² + 2πrh', text)
    
    # Fix cost formula: C = 4 π π 1 2 1 2 + 2000 r r 2000 → C = 4πr² + 2000/r
    text = re.sub(r'C\s*=\s*4\s*π\s*π\s*1\s*2\s*1\s*2\s*\+\s*2000\s+r\s+r\s+2000', 'C = 4πr² + 2000/r', text)
    
    # Fix derivative: 8 π π r → 8πr
    text = re.sub(r'8\s*π\s*π\s*r', '8πr', text)
    
    # Fix fraction: \frac{2000}{1^{2}} → 2000/r²
    text = re.sub(r'\\frac\{2000\}\{1\^\{2\}\}', '2000/r²', text)
    text = re.sub(r'2000/1\^\{2\}', '2000/r²', text)
    
    # Fix exponent notation: 2 3 3 2 → 2/3
    text = re.sub(r'(?<!\d)2\s*3\s*3\s*2\s*​?\s*', '2/3', text)
    
    # Fix specific patterns from the example
    # ∛(\frac{250){ππ}} → ∛(250/π)
    text = re.sub(r'∛\(\\frac\{(\d+)\)\{?([^}]+)\}\}', r'∛(\1/\2)', text)
    text = re.sub(r'∛\(\((\d+)\)\{?([^}]+)\}\)', r'∛(\1/\2)', text)
    
    # Fix exponent fractions: ^{(2) / (3)} → ^(2/3)
    text = re.sub(r'\^\{?\((\d+)\)\s*/\s*\((\d+)\)\}?', r'^(\1/\2)', text)
    
    # Fix boxed answers: $\boxed{...}$ → [...]
    text = re.sub(r'\$\\boxed\{([^}]+)\}\$', r'[\1]', text)
    
    # Fix remaining LaTeX commands
    text = re.sub(r'\\times', '×', text)
    text = re.sub(r'\\cdot', '·', text)
    text = re.sub(r'\\pi', 'π', text)
    
    # Fix malformed cube roots with fractions
    # ∛(\frac{250){ππ}} or ∛((250)/(ππ))
    text = re.sub(r'∛\(\\frac\{?(\d+)\}?\)\{?ππ\}?\}', r'∛(\1/π)', text)
    text = re.sub(r'∛\(\((\d+)\)/\(ππ\)\)', r'∛(\1/π)', text)
    
    # Clean up extra spaces around mathematical operators
    text = re.sub(r'\s*([+\-*/=])\s*', r' \1 ', text)
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove zero-width spaces and other invisible characters
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    
    # Remove any remaining backslashes before common characters
    text = re.sub(r'\\([(){}])', r'\1', text)
    
    return text.strip()


def format_solution(solution_text):
    """
    Format the entire solution text by cleaning mathematical expressions.
    
    Args:
        solution_text (str): Raw solution text from AI
        
    Returns:
        str: Cleaned and formatted solution text
    """
    if not solution_text:
        return solution_text
    
    # First pass: Remove common LaTeX delimiters globally
    solution_text = re.sub(r'\\\(', '', solution_text)
    solution_text = re.sub(r'\\\)', '', solution_text)
    solution_text = re.sub(r'\\left', '', solution_text)
    solution_text = re.sub(r'\\right', '', solution_text)
    
    # Split into lines to preserve structure
    lines = solution_text.split('\n')
    
    # Clean each line
    cleaned_lines = [clean_math_expression(line) for line in lines]
    
    # Rejoin
    formatted_text = '\n'.join(cleaned_lines)
    
    # Final pass: Clean up any remaining LaTeX artifacts
    formatted_text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', formatted_text)
    formatted_text = re.sub(r'\\[a-zA-Z]+\{', '', formatted_text)  # Remove \command{
    formatted_text = re.sub(r'\}', '', formatted_text)  # Remove stray }
    formatted_text = re.sub(r'\\', '', formatted_text)  # Remove stray backslashes
    
    return formatted_text


def extract_and_format_expressions(solution_text):
    """
    Extract mathematical expressions and format them properly.
    
    Args:
        solution_text (str): Raw solution text
        
    Returns:
        dict: Dictionary with formatted expressions and cleaned text
    """
    # Common mathematical patterns to extract
    patterns = {
        'volume': r'V\s*=\s*[^.]+',
        'surface_area': r'A\s*=\s*[^.]+',
        'cost': r'C\s*=\s*[^.]+',
        'derivative': r'd[A-Z]/dr\s*=\s*[^.]+',
        'equation': r'[^=]+=\s*[^.]+',
    }
    
    expressions = {}
    for name, pattern in patterns.items():
        matches = re.findall(pattern, solution_text)
        if matches:
            expressions[name] = [clean_math_expression(m) for m in matches]
    
    return {
        'formatted_text': format_solution(solution_text),
        'extracted_expressions': expressions
    }


# Common mathematical symbol replacements for better readability
MATH_SYMBOLS = {
    'pi': 'π',
    'alpha': 'α',
    'beta': 'β',
    'gamma': 'γ',
    'delta': 'δ',
    'theta': 'θ',
    'lambda': 'λ',
    'mu': 'μ',
    'sigma': 'σ',
    'sqrt': '√',
    'integral': '∫',
    'sum': '∑',
    'product': '∏',
    'infinity': '∞',
    'approx': '≈',
    'leq': '≤',
    'geq': '≥',
    'neq': '≠',
    'times': '×',
    'divide': '÷',
    'plusminus': '±',
}


def replace_text_symbols(text):
    """
    Replace text representations of symbols with actual symbols.
    
    Args:
        text (str): Text with symbol names
        
    Returns:
        str: Text with actual symbols
    """
    for name, symbol in MATH_SYMBOLS.items():
        # Replace word boundaries to avoid partial matches
        text = re.sub(r'\b' + name + r'\b', symbol, text, flags=re.IGNORECASE)
    
    return text


if __name__ == '__main__':
    # Test with sample text
    sample = """
    The volume V of a cylinder is given by V = π π 1 2 1 2 h.
    The cost is C = 4 π π 1 2 1 2 + 2000 r r 2000.
    The derivative is d C d r dr dC = 8 π π r - 2000/1^{2}.
    The radius is r = \sqrt[3]{\frac{250}{\pi}}.
    """
    
    print("Original:")
    print(sample)
    print("\nCleaned:")
    print(format_solution(sample))
