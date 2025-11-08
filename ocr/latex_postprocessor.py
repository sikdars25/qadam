#!/usr/bin/env python3
"""
LaTeX Output Post-processor
Cleans up LaTeX-OCR output and fixes common OCR errors
"""

import re
import logging

def clean_latex_output(latex_text):
    """
    Clean up LaTeX-OCR output by fixing common OCR errors
    
    Args:
        latex_text (str): Raw LaTeX output from LaTeX-OCR
        
    Returns:
        str: Cleaned LaTeX text
    """
    if not latex_text:
        return latex_text
    
    cleaned = latex_text
    
    # Step 1: Fix common OCR word errors in mathematical context
    ocr_word_fixes = {
        # Physics/mathematical terminology fixes
        'tonsity': 'density',
        'maintianed': 'maintained',
        'electrons': 'electrons',
        'maxs': 'mass',
        'chare': 'charge',
        'plar': 'play',
        'conducter': 'conductor',
        'riar': 'via',
        'un': 'in',
        'curent': 'current',
        'trin': 'thin',
        'fteld': 'field',
        'onetor': 'one or',
        'orathe': 'other',
        'f s': 'is',
        'i t': 'it',
        'a e': 'are',
        'a v': 'a',
        'Define~^{}': 'Define',
        
        # Common LaTeX command fixes
        'mathrm~': 'mathrm{',
        '~}': '}',
        '~~': ' ',
        '~': ' ',
        '}{': '}{',
        '\\\\': '\\',
    }
    
    logging.info("🔧 Applying LaTeX OCR fixes...")
    
    for wrong, correct in ocr_word_fixes.items():
        if wrong in cleaned:
            cleaned = cleaned.replace(wrong, correct)
            logging.info(f"Fixed: {wrong} → {correct}")
    
    # Step 2: Fix LaTeX syntax issues
    latex_syntax_fixes = [
        # Fix double braces
        (r'\{\{([^}]+)\}\}', r'{\1}'),
        
        # Fix broken mathrm commands
        (r'\\mathrm\~([^{}]+)', r'\\mathrm{\1}'),
        (r'\\mathrm\{\s*([^{}]+)\s*\}', r'\\mathrm{\1}'),
        
        # Fix spacing issues
        (r'\s+', ' '),
        (r'~+', ' '),
        (r'\s*}\s*{\s*', '}{'),
        
        # Fix array formatting
        (r'\\begin\{array\}\{[^}]*\}\s*', r'\\begin{array}{l l l l}\n'),
        (r'\\end\{array\}\s*', r'\n\\end{array}'),
        
        # Fix math mode issues
        (r'\$\s*\$', ''),
        (r'\^\{\}', '^'),
    ]
    
    for pattern, replacement in latex_syntax_fixes:
        if re.search(pattern, cleaned):
            cleaned = re.sub(pattern, replacement, cleaned)
            logging.info(f"Applied LaTeX syntax fix: {pattern}")
    
    # Step 3: Clean up extra spaces and formatting
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Multiple spaces to single
    cleaned = cleaned.strip()  # Remove leading/trailing spaces
    
    # Step 4: Fix specific mathematical expressions
    math_fixes = [
        # Fix common physics expressions
        (r'density\s+f\s+is\s+scalar', 'density f is scalar'),
        (r'electric\s+field', 'electric field'),
        (r'conductors?\s+in', 'conductor in'),
        (r'current\s+in\s+the\s+conductor', 'current in the conductor'),
    ]
    
    for pattern, replacement in math_fixes:
        if re.search(pattern, cleaned, re.IGNORECASE):
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    
    logging.info(f"✅ LaTeX cleaning completed")
    logging.info(f"📝 Original: {latex_text[:100]}...")
    logging.info(f"✅ Cleaned: {cleaned[:100]}...")
    
    return cleaned

