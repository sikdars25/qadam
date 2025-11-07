import React from 'react';
import { InlineMath, BlockMath } from 'react-katex';

// Process text and render mathematical expressions with KaTeX
export const processMathInText = (text) => {
  if (!text) return text;
  
  // This function will be used to identify math expressions
  // The actual rendering will be done in the component
  return text;
};

// Render text with KaTeX math expressions
export const renderTextWithMath = (text) => {
  if (!text) return null;
  
  const parts = [];
  let lastIndex = 0;
  
  // Find all math expressions
  const displayMathRegex = /\$\$([^$]+)\$\$/g;
  const inlineMathRegex = /\$([^$]+)\$/g;
  
  let match;
  const mathExpressions = [];
  
  // Collect display math expressions
  while ((match = displayMathRegex.exec(text)) !== null) {
    mathExpressions.push({
      type: 'display',
      content: match[1],
      start: match.index,
      end: match.index + match[0].length
    });
  }
  
  // Reset regex for inline math
  displayMathRegex.lastIndex = 0;
  
  // Collect inline math expressions
  while ((match = inlineMathRegex.exec(text)) !== null) {
    mathExpressions.push({
      type: 'inline',
      content: match[1],
      start: match.index,
      end: match.index + match[0].length
    });
  }
  
  // Sort by start position
  mathExpressions.sort((a, b) => a.start - b.start);
  
  // Build parts array
  mathExpressions.forEach((expr, index) => {
    // Add text before math expression
    if (expr.start > lastIndex) {
      parts.push({
        type: 'text',
        content: text.slice(lastIndex, expr.start)
      });
    }
    
    // Add math expression
    parts.push({
      type: expr.type,
      content: expr.content
    });
    
    lastIndex = expr.end;
  });
  
  // Add remaining text
  if (lastIndex < text.length) {
    parts.push({
      type: 'text',
      content: text.slice(lastIndex)
    });
  }
  
  // Render parts
  return parts.map((part, index) => {
    if (part.type === 'text') {
      return <span key={index}>{part.content}</span>;
    } else if (part.type === 'display') {
      return <BlockMath key={index} math={part.content} errorColor="#cc0000" />;
    } else if (part.type === 'inline') {
      return <InlineMath key={index} math={part.content} errorColor="#cc0000" />;
    }
    return null;
  });
};

// Detect if text contains mathematical expressions
export const containsMathExpressions = (text) => {
  if (!text) return false;
  
  const mathIndicators = [
    /\$\$[^$]+\$\$/,         // Display math
    /\$[^$]+\$/,             // Inline math
    /\\[a-zA-Z]+\{[^}]*\}/,  // LaTeX commands with braces (e.g., \frac{a}{b})
    /\\[a-zA-Z]+(?!\w)/,     // LaTeX commands without braces (e.g., \alpha)
    /\\boxed\{[^}]+\}/,      // Boxed expressions
    /\\frac\{[^}]+\}\{[^}]+\}/, // Fractions
    /\\sqrt\{[^}]+\}/,       // Square roots
    /\\int_\{[^}]+\}\^\{[^}]+\}/, // Integrals with limits
    /\\sum_\{[^}]+\}\^\{[^}]+\}/, // Sums with limits
    /[α-ωΑ-Ω]/,              // Greek letters
    /[∫∑∏√∂∇∞±×÷≤≥≠≈≡]/,    // Math symbols
    /[₀-₉]/,                 // Subscripts
    /[⁰-⁹]/,                 // Superscripts
  ];

  return mathIndicators.some(pattern => pattern.test(text));
};

// Extract LaTeX expressions from text
export const extractLatexExpressions = (text) => {
  const expressions = [];
  
  // Display math $$...$$
  const displayMatches = text.match(/\$\$([^$]+)\$\$/g);
  if (displayMatches) {
    displayMatches.forEach(match => {
      expressions.push({
        type: 'display',
        expression: match.slice(2, -2),
        original: match
      });
    });
  }

  // Inline math $...$
  const inlineMatches = text.match(/\$([^$]+)\$/g);
  if (inlineMatches) {
    inlineMatches.forEach(match => {
      expressions.push({
        type: 'inline',
        expression: match.slice(1, -1),
        original: match
      });
    });
  }

  return expressions;
};

