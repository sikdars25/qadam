"""
OCR Service - Flask Application using EasyOCR
Direct Flask app without Azure Functions wrapper
Last deployed: 2025-11-07 20:00:00
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
    Correct common OCR detection errors for mathematical symbols and expressions
    
    Issues addressed:
    1. τ (tau) detected as T
    2. Vector arrows (→) not detected above letters
    3. Single letter with prefix/suffix split incorrectly
    4. Power digits (exponential) not detected correctly
    5. Expressions in parentheses/brackets not detected correctly
    """
    if not text:
        return text
    
    corrected_text = text
    corrections_made = []
    
    # 1. Fix τ (tau) detection issues
    tau_corrections = [
        # Common contexts where τ is misdetected as T
        (r'\btorque\s+T\b', 'torque τ'),
        (r'\bshear\s+stress\s+T\b', 'shear stress τ'),
        (r'\btime\s+constant\s+T\b', 'time constant τ'),
        (r'\bangular\s+period\s+T\b', 'angular period τ'),
        (r'\bT\s+(constant|period|torque)\b', r'τ \1'),
        # Direct T to τ in math contexts
        (r'([=+\-*/(])T([a-zA-Z])', r'\1τ\2'),
        (r'([a-zA-Z])T([=+\-*/)])', r'\1τ\2'),
        # Handle T between variables
        (r'([=+\-*/(])T\s+([a-zA-Z])', r'\1τ\2'),
        (r'([a-zA-Z])\s+T([=+\-*/)])', r'\1τ\2'),
    ]
    
    for pattern, replacement in tau_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append(f"T → τ")
    
    # 2. Fix vector arrow detection
    vector_corrections = [
        # Common vector notations that get split - be more specific
        (r'\bvec\s+([a-zA-Z])\b', r'→\1'),  # vec a → →a
        (r'\b([a-zA-Z])\s+vec\b(?!\s+vec)', r'\1→'),  # a vec → a→ (not if followed by another vec)
        (r'\b([a-zA-Z])\s+vector\b', r'\1→'),  # a vector → a→
        (r'\bvector\s+([a-zA-Z])\b', r'→\1'),  # vector a → →a
        # Arrow combinations
        (r'->\s*([a-zA-Z])', r'→\1'),  # -> a → →a
        (r'([a-zA-Z])\s*->', r'\1→'),  # a -> → a→
    ]
    
    for pattern, replacement in vector_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("vector arrow fixed")
    
    # 3. Fix single letter with prefix/suffix splitting
    # Combine common math notation that gets incorrectly split
    combination_corrections = [
        # Greek letters with subscripts/superscripts - be more specific
        (r'λ\s+n\b', 'λn'),
        (r'λ\s+p\b', 'λp'),
        (r'α\s+n\b', 'αn'),
        (r'β\s+n\b', 'βn'),
        (r'θ\s+n\b', 'θn'),
        (r'μ\s+0\b', 'μ₀'),
        (r'σ\s+2\b', 'σ²'),
        # Variables with subscripts - be more specific to avoid power conflicts
        (r'([a-zA-Z])\s+(\d+)\b', r'\1\2'),  # a 1 → a1 (only at word boundary)
        (r'([a-zA-Z])\s+_(\d+)', r'\1_\2'),  # a _1 → a_1
        # Function notation
        (r'f\s*\(\s*x\s*\)', 'f(x)'),  # f ( x ) → f(x)
        (r'g\s*\(\s*x\s*\)', 'g(x)'),
        (r'sin\s*\(\s*x\s*\)', 'sin(x)'),
        (r'cos\s*\(\s*x\s*\)', 'cos(x)'),
        (r'tan\s*\(\s*x\s*\)', 'tan(x)'),
        (r'log\s*\(\s*x\s*\)', 'log(x)'),
        (r'ln\s*\(\s*x\s*\)', 'ln(x)'),
    ]
    
    for pattern, replacement in combination_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("combined split characters")
    
    # 4. Fix power digits and exponentials - fix negative exponent issue
    power_corrections = [
        # Superscript patterns - fix negative exponent issue
        (r'\^\s*-(\d+)', r'^-\1'),  # ^ -2 → ^-2
        (r'\^\s*(\d+)', r'^\1'),  # ^ 2 → ^2
        (r'([a-zA-Z])\s*\^\s*-(\d+)', r'\1^-\2'),  # x ^ -2 → x^-2
        (r'([a-zA-Z])\s*\^\s*(\d+)', r'\1^\2'),  # x ^ 2 → x^2
        # Only apply x2 → x^2 for common variables, not all letters
        (r'([xyze])\s*(\d+)\b', r'\1^\2'),  # x2 → x^2, y3 → y^3, etc.
        (r'e\s*\^\s*-(\d+)', r'e^-\1'),  # e ^ -2 → e^-2
        (r'e\s*\^\s*(\d+)', r'e^\1'),  # e ^ 2 → e^2
        (r'10\s*\^\s*-(\d+)', r'10^-\1'),  # 10 ^ -2 → 10^-2
        (r'10\s*\^\s*(\d+)', r'10^\1'),  # 10 ^ 2 → 10^2
    ]
    
    for pattern, replacement in power_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("power/exponential fixed")
    
    # 5. Scientific notation - apply after power corrections
    scientific_corrections = [
        # Scientific notation - be more specific, avoid conflicts with power corrections
        (r'(\d+\.\d+)\s+e\s+(\d+)(?!\s*\w)', r'\1e\2'),  # 1.2 e 3 → 1.2e3
        (r'(\d+\.\d+)\s+e\s+-(\d+)(?!\s*\w)', r'\1e-\2'),  # 1.2 e -3 → 1.2e-3
        (r'(\d+)\s+e\s+(\d+)(?!\s*\w)', r'\1e\2'),  # 1 e 3 → 1e3
        (r'(\d+)\s+e\s+-(\d+)(?!\s*\w)', r'\1e-\2'),  # 1 e -3 → 1e-3
    ]
    
    for pattern, replacement in scientific_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("scientific notation fixed")
    
    # 5. Fix parentheses and brackets expressions
    bracket_corrections = [
        # Fix spacing in mathematical expressions
        (r'\(\s*([^)]+?)\s*\)', r'(\1)'),  # ( x + y ) → (x+y)
        (r'\[\s*([^\]]+?)\s*\]', r'[\1]'),  # [ x + y ] → [x+y]
        (r'\{\s*([^}]+?)\s*\}', r'{\1}'),  # { x + y } → {x+y}
        # Remove extra spaces around operators in parentheses
        (r'\(\s*([^)]+?)\s*\+\s*([^)]+?)\s*\)', r'(\1+\2)'),  # ( a + b ) → (a+b)
        (r'\(\s*([^)]+?)\s*\-\s*([^)]+?)\s*\)', r'(\1-\2)'),  # ( a - b ) → (a-b)
        (r'\(\s*([^)]+?)\s*\*\s*([^)]+?)\s*\)', r'(\1*\2)'),  # ( a * b ) → (a*b)
        (r'\(\s*([^)]+?)\s*\/\s*([^)]+?)\s*\)', r'(\1/\2)'),  # ( a / b ) → (a/b)
        # Similar for brackets
        (r'\[\s*([^\]]+?)\s*\+\s*([^\]]+?)\s*\]', r'[\1+\2]'),  # [ a + b ] → [a+b]
        (r'\[\s*([^\]]+?)\s*\-\s*([^\]]+?)\s*\]', r'[\1-\2]'),  # [ a - b ] → [a-b]
        (r'\{\s*([^}]+?)\s*\+\s*([^}]+?)\s*\}', r'{\1+\2}'),  # { a + b } → {a+b}
        (r'\{\s*([^}]+?)\s*\-\s*([^}]+?)\s*\}', r'{\1-\2}'),  # { a - b } → {a-b}
    ]
    
    for pattern, replacement in bracket_corrections:
        if re.search(pattern, corrected_text):
            corrected_text = re.sub(pattern, replacement, corrected_text)
            corrections_made.append("parentheses/brackets fixed")
    
    # Log corrections for debugging
    if corrections_made:
        logging.info(f"🔧 Math symbol corrections applied: {', '.join(set(corrections_made))}")
    
    return corrected_text