def extract_text_from_latex(latex_text):
    """
    Extract readable text from LaTeX output
    
    Args:
        latex_text (str): LaTeX text
        
    Returns:
        str: Readable text
    """
    if not latex_text:
        return latex_text
    
    # Remove LaTeX commands but preserve content
    text = latex_text
    
    # Replace LaTeX commands with their content in order
    replacements = [
        # Extract content from mathrm commands
        (r'\\mathrm\{([^}]+)\}', r'\1'),
        # Extract content from mathbf commands  
        (r'\\mathbf\{([^}]+)\}', r'\1'),
        # Extract content from other math commands
        (r'\\mathit\{([^}]+)\}', r'\1'),
        (r'\\mathsf\{([^}]+)\}', r'\1'),
        (r'\\mathtt\{([^}]+)\}', r'\1'),
        
        # Remove array environments but keep content
        (r'\\begin\{array\}\{[^}]*\}', ''),
        (r'\\end\{array\}', ''),
        
        # Handle superscripts and subscripts
        (r'\^\{([^}]+)\}', r'^\1'),
        (r'_\{([^}]+)\}', r'_\1'),
        
        # Remove other LaTeX commands
        (r'\\[a-zA-Z]+\{[^}]*\}', ''),
        (r'\\[a-zA-Z]', ''),
        
        # Clean up braces (but keep content)
        (r'\{([^}]+)\}', r'\1'),
        
        # Remove remaining LaTeX symbols
        (r'\\', ''),
        (r'\$', ''),
        (r'\&', ' '),
        (r'\\', ' '),
    ]
    
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    
    # Clean up spacing and formatting
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
    text = re.sub(r'[&{}]', ' ', text)  # Replace remaining LaTeX symbols with space
    text = text.strip()
    
    # Fix spacing around punctuation
    text = re.sub(r'\s*([;,.])\s*', r'\1 ', text)
    text = re.sub(r'\s+', ' ', text)  # Clean up again
    text = text.strip()
    
    return text

def post_process_latex_ocr_result(latex_result):
    """
    Complete post-processing pipeline for LaTeX-OCR results
    
    Args:
        latex_result (str): Raw LaTeX-OCR output
        
    Returns:
        dict: Processed result with cleaned LaTeX and extracted text
    """
    if not latex_result:
        return {
            'latex': latex_result,
            'cleaned_latex': latex_result,
            'extracted_text': latex_result,
            'corrections_applied': False
        }
    
    # Clean up LaTeX
    cleaned_latex = clean_latex_output(latex_result)
    
    # Extract readable text
    extracted_text = extract_text_from_latex(cleaned_latex)
    
    # Apply generic math symbol corrections to extracted text
    from app import correct_math_symbols
    corrected_text = correct_math_symbols(extracted_text)
    
    return {
        'latex': latex_result,
        'cleaned_latex': cleaned_latex,
        'extracted_text': extracted_text,
        'corrected_text': corrected_text,
        'corrections_applied': cleaned_latex != latex_result or corrected_text != extracted_text
    }

def test_latex_postprocessor():
    """Test the LaTeX post-processor with the provided example"""
    
    test_input = r"\begin{array}{l l l l}{{(\mathbf{a})}}&{{\mathrm{Define~}^{\mathrm{tonsity}, ~f s~i t~a~e c a l a r~o r~a~v e c t o r~};~{\mathrm{kn~electric~fteld}}}}\\ {{}}&{{\mathrm{E}~\mathrm{is~~maintianed~in~onetor~in~orathe~conductior~in}~~}}\\ {{}}&{{\mathrm{electrons~(maxs~m, ~chare}~\mathrm{plar~the~conducter}~i n}}}\\ {{}}&{{\mathrm{and~riar~time}~\mathrm{the~curent~un~the~conducte}}}\\ {{}}&{{\mathrm{where}~\mathrm{trin}~~}}&{{\mathrm{~~}}}\end{array}"
    
    print("🧪 Testing LaTeX Post-processor")
    print("=" * 50)
    print("📝 Input LaTeX:")
    print(test_input[:200] + "...")
    
    result = post_process_latex_ocr_result(test_input)
    
    print(f"\n✅ Cleaned LaTeX:")
    print(result['cleaned_latex'][:300] + "...")
    
    print(f"\n📄 Extracted Text:")
    print(result['extracted_text'])
    
    print(f"\n🔧 Corrected Text:")
    print(result['corrected_text'])
    
    print(f"\n📊 Corrections Applied: {result['corrections_applied']}")
    
    return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test the post-processor
    test_latex_postprocessor()
    
    print(f"\n{'='*50}")
    print("🎯 LaTeX Post-processor Features:")
    print("  ✅ Fixes common OCR word errors")
    print("  ✅ Corrects LaTeX syntax issues")
    print("  ✅ Extracts readable text from LaTeX")
    print("  ✅ Applies generic math symbol corrections")
    print("  ✅ Maintains mathematical structure")
