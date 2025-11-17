"""
OCR Service - Flask Application using LaTeX-OCR (Primary) + EasyOCR (Fallback)
Direct Flask app without Azure Functions wrapper
Last deployed: 2025-11-08 11:00:00
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import base64
import io
import re
import unicodedata
from PIL import Image
import numpy as np
import easyocr

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# LaTeX-OCR integration (primary engine)
from latex_ocr_integration import get_latex_ocr_integration, extract_text_with_latex_priority

# LaTeX post-processing
from latex_postprocessor import post_process_latex_ocr_result

# Mathematical expression libraries
import math
import xml.etree.ElementTree as ET
from xml.dom import minidom
import hashlib
import json

# LaTeX to MathML support
try:
    import latex2mathml.converter
    LATEX2MATHML_AVAILABLE = True
except ImportError:
    LATEX2MATHML_AVAILABLE = False
    logging.warning("latex2mathml not available - LaTeX to MathML conversion disabled")

# OpenType MATH support (via font configuration and math rendering)
try:
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    from matplotlib import rcParams
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("Matplotlib not available - limited OpenType MATH support")

# LaTeX with AMS extensions support
try:
    from sympy import latex, preview
    from sympy.parsing.latex import parse_latex
    from sympy import symbols, integrate, diff, simplify, solve
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    logging.warning("SymPy not available - limited LaTeX processing")

# MathML processing utilities
class MathMLProcessor:
    """Process MathML expressions for mathematical content"""
    
    @staticmethod
    def mathml_to_text(mathml_content):
        """Convert MathML to readable text representation"""
        try:
            # Parse MathML and extract content
            root = ET.fromstring(mathml_content)
            
            # Handle different MathML elements
            if root.tag.endswith('math'):
                return MathMLProcessor._process_math_element(root)
            else:
                return MathMLProcessor._process_element(root)
        except Exception as e:
            logging.warning(f"MathML parsing error: {e}")
            return mathml_content
    
    @staticmethod
    def _process_math_element(element):
        """Process <math> element"""
        content = []
        for child in element:
            content.append(MathMLProcessor._process_element(child))
        return ''.join(content)
    
    @staticmethod
    def _process_element(element):
        """Process individual MathML elements"""
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        
        # Handle different MathML tags
        if tag == 'mi':  # Identifier
            return element.text or ''
        elif tag == 'mo':  # Operator
            return element.text or ''
        elif tag == 'mn':  # Number
            return element.text or ''
        elif tag == 'mfrac':  # Fraction
            numerator = denominator = ''
            if len(element) >= 2:
                numerator = MathMLProcessor._process_element(element[0])
                denominator = MathMLProcessor._process_element(element[1])
            return f"({numerator}/{denominator})"
        elif tag == 'msup':  # Superscript
            base = power = ''
            if len(element) >= 2:
                base = MathMLProcessor._process_element(element[0])
                power = MathMLProcessor._process_element(element[1])
            return f"{base}^{power}"
        elif tag == 'msub':  # Subscript
            base = subscript = ''
            if len(element) >= 2:
                base = MathMLProcessor._process_element(element[0])
                subscript = MathMLProcessor._process_element(element[1])
            return f"{base}_{subscript}"
        elif tag == 'mrow':  # Row
            content = []
            for child in element:
                content.append(MathMLProcessor._process_element(child))
            return ''.join(content)
        elif tag == 'msqrt':  # Square root
            if len(element) >= 1:
                content = MathMLProcessor._process_element(element[0])
                return f"√({content})"
            return '√()'
        elif tag == 'mroot':  # Nth root
            if len(element) >= 2:
                base = MathMLProcessor._process_element(element[0])
                root = MathMLProcessor._process_element(element[1])
                return f"√[{root}]({base})"
            return '√()'
        else:
            # Default: return text content
            return element.text or ''
    
    @staticmethod
    def validate_mathml(mathml_content):
        """Validate MathML content structure"""
        try:
            ET.fromstring(mathml_content)
            return True
        except ET.ParseError:
            return False

# LaTeX with AMS extensions processor
class LaTeXProcessor:
    """Process LaTeX expressions with AMS extensions"""
    
    @staticmethod
    def latex_to_text(latex_content):
        """Convert LaTeX to readable text"""
        try:
            if SYMPY_AVAILABLE:
                # Try to parse with SymPy for mathematical expressions
                try:
                    expr = parse_latex(latex_content)
                    return str(expr)
                except:
                    # Fallback to basic LaTeX parsing
                    return LaTeXProcessor._basic_latex_to_text(latex_content)
            else:
                return LaTeXProcessor._basic_latex_to_text(latex_content)
        except Exception as e:
            logging.warning(f"LaTeX parsing error: {e}")
            return latex_content
    
    @staticmethod
    def _basic_latex_to_text(latex_content):
        """Basic LaTeX to text conversion"""
        # Common LaTeX replacements
        replacements = {
            r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ',
            r'\epsilon': 'ε', r'\zeta': 'ζ', r'\eta': 'η', r'\theta': 'θ',
            r'\iota': 'ι', r'\kappa': 'κ', r'\lambda': 'λ', r'\mu': 'μ',
            r'\nu': 'ν', r'\xi': 'ξ', r'\pi': 'π', r'\rho': 'ρ',
            r'\sigma': 'σ', r'\tau': 'τ', r'\upsilon': 'υ', r'\phi': 'φ',
            r'\chi': 'χ', r'\psi': 'ψ', r'\omega': 'ω',
            r'\Gamma': 'Γ', r'\Delta': 'Δ', r'\Theta': 'Θ', r'\Lambda': 'Λ',
            r'\Xi': 'Ξ', r'\Pi': 'Π', r'\Sigma': 'Σ', r'\Upsilon': 'Υ',
            r'\Phi': 'Φ', r'\Psi': 'Ψ', r'\Omega': 'Ω',
            r'\sum': '∑', r'\prod': '∏', r'\int': '∫', r'\iint': '∬',
            r'\iiint': '∭', r'\oint': '∮', r'\sqrt': '√',
            r'\infty': '∞', r'\partial': '∂', r'\nabla': '∇',
            r'\pm': '±', r'\mp': '∓', r'\times': '×', r'\div': '÷',
            r'\leq': '≤', r'\geq': '≥', r'\neq': '≠', r'\approx': '≈',
            r'\equiv': '≡', r'\sim': '∼', r'\simeq': '≃', r'\cong': '≅',
            r'\propto': '∝', r'\parallel': '∥', r'\perp': '⊥',
            r'\rightarrow': '→', r'\leftarrow': '←', r'\leftrightarrow': '↔',
            r'\Rightarrow': '⇒', r'\Leftarrow': '⇐', r'\Leftrightarrow': '⇔',
            r'\subset': '⊂', r'\supset': '⊃', r'\subseteq': '⊆', r'\supseteq': '⊇',
            r'\in': '∈', r'\notin': '∉', r'\cup': '∪', r'\cap': '∩',
            r'\emptyset': '∅', r'\forall': '∀', r'\exists': '∃',
            r'\neg': '¬', r'\land': '∧', r'\lor': '∨', r'\oplus': '⊕',
            r'\otimes': '⊗', r'\odot': '⊙'
        }
        
        result = latex_content
        for latex_cmd, unicode_char in replacements.items():
            result = result.replace(latex_cmd, unicode_char)
        
        # Handle superscripts and subscripts
        import re
        result = re.sub(r'\^(\{[^}]+\}|\w)', lambda m: f'^{m.group(1).strip("{}")}', result)
        result = re.sub(r'_(\{[^}]+\}|\w)', lambda m: f'_{m.group(1).strip("{}")}', result)
        
        # Handle fractions
        result = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1/\2)', result)
        
        # Handle square roots
        result = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', result)
        result = re.sub(r'\\sqrt\[(\d+)\]\{([^}]+)\}', r'√[\1](\2)', result)
        
        return result
    
    @staticmethod
    def validate_latex(latex_content):
        """Basic LaTeX validation"""
        # Check for balanced braces
        brace_count = latex_content.count('{') - latex_content.count('}')
        if brace_count != 0:
            return False
        
        # Check for common LaTeX commands
        latex_patterns = [
            r'\\[a-zA-Z]+',  # LaTeX commands
            r'\^[^\\]',      # Superscripts
            r'_[^\\]',       # Subscripts
            r'\{[^}]*\}',    # Braced content
        ]
        
        for pattern in latex_patterns:
            if re.search(pattern, latex_content):
                return True
        
        return True

# Unicode data processor for mathematical symbols
class UnicodeMathProcessor:
    """Process Unicode mathematical characters and symbols"""
    
    @staticmethod
    def normalize_math_unicode(text):
        """Normalize Unicode mathematical characters"""
        if not text:
            return text
        
        # Normalize to NFC form for consistent representation
        normalized = unicodedata.normalize('NFC', text)
        
        # Convert superscripts and subscripts to regular characters
        superscripts = {
            '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
            '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
            '⁺': '+', '⁻': '-', '⁼': '=', '⁽': '(', '⁾': ')',
            'ⁱ': 'i', 'ʲ': 'j', 'ᵏ': 'k', 'ˡ': 'l', 'ᵐ': 'm',
            'ⁿ': 'n', 'ᵒ': 'o', 'ᵖ': 'p', 'ʳ': 'r', 'ˢ': 's',
            'ᵗ': 't', 'ᵘ': 'u', 'ᵛ': 'v', 'ʷ': 'w', 'ˣ': 'x',
            'ʸ': 'y', 'ᶻ': 'z'
        }
        
        subscripts = {
            '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
            '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
            '₊': '+', '₋': '-', '₌': '=', '₍': '(', '₎': ')',
            'ₐ': 'a', 'ₑ': 'e', 'ᵢ': 'i', 'ⱼ': 'j', 'ₖ': 'k',
            'ₗ': 'l', 'ₘ': 'm', 'ₙ': 'n', 'ₒ': 'o', 'ₚ': 'p',
            'ᵣ': 'r', 'ₛ': 's', 'ₜ': 't', 'ᵤ': 'u', 'ᵥ': 'v',
            'ₓ': 'x', 'ᵧ': 'y', '𝓏': 'z'
        }
        
        # Apply superscript/subscript conversion
        for sup_char, replacement in superscripts.items():
            normalized = normalized.replace(sup_char, replacement)
        
        for sub_char, replacement in subscripts.items():
            normalized = normalized.replace(sub_char, replacement)
        
        return normalized
    
    @staticmethod
    def get_math_symbol_info(char):
        """Get information about mathematical Unicode characters"""
        try:
            char_name = unicodedata.name(char)
            char_category = unicodedata.category(char)
            
            # Mathematical symbol categories
            math_categories = {
                'Sm': 'Math Symbol',
                'Sc': 'Currency Symbol',
                'Sk': 'Modifier Symbol',
                'So': 'Other Symbol'
            }
            
            return {
                'character': char,
                'name': char_name,
                'category': char_category,
                'math_category': math_categories.get(char_category, 'Unknown'),
                'unicode_point': f'U+{ord(char):04X}'
            }
        except ValueError:
            return None
    
    @staticmethod
    def extract_math_symbols(text):
        """Extract all mathematical Unicode symbols from text"""
        math_symbols = []
        for char in text:
            if char.startswith(('λ', 'μ', 'π', 'σ', 'τ', 'α', 'β', 'γ', 'δ', 'θ', 'ω')) or \
               unicodedata.category(char) in ['Sm', 'Sc', 'Sk', 'So']:
                info = UnicodeMathProcessor.get_math_symbol_info(char)
                if info:
                    math_symbols.append(info)
        return math_symbols

# OpenType MATH processor for advanced mathematical rendering
class OpenTypeMathProcessor:
    """Process OpenType MATH features for mathematical typography"""
    
    @staticmethod
    def setup_math_fonts():
        """Setup mathematical fonts for OpenType MATH support"""
        if not MATPLOTLIB_AVAILABLE:
            return False
        
        try:
            # Configure matplotlib for mathematical fonts
            rcParams['font.family'] = 'serif'
            rcParams['mathtext.fontset'] = 'stix'  # Stix fonts for math
            
            # Try to find and use mathematical fonts
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            math_fonts = ['STIX Two Math', 'Latin Modern Math', 'XITS Math', 'Asana Math']
            
            for font in math_fonts:
                if font in available_fonts:
                    rcParams['mathtext.fontset'] = 'stix'
                    logging.info(f"Using mathematical font: {font}")
                    return True
            
            logging.warning("No specialized math fonts found, using default")
            return True
        except Exception as e:
            logging.warning(f"Math font setup failed: {e}")
            return False
    
    @staticmethod
    def render_math_expression(expression, output_format='png'):
        """Render mathematical expression using OpenType MATH features"""
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        try:
            # Setup math fonts
            OpenTypeMathProcessor.setup_math_fonts()
            
            # Create figure for mathematical expression
            fig, ax = plt.subplots(figsize=(10, 2))
            ax.text(0.5, 0.5, f'${expression}$', fontsize=16, 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format=output_format, bbox_inches='tight', 
                       dpi=300, transparent=True)
            buffer.seek(0)
            plt.close()
            
            return buffer
        except Exception as e:
            logging.warning(f"Math rendering failed: {e}")
            return None
    
    @staticmethod
    def validate_math_expression(expression):
        """Validate mathematical expression for rendering"""
        try:
            # Basic validation - check for balanced braces and common math symbols
            brace_count = expression.count('{') - expression.count('}')
            if brace_count != 0:
                return False
            
            # Check for mathematical symbols
            math_symbols = ['^', '_', '\\', '∑', '∫', '∏', '√', '∞', '±', '∓', '×', '÷']
            return any(symbol in expression for symbol in math_symbols)
        except Exception:
            return False

# Initialize mathematical processors
mathml_processor = MathMLProcessor()
latex_processor = LaTeXProcessor()
unicode_processor = UnicodeMathProcessor()
opentype_processor = OpenTypeMathProcessor()

# Setup math fonts if available
if MATPLOTLIB_AVAILABLE:
    opentype_processor.setup_math_fonts()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
logging.basicConfig(level=logging.INFO)

# Initialize EasyOCR (lazy loading)
ocr_reader = None

def convert_numpy_types(obj):
    """Convert NumPy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    return obj