// Convert plain text math to LaTeX
export const plainTextToLatex = (text) => {
  let latex = text;
  
  // Convert common mathematical patterns
  const conversions = [
    { pattern: /sqrt\(([^)]+)\)/g, replacement: '\\sqrt{$1}' },
    { pattern: /\^([0-9]+)/g, replacement: '^{$1}' },
    { pattern: /_([0-9]+)/g, replacement: '_{$1}' },
    { pattern: /int from (\d+) to (\d+)/g, replacement: '\\int_{$1}^{$2}' },
    { pattern: /sum from (\d+) to (\d+)/g, replacement: '\\sum_{$1}^{$2}' },
    { pattern: /pi/g, replacement: '\\pi' },
    { pattern: /alpha/g, replacement: '\\alpha' },
    { pattern: /beta/g, replacement: '\\beta' },
    { pattern: /gamma/g, replacement: '\\gamma' },
    { pattern: /delta/g, replacement: '\\delta' },
    { pattern: /theta/g, replacement: '\\theta' },
    { pattern: /lambda/g, replacement: '\\lambda' },
    { pattern: /mu/g, replacement: '\\mu' },
    { pattern: /sigma/g, replacement: '\\sigma' },
    { pattern: /phi/g, replacement: '\\phi' },
    { pattern: /omega/g, replacement: '\\omega' },
  ];

  conversions.forEach(({ pattern, replacement }) => {
    latex = latex.replace(pattern, replacement);
  });

  return latex;
};

// Process solution text for mathematical content
export const processSolutionForMath = (solutionText) => {
  if (!solutionText) return solutionText;
  
  let processedText = solutionText;
  
  // First, handle existing LaTeX expressions from backend
  // Wrap standalone LaTeX commands in math delimiters
  const latexCommandPatterns = [
    // Handle \boxed{} expressions
    { pattern: /\\boxed\{([^}]+)\}/g, replacement: '$$\\boxed{$1}$$' },
    // Handle \frac{}{} expressions
    { pattern: /\\frac\{([^}]+)\}\{([^}]+)\}/g, replacement: '$\\frac{$1}{$2}$' },
    // Handle \sqrt{} expressions
    { pattern: /\\sqrt\{([^}]+)\}/g, replacement: '$\\sqrt{$1}$' },
    // Handle \sqrt[n]{} expressions
    { pattern: /\\sqrt\[(\d+)\]\{([^}]+)\}/g, replacement: '$\\sqrt[$1]{$2}$' },
    // Handle \int_{}^{} expressions
    { pattern: /\\int_\{([^}]+)\}\^\{([^}]+)\}/g, replacement: '$\\int_{$1}^{$2}$' },
    // Handle \sum_{}^{} expressions
    { pattern: /\\sum_\{([^}]+)\}\^\{([^}]+)\}/g, replacement: '$\\sum_{$1}^{$2}$' },
    // Handle \lim_{} expressions
    { pattern: /\\lim_\{([^}]+)\}/g, replacement: '$\\lim_{$1}$' },
    // Handle Greek letters
    { pattern: /\\(alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega)(?!\w)/g, replacement: '$\\$1$' },
    // Handle uppercase Greek letters
    { pattern: /\\(Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Phi|Psi|Omega)(?!\w)/g, replacement: '$\\$1$' },
    // Handle math operators
    { pattern: /\\(leq|geq|neq|approx|equiv|infty|pm|mp|times|div|cdot|partial|nabla|forall|exists|neg|land|lor|in|notin|subset|supset|cup|cap|emptyset)(?!\w)/g, replacement: '$\\$1$' },
    // Handle trigonometric functions
    { pattern: /\\(sin|cos|tan|cot|sec|csc|arcsin|arccos|arctan)(?!\w)/g, replacement: '$\\$1$' },
    // Handle logarithmic functions
    { pattern: /\\(log|ln|exp)(?!\w)/g, replacement: '$\\$1$' },
  ];

  // Apply LaTeX command patterns first
  latexCommandPatterns.forEach(({ pattern, replacement }) => {
    processedText = processedText.replace(pattern, replacement);
  });
  
  // Then, wrap common mathematical expressions in LaTeX delimiters
  const mathPatterns = [
    // Fractions (simpler pattern without negative lookbehind)
    { pattern: /(\d+)\/(\d+)/g, replacement: '$\\frac{$1}{$2}$' },
    // Powers (simpler pattern without negative lookbehind)
    { pattern: /([a-zA-Z])\^(\d+)/g, replacement: '$$1^{$2}$' },
    // Square roots (simpler pattern without negative lookbehind)
    { pattern: /sqrt\(([^)]+)\)/g, replacement: '$\\sqrt{$1}$' },
    // Mathematical operators
    { pattern: /≤/g, replacement: '$\\leq$' },
    { pattern: /≥/g, replacement: '$\\geq$' },
    { pattern: /≠/g, replacement: '$\\neq$' },
    { pattern: /≈/g, replacement: '$\\approx$' },
    { pattern: /∞/g, replacement: '$\\infty$' },
    { pattern: /±/g, replacement: '$\\pm$' },
    { pattern: /×/g, replacement: '$\\times$' },
    { pattern: /÷/g, replacement: '$\\div$' },
  ];

  mathPatterns.forEach(({ pattern, replacement }) => {
    processedText = processedText.replace(pattern, replacement);
  });
  
  return processedText;
};