def get_ocr_reader():
    """Get or initialize EasyOCR reader"""
    global ocr_reader
    if ocr_reader is None:
        try:
            logging.info("📄 Initializing EasyOCR with math support...")
            # Use both English and Latin for better math symbol recognition
            ocr_reader = easyocr.Reader(
                ['en', 'la'],  # English + Latin for math expressions
                gpu=False,
                recog_network='latin_g2'  # Latin character recognition network
            )
            logging.info("✅ EasyOCR initialized successfully with math support")
        except Exception as e:
            logging.error(f"❌ Failed to initialize EasyOCR: {e}")
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
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            logging.info(f"📐 Resized image to {new_size}")
        elif img.width < 800:
            # Upscale small images for better recognition
            ratio = 800 / img.width
            new_size = (800, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            logging.info(f"📐 Upscaled image to {new_size}")
        
        # Convert to numpy array
        img_np = np.array(img)
        
        return img_np
    except Exception as e:
        logging.error(f"Image preprocessing failed: {e}")
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
    Extract text from an image using EasyOCR
    
    Request:
        - file: Image file (multipart/form-data)
        OR
        - image_base64: Base64 encoded image (JSON)
    
    Response:
        {
            "success": true,
            "text": "extracted text",
            "confidence": 0.95
        }
    """
    try:
        # Get image from request
        if 'file' in request.files:
            file = request.files['file']
            image_data = file.read()
        elif request.is_json:
            data = request.get_json()
            image_base64 = data.get('image_base64', '')
            image_data = base64.b64decode(image_base64)
        else:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        # Preprocess image
        img_np = preprocess_image(image_data)
        if img_np is None:
            return jsonify({'success': False, 'error': 'Failed to process image'}), 500
        
        # Get OCR reader
        reader = get_ocr_reader()
        
        # Perform OCR with optimized parameters for math content
        logging.info("🔍 Performing OCR with math optimization...")
        results = reader.readtext(
            img_np,
            detail=1,
            paragraph=False,  # Detect individual text elements
            min_size=10,      # Detect smaller text (math symbols)
            text_threshold=0.6,  # Lower threshold for math symbols
            low_text=0.3      # Detect faint text
        )
        
        # Extract text from results
        # EasyOCR returns: [(bbox, text, confidence), ...]
        raw_text = ' '.join([text for (bbox, text, conf) in results])
        avg_confidence = sum([conf for (_, _, conf) in results]) / len(results) if results else 0
        
        # Apply mathematical symbol and expression corrections
        corrected_text = correct_math_symbols(raw_text)
        
        logging.info(f"✅ OCR completed: {len(corrected_text)} characters, confidence: {avg_confidence:.2f}")
        
        # Convert NumPy types to Python native types for JSON serialization
        details = [
            {
                'text': text,
                'confidence': float(conf),
                'bbox': convert_numpy_types(bbox)
            }
            for (bbox, text, conf) in results
        ]
        
        return jsonify({
            'success': True,
            'text': corrected_text,
            'raw_text': raw_text,  # Include original for debugging
            'confidence': float(avg_confidence),
            'corrections_applied': corrected_text != raw_text,
            'details': details
        })
        
    except Exception as e:
        logging.error(f"❌ OCR error: {e}")
        import traceback
        traceback.print_exc()
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
                    results = reader.readtext(img_np)
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

if __name__ == '__main__':
    # For development only
    app.run(host='0.0.0.0', port=8000, debug=False)