def correct_math_symbols(text):
    """
    Generic mathematical symbol detection and correction system
    
    This function uses intelligent symbol detection and context analysis
    to correct ANY mathematical expression, not just fixed patterns.
    
    Features:
    - Detects mathematical context automatically
    - Converts OCR misrecognitions to proper symbols
    - Handles vector notation, Greek letters, fractions, powers
    - Works for infinite combinations of expressions
    - Context-aware corrections based on surrounding text
    """
    if not text:
        return text
    
    corrected_text = text
    corrections_made = []
    
    # Step 1: Detect if this is mathematical/physics content
    math_indicators = [
        r'\b(equation|formula|expression|density|current|voltage|resistance)\b',
        r'\b(alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|tau|phi|omega)\b',
        r'\b(vector|vec|magnitude|direction|component)\b',
        r'[=+\-*/]',
        r'\^',
        r'\b(sin|cos|tan|log|ln|exp|sqrt|integral|derivative)\b',
        r'[α-ωΑ-Ω]',  # Greek letters
        r'[→←↑↓↔]',  # Arrows
    ]
    
    is_math_content = any(re.search(pattern, text, re.IGNORECASE) for pattern in math_indicators)
    
    if not is_math_content:
        return text  # Not mathematical content, return as-is
    
    # Step 2: Generic Greek letter corrections
    greek_mappings = {
        # Word-based Greek letters (OCR often recognizes these as words)
        'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ',
        'epsilon': 'ε', 'zeta': 'ζ', 'eta': 'η', 'theta': 'θ',
        'iota': 'ι', 'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ',
        'nu': 'ν', 'xi': 'ξ', 'omicron': 'ο', 'pi': 'π',
        'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ',
        'phi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω',
        
        # Common OCR misrecognitions for Greek letters
        'a': 'α', 'A': 'Α',  # a/alpha confusion
        'b': 'β', 'B': 'Β',  # b/beta confusion
        't': 'τ', 'T': 'Τ',  # t/tau confusion
        'Q': 'Θ', 'q': 'θ',  # Q/theta confusion
        'n': 'η', 'N': 'Ν',  # n/eta confusion
        'm': 'μ', 'M': 'Μ',  # m/mu confusion
    }
    
    # Apply Greek letter corrections with context awareness
    for wrong, correct in greek_mappings.items():
        # Only replace if it makes sense in mathematical context
        if wrong.lower() in ['a', 't', 'q', 'n', 'm']:
            # Be more careful with common letters
            pattern = rf'\b{wrong}\b(?=\s*[=+\-*/]|\s*\w*\s*[=+\-*/]|$)'
        else:
            pattern = rf'\b{wrong}\b'
        
        if re.search(pattern, corrected_text, re.IGNORECASE):
            corrected_text = re.sub(pattern, correct, corrected_text, flags=re.IGNORECASE)
            corrections_made.append(f"Greek letter: {wrong} → {correct}")
    
    # Step 3: Generic vector notation detection
    vector_patterns = [
        # Explicit vector words
        (r'\bvec\s+([a-zA-Z])\b', r'→\1'),
        (r'\bvector\s+([a-zA-Z])\b', r'→\1'),
        
        # Common physics variables that should be vectors
        (r'\b(j|E|B|F|v|a|p|r|u|w)\b(?=\s*[=+\-*/])', r'→\1'),
        
        # Variables in mathematical context that are likely vectors
        (r'\b([jJ])\b(?=\s*[=+\-*/])', r'→\1'),
        (r'\b([eE])\b(?=\s*[=+\-*/])', r'→\1'),
    ]
    
    for pattern, replacement in vector_patterns:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("Vector notation corrected")
    
    # Step 4: Generic mathematical notation corrections
    math_corrections = [
        # Power notation
        (r'([a-zA-Z])\s*\^\s*(\d+)', r'\1^\2'),
        (r'([a-zA-Z])\s*\^\s*-\s*(\d+)', r'\1^-\2'),
        (r'\^\s*2', '²'),
        (r'\^\s*3', '³'),
        (r'\^\s*4', '⁴'),
        
        # Fraction notation
        (r'\bfrac\s+([a-zA-Z0-9]+)\s+([a-zA-Z0-9]+)\b', r'(\1/\2)'),
        (r'([a-zA-Z0-9]+)\s*/\s*([a-zA-Z0-9]+)', r'(\1/\2)'),
        
        # Mathematical operators
        (r'\bsqrt\b', '√'),
        (r'\bint\b', '∫'),
        (r'\bsum\b', '∑'),
        (r'\bprod\b', '∏'),
        (r'\bapprox\b', '≈'),
        (r'\bneq\b', '≠'),
        (r'\bleq\b', '≤'),
        (r'\bgeq\b', '≥'),
        (r'\binfty\b', '∞'),
        
        # Parentheses and brackets cleanup
        (r'\bleft\s*\(', '('),
        (r'\bright\s*\)', ')'),
        (r'\bleft\s*\[', '['),
        (r'\bright\s*\]', ']'),
        (r'\bleft\s*\{', '{'),
        (r'\bright\s*\}', '}'),
    ]
    
    for pattern, replacement in math_corrections:
        if re.search(pattern, corrected_text, re.IGNORECASE):
            corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
            corrections_made.append("Mathematical notation corrected")
    
    # Step 5: Context-aware expression enhancement
    # Add brackets around mathematical expressions in physics context
    if re.search(r'\b(current|density|voltage|resistance|force|energy|power)\b', corrected_text, re.IGNORECASE):
        # Find mathematical expressions and add brackets
        math_expressions = re.finditer(r'([^=\s]+\s*=\s*[^,\n]+)', corrected_text)
        for match in math_expressions:
            expr = match.group(1)
            if not expr.startswith('[') and not expr.endswith(']'):
                if any(symbol in expr for symbol in ['→', 'α', 'β', 'γ', 'δ', '²', '³', '∫', '∑', '√']):
                    bracketed_expr = f'[{expr}]'
                    corrected_text = corrected_text.replace(expr, bracketed_expr, 1)
                    corrections_made.append("Added brackets to mathematical expression")
    
    # Step 6: Smart spacing and formatting
    formatting_corrections = [
        # Clean up spacing around operators
        (r'\s*([=+\-*/])\s*', r' \1 '),
        (r'\s+', ' '),  # Multiple spaces to single
        (r'\s*,\s*', ', '),  # Clean comma spacing
        (r'\s*\)\s*', ')'),  # Remove space before closing parenthesis
        (r'\s*\(\s*', '('),  # Remove space after opening parenthesis
    ]
    
    for pattern, replacement in formatting_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("Formatting cleaned up")
    
    # Step 7: Generic expression enhancement (no hard-coded patterns)
    # Add brackets around mathematical expressions in physics/math context
    if re.search(r'\b(current|density|voltage|resistance|force|energy|power|momentum|torque)\b', corrected_text, re.IGNORECASE):
        # Find mathematical expressions and add brackets
        math_expressions = re.finditer(r'([^=\s]+\s*=\s*[^,\n]+)', corrected_text)
        for match in math_expressions:
            expr = match.group(1)
            if not expr.startswith('[') and not expr.endswith(']'):
                if any(symbol in expr for symbol in ['→', 'α', 'β', 'γ', 'δ', '²', '³', '∫', '∑', '√']):
                    bracketed_expr = f'[{expr}]'
                    corrected_text = corrected_text.replace(expr, bracketed_expr, 1)
                    corrections_made.append("Added brackets to mathematical expression")
    
    # Log corrections for debugging
    if corrections_made:
        logging.info(f"🔧 Generic math corrections applied: {', '.join(set(corrections_made))}")
        logging.info(f"📝 Original: {text}")
        logging.info(f"✅ Corrected: {corrected_text}")
    
    return corrected_text

def get_ocr_reader():
    """Get or initialize EasyOCR reader with enhanced math symbol support"""
    global ocr_reader
    if ocr_reader is None:
        try:
            logging.info("📄 Initializing EasyOCR with enhanced math support...")
            # Use multiple languages for better math symbol recognition
            # English + Latin + Greek for comprehensive math symbol detection
            ocr_reader = easyocr.Reader(
                ['en', 'la', 'fr', 'de'],  # Multiple languages for better symbol recognition
                gpu=False,
                recog_network='latin_g2',  # Latin character recognition network
                download_enabled=True  # Ensure models are downloaded
            )
            logging.info("✅ EasyOCR initialized successfully with enhanced math support")
        except Exception as e:
            logging.error(f"❌ Failed to initialize EasyOCR: {e}")
            # Fallback to basic configuration
            try:
                logging.info("🔄 Trying fallback OCR configuration...")
                ocr_reader = easyocr.Reader(['en'], gpu=False)
                logging.info("✅ EasyOCR initialized with fallback configuration")
            except Exception as fallback_error:
                logging.error(f"❌ Failed to initialize EasyOCR even with fallback: {fallback_error}")
                raise
    return ocr_reader

def preprocess_image(image_data):
    """Optimize image for OCR - resize and enhance for math content"""
    try:
        # Load image
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large (max 2400px width for better math symbol recognition)
        max_width = 2400
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            # Use LANCZOS instead of ANTIALIAS for newer Pillow versions
            try:
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            except AttributeError:
                img = img.resize((max_width, new_height), Image.LANCZOS)
            logging.info(f"📏 Image resized from {img.width}x{img.height} to {max_width}x{new_height}")
        
        # Enhance contrast for better symbol detection
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)  # Increase contrast by 50%
        
        # Enhance sharpness for better symbol edges
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.3)  # Increase sharpness by 30%
        
        # Convert to numpy array for EasyOCR
        img_np = np.array(img)
        
        # Apply additional preprocessing for math symbols
        # Convert to grayscale for better text detection
        if len(img_np.shape) == 3:
            import cv2
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            # Apply adaptive threshold for better symbol detection
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            # Convert back to 3-channel for EasyOCR
            img_np = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
        
        logging.info(f"🖼️ Image preprocessed for math OCR: {img_np.shape}")
        return img_np
        
    except Exception as e:
        logging.error(f"❌ Failed to preprocess image: {e}")
        return None

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    logging.info('Health check requested')
    
    # Check if EasyOCR is installed
    easyocr_installed = False
    easyocr_version = None
    try:
        import easyocr
        easyocr_installed = True
        easyocr_version = easyocr.__version__ if hasattr(easyocr, '__version__') else 'unknown'
    except ImportError:
        pass

    return jsonify({
        'status': 'healthy',
        'service': 'OCR Service (Flask on VM)',
        'ocr_engine': 'EasyOCR',
        'easyocr_installed': easyocr_installed,
        'easyocr_version': easyocr_version if easyocr_installed else 'unknown',
        'python_version': os.sys.version,
        'features': [
            'greek_math_support',
            'utf8_encoding', 
            'symbol_recognition',
            'latin_language_support',
            'math_corrections',
            'tau_detection',
            'vector_arrows',
            'power_exponentials',
            'parentheses_brackets'
        ],
        'supported_corrections': [
            'τ (tau) detection',
            'Vector arrows (→)',
            'Combined characters (λn, λp)',
            'Power/exponential notation',
            'Parentheses/brackets cleanup'
        ]
    })

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """
    Extract text from an image using LaTeX-OCR (Primary) + EasyOCR (Fallback)
    
    Request:
        - file: Image file (multipart/form-data)
        OR
        - image_base64: Base64 encoded image (JSON)
    
    Response:
        {
            "success": true,
            "text": "extracted text",
            "engine": "latex-ocr" | "easyocr",
            "confidence": 0.95,
            "is_mathematical": true
        }
    """
    try:
        # Get image from request
        if 'file' in request.files:
            file = request.files['file']
            image_data = file.read()
            # Save temporary file for LaTeX-OCR
            temp_path = "/tmp/ocr_image.png"
            with open(temp_path, "wb") as f:
                f.write(image_data)
            image_path = temp_path
        elif request.is_json:
            data = request.get_json()
            image_base64 = data.get('image_base64', '')
            image_data = base64.b64decode(image_base64)
            # Save temporary file for LaTeX-OCR
            temp_path = "/tmp/ocr_image.png"
            with open(temp_path, "wb") as f:
                f.write(image_data)
            image_path = temp_path
        else:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        logging.info("🔍 Starting text extraction with LaTeX-OCR priority...")
        
        # Use LaTeX-OCR integration (primary engine)
        ocr_result = extract_text_with_latex_priority(image_path)
        
        if ocr_result['text'] and len(ocr_result['text'].strip()) > 0:
            # Apply LaTeX post-processing if LaTeX-OCR was used
            if ocr_result['engine'] == 'latex-ocr':
                logging.info("🔧 Applying LaTeX post-processing...")
                processed_result = post_process_latex_ocr_result(ocr_result['text'])
                processed_text = processed_result['corrected_text']
                logging.info(f"✅ LaTeX post-processing completed")
            else:
                processed_text = ocr_result['text']
            
            # Apply generic mathematical symbol corrections
            corrected_text = correct_math_symbols(processed_text)
            
            logging.info(f"✅ OCR completed with {ocr_result['engine']}: {len(corrected_text)} characters")
            logging.info(f"📊 Engine used: {ocr_result['engine']}")
            logging.info(f"🧮 Mathematical content: {ocr_result['is_mathematical']}")
            
            # Clean up temporary file
            if os.path.exists(image_path):
                os.remove(image_path)
            
            return jsonify({
                'success': True,
                'text': corrected_text,
                'raw_text': ocr_result['text'],  # Original OCR result
                'processed_text': processed_text if ocr_result['engine'] == 'latex-ocr' else None,
                'engine': ocr_result['engine'],
                'confidence': ocr_result['confidence'],
                'is_mathematical': ocr_result['is_mathematical'],
                'corrections_applied': corrected_text != ocr_result['text'],
                'latex_processed': ocr_result['engine'] == 'latex-ocr'
            })
        else:
            # Clean up temporary file
            if os.path.exists(image_path):
                os.remove(image_path)
            
            return jsonify({
                'success': False,
                'error': 'No text could be extracted from the image'
            }), 400
        
    except Exception as e:
        logging.error(f"❌ OCR error: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up temporary file on error
        try:
            if 'image_path' in locals() and os.path.exists(image_path):
                os.remove(image_path)
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ocr-engines-status', methods=['GET'])
def ocr_engines_status():
    """
    Get status of OCR engines (LaTeX-OCR and EasyOCR)
    
    Response:
        {
            "success": true,
            "engines": {
                "latex_ocr_available": true,
                "easyocr_available": true,
                "primary_engine": "latex-ocr",
                "fallback_engine": "easyocr"
            }
        }
    """
    try:
        integration = get_latex_ocr_integration()
        status = integration.get_engine_status()
        
        return jsonify({
            'success': True,
            'engines': status
        })
        
    except Exception as e:
        logging.error(f"❌ Error getting OCR engine status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/extract-from-pdf', methods=['POST'])
def extract_from_pdf():
    """
    Extract text from PDF using EasyOCR
    
    Request:
        - file: PDF file (multipart/form-data)
    
    Response:
        {
            "success": true,
            "text": "extracted text from all pages",
            "pages": 5
        }
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        try:
            import fitz  # PyMuPDF
            
            # Read PDF
            pdf_bytes = file.read()
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            all_text = []
            reader = get_ocr_reader()
            
            # Process each page
            for page_num in range(len(pdf_document)):
                logging.info(f"🔍 Processing page {page_num + 1}/{len(pdf_document)}")
                page = pdf_document[page_num]
                
                # Convert page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_data = pix.tobytes("png")
                
                # Preprocess and perform OCR
                img_np = preprocess_image(img_data)
                if img_np is not None:
                    results = reader.readtext(
                        img_np,
                        detail=1,
                        paragraph=False,
                        min_size=8,
                        text_threshold=0.5,
                        low_text=0.2,
                        contrast_ths=0.3,
                        adjust_contrast=0.7,
                        add_margin=0.1
                    )
                    page_text = ' '.join([text for (bbox, text, conf) in results])
                    all_text.append(page_text)
            
            pdf_document.close()
            
            combined_text = '\n\n'.join(all_text)
            
            logging.info(f"✅ PDF OCR completed: {len(combined_text)} characters from {len(all_text)} pages")
            
            return jsonify({
                'success': True,
                'text': combined_text,
                'pages': len(all_text)
            })
            
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'PyMuPDF not installed. Cannot process PDF files.'
            }), 500
            
    except Exception as e:
        logging.error(f"❌ PDF OCR error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages"""
    return jsonify({
        'languages': ['en', 'la'],
        'features': ['math_symbols', 'greek_letters', 'latin_characters'],
        'note': 'Optimized for mathematical expressions and educational content'
    })

# ============================================================================
# MATHEMATICAL EXPRESSION PROCESSING ENDPOINTS
# ============================================================================

@app.route('/api/math/unicode/normalize', methods=['POST'])
def normalize_math_unicode():
    """Normalize Unicode mathematical characters"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing text parameter'
            }), 400
        
        text = data['text']
        normalized_text = unicode_processor.normalize_math_unicode(text)
        math_symbols = unicode_processor.extract_math_symbols(text)
        
        return jsonify({
            'success': True,
            'original_text': text,
            'normalized_text': normalized_text,
            'math_symbols_found': len(math_symbols),
            'math_symbols': math_symbols,
            'unicode_form': 'NFC'
        })
        
    except Exception as e:
        logging.error(f"Unicode normalization error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/math/latex/convert', methods=['POST'])
def convert_latex_to_text():
    """Convert LaTeX expressions to readable text"""
    try:
        data = request.get_json()
        if not data or 'latex' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing latex parameter'
            }), 400
        
        latex_content = data['latex']
        is_valid = latex_processor.validate_latex(latex_content)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Invalid LaTeX syntax'
            }), 400
        
        converted_text = latex_processor.latex_to_text(latex_content)
        
        # Try to convert to MathML if requested
        mathml_output = None
        if data.get('include_mathml', False) and LATEX2MATHML_AVAILABLE:
            try:
                mathml_output = latex2mathml.converter.convert(latex_content)
            except Exception as e:
                logging.warning(f"LaTeX to MathML conversion failed: {e}")
        elif data.get('include_mathml', False) and not LATEX2MATHML_AVAILABLE:
            logging.warning("LaTeX to MathML conversion requested but latex2mathml not available")
        
        return jsonify({
            'success': True,
            'original_latex': latex_content,
            'converted_text': converted_text,
            'mathml': mathml_output,
            'sympy_available': SYMPY_AVAILABLE,
            'latex2mathml_available': LATEX2MATHML_AVAILABLE
        })
        
    except Exception as e:
        logging.error(f"LaTeX conversion error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/math/mathml/convert', methods=['POST'])
def convert_mathml_to_text():
    """Convert MathML expressions to readable text"""
    try:
        data = request.get_json()
        if not data or 'mathml' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing mathml parameter'
            }), 400
        
        mathml_content = data['mathml']
        is_valid = mathml_processor.validate_mathml(mathml_content)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Invalid MathML structure'
            }), 400
        
        converted_text = mathml_processor.mathml_to_text(mathml_content)
        
        return jsonify({
            'success': True,
            'original_mathml': mathml_content,
            'converted_text': converted_text
        })
        
    except Exception as e:
        logging.error(f"MathML conversion error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/math/render', methods=['POST'])
def render_math_expression():
    """Render mathematical expression using OpenType MATH features"""
    try:
        data = request.get_json()
        if not data or 'expression' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing expression parameter'
            }), 400
        
        expression = data['expression']
        output_format = data.get('format', 'png')
        
        is_valid = opentype_processor.validate_math_expression(expression)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Invalid mathematical expression'
            }), 400
        
        rendered_buffer = opentype_processor.render_math_expression(expression, output_format)
        
        if rendered_buffer is None:
            return jsonify({
                'success': False,
                'error': 'Math rendering failed - matplotlib not available or expression invalid'
            }), 500
        
        # Convert buffer to base64 for JSON response
        rendered_buffer.seek(0)
        rendered_data = base64.b64encode(rendered_buffer.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'original_expression': expression,
            'format': output_format,
            'rendered_image': f"data:image/{output_format};base64,{rendered_data}",
            'matplotlib_available': MATPLOTLIB_AVAILABLE
        })
        
    except Exception as e:
        logging.error(f"Math rendering error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/math/analyze', methods=['POST'])
def analyze_math_expression():
    """Comprehensive analysis of mathematical expression"""
    try:
        data = request.get_json()
        if not data or 'expression' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing expression parameter'
            }), 400
        
        expression = data['expression']
        
        # Unicode analysis
        normalized_expression = unicode_processor.normalize_math_unicode(expression)
        math_symbols = unicode_processor.extract_math_symbols(expression)
        
        # LaTeX analysis (if expression contains LaTeX commands)
        latex_analysis = None
        if '\\' in expression or '^' in expression or '_' in expression:
            latex_analysis = {
                'is_latex': latex_processor.validate_latex(expression),
                'converted_text': latex_processor.latex_to_text(expression)
            }
        
        # MathML analysis (if expression looks like MathML)
        mathml_analysis = None
        if '<math' in expression or '<m:' in expression:
            mathml_analysis = {
                'is_mathml': mathml_processor.validate_mathml(expression),
                'converted_text': mathml_processor.mathml_to_text(expression)
            }
        
        # OpenType MATH analysis
        render_analysis = {
            'can_render': opentype_processor.validate_math_expression(expression),
            'matplotlib_available': MATPLOTLIB_AVAILABLE
        }
        
        return jsonify({
            'success': True,
            'original_expression': expression,
            'normalized_expression': normalized_expression,
            'unicode_analysis': {
                'math_symbols_count': len(math_symbols),
                'math_symbols': math_symbols
            },
            'latex_analysis': latex_analysis,
            'mathml_analysis': mathml_analysis,
            'render_analysis': render_analysis,
            'libraries_available': {
                'unicodedata': True,
                'latex2mathml': LATEX2MATHML_AVAILABLE,
                'sympy': SYMPY_AVAILABLE,
                'matplotlib': MATPLOTLIB_AVAILABLE
            }
        })
        
    except Exception as e:
        logging.error(f"Math analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/math/libraries/status', methods=['GET'])
def get_math_libraries_status():
    """Get status of all mathematical expression libraries"""
    return jsonify({
        'success': True,
        'libraries': {
            'unicodedata': {
                'available': True,
                'version': 'built-in',
                'features': ['unicode_normalization', 'math_symbol_extraction', 'character_info']
            },
            'latex2mathml': {
                'available': LATEX2MATHML_AVAILABLE,
                'version': 'latex2mathml',
                'features': ['latex_to_mathml', 'latex_parsing'] if LATEX2MATHML_AVAILABLE else ['not_available'],
                'note': 'Install with: pip install latex2mathml' if not LATEX2MATHML_AVAILABLE else 'Fully functional'
            },
            'sympy': {
                'available': SYMPY_AVAILABLE,
                'features': ['latex_parsing', 'mathematical_computation', 'symbolic_math'] if SYMPY_AVAILABLE else ['not_available'],
                'note': 'Install with: pip install sympy' if not SYMPY_AVAILABLE else 'Fully functional'
            },
            'matplotlib': {
                'available': MATPLOTLIB_AVAILABLE,
                'features': ['math_rendering', 'opentype_math_fonts', 'expression_visualization'] if MATPLOTLIB_AVAILABLE else ['not_available'],
                'note': 'Install with: pip install matplotlib' if not MATPLOTLIB_AVAILABLE else 'Fully functional'
            },
            'mathml': {
                'available': True,
                'features': ['mathml_parsing', 'mathml_to_text', 'structure_validation']
            },
            'opentype_math': {
                'available': MATPLOTLIB_AVAILABLE,
                'features': ['math_font_support', 'advanced_typography', 'symbol_rendering'] if MATPLOTLIB_AVAILABLE else ['not_available'],
                'supported_fonts': ['STIX Two Math', 'Latin Modern Math', 'XITS Math', 'Asana Math'] if MATPLOTLIB_AVAILABLE else []
            }
        },
        'endpoints': {
            'unicode_normalize': '/api/math/unicode/normalize',
            'latex_convert': '/api/math/latex/convert',
            'mathml_convert': '/api/math/mathml/convert',
            'render_expression': '/api/math/render',
            'analyze_expression': '/api/math/analyze'
        }
    })

@app.route('/api/latex-ocr-solve', methods=['POST'])
def solve_latex_ocr_question():
    """
    Solve OCR text question using LaTeX OCR integration with NEW APPROACH:
    - Break into expressions, solve with Wolfram Alpha, format with Groq
    - Groq NO LONGER receives original OCR text
    """
    try:
        # Import the API integration (only available in backend-ocr branch)
        from latex_ocr_api_integration import LatexOCRIntegration
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        ocr_text = data.get('ocr_text', '').strip()
        subject = data.get('subject', '')
        
        if not ocr_text:
            return jsonify({'error': 'OCR text is required'}), 400
        
        # Validate input length
        if len(ocr_text) > 10000:
            return jsonify({'error': 'OCR text too long (max 10000 characters)'}), 400
        
        logger.info(f"🔍 Processing LaTeX OCR question with NEW approach")
        logger.info(f"📝 OCR text: {ocr_text[:100]}...")
        
        # Initialize the integration with NEW approach
        integration = LatexOCRIntegration()
        
        # Process the OCR text with timeout protection
        import signal
        from contextlib import contextmanager
        
        @contextmanager
        def time_limit(seconds):
            def signal_handler(signum, frame):
                raise TimeoutError("Processing timed out")
            signal.signal(signal.SIGALRM, signal_handler)
            signal.alarm(seconds)
            try:
                yield
            finally:
                signal.alarm(0)
        
        try:
            with time_limit(300):  # 5 minute timeout
                result = integration.process_single_question(ocr_text, subject)
        except TimeoutError:
            return jsonify({'error': 'Processing timed out - question may be too complex'}), 408
        
        if result['success']:
            # Prepare response with NEW approach structure
            response_data = {
                'success': True,
                'original_text': result['original_text'],
                'subject': result['subject'],
                'detected_expressions': result['detected_expressions'],
                'solved_expressions': result['solved_expressions'],  # NEW: Detailed solved results
                'final_answer': result['final_answer'],
                'processing_time_seconds': result.get('processing_time_seconds', 0),
                'approach': result.get('approach', 'wolfram_alpha_primary_grok_formatting')  # NEW: Approach indicator
            }
            
            return jsonify(response_data)
        else:
            return jsonify({
                'error': 'Failed to process OCR text', 
                'details': result.get('error', 'Unknown error'),
                'processing_time_seconds': result.get('processing_time_seconds', 0)
            }), 500
            
    except ImportError as e:
        return jsonify({'error': f'LaTeX OCR API integration not available: {e}'}), 503
    except Exception as e:
        import traceback
        logger.error(f"❌ LaTeX OCR processing error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Internal server error during OCR processing'}), 500

if __name__ == '__main__':
    # For development only
    app.run(host='0.0.0.0', port=8000, debug=False)
