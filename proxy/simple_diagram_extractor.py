#!/usr/bin/env python3
"""
Simple Diagram Extractor - Collects and appends all [DIAGRAM:...] texts
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def extract_diagram_texts(solution_text: str) -> List[str]:
    """
    Extract all [DIAGRAM:...] texts from solution steps
    """
    # Pattern to match [DIAGRAM: ...] markers
    pattern = r'\[DIAGRAM:\s*([^\]]+)\]'
    matches = re.findall(pattern, solution_text, re.IGNORECASE)
    
    diagram_texts = []
    for match in matches:
        diagram_texts.append(match.strip())
    
    logger.info(f"Extracted {len(diagram_texts)} diagram texts")
    for i, text in enumerate(diagram_texts):
        logger.info(f"  Diagram {i+1}: {text}")
    
    return diagram_texts

def create_combined_diagram(diagram_texts: List[str], question_text: str) -> Dict[str, Any]:
    """
    Create a combined diagram from all extracted diagram texts
    """
    if not diagram_texts:
        return {
            'type': 'empty',
            'content': 'No diagram markers found in solution',
            'elements_count': 0,
            'svg': '<svg width="400" height="200" viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="200" fill="#f8f9fa" stroke="#dee2e6" stroke-width="2" rx="10"/><text x="200" y="100" font-size="16" fill="#666" text-anchor="middle">No diagram elements detected</text></svg>',
            'diagrams': [],
            'text_content': ''
        }
    
    # Combine all diagram texts
    combined_text = '\n\n'.join([f"Diagram {i+1}: {text}" for i, text in enumerate(diagram_texts)])
    
    # Create a simple SVG that displays the text
    svg_content = create_text_svg(diagram_texts, question_text)
    
    # Create individual diagram objects for frontend compatibility
    diagrams = []
    for i, text in enumerate(diagram_texts):
        diagrams.append({
            'id': f'diagram_{i+1}',
            'title': f'Diagram {i+1}',
            'content': text,
            'svg': f'<svg width="400" height="100" viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="100" fill="#f8f9fa" stroke="#dee2e6" stroke-width="1" rx="5"/><text x="200" y="50" font-size="14" fill="#333" text-anchor="middle">{text}</text></svg>'
        })
    
    return {
        'type': 'combined_text',
        'content': combined_text,
        'elements_count': len(diagram_texts),
        'svg': svg_content,
        'raw_texts': diagram_texts,
        'diagrams': diagrams,
        'text_content': combined_text,  # Additional field for frontend
        'has_content': True,  # Additional field for frontend
        'display_content': combined_text  # Additional field for frontend
    }

def create_text_svg(diagram_texts: List[str], question_text: str) -> str:
    """
    Create an SVG that displays the diagram texts
    """
    width = 600
    height = 300 + (len(diagram_texts) * 60)  # Dynamic height based on content
    
    svg_lines = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        f'<rect width="{width}" height="{height}" fill="#f8f9fa" stroke="#dee2e6" stroke-width="2" rx="10"/>',
        f'<text x="{width//2}" y="30" font-size="18" font-weight="bold" fill="#333" text-anchor="middle">Construction Diagrams</text>',
        f'<text x="{width//2}" y="50" font-size="12" fill="#666" text-anchor="middle" font-style="italic">{question_text[:60]}...</text>',
    ]
    
    y_position = 80
    for i, text in enumerate(diagram_texts):
        # Add diagram number
        svg_lines.append(f'<text x="30" y="{y_position}" font-size="14" font-weight="bold" fill="#007bff">Diagram {i+1}:</text>')
        
        # Wrap text if too long
        if len(text) > 70:
            # Split long text into multiple lines
            words = text.split()
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= 70:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Add each line
            for j, line in enumerate(lines):
                svg_lines.append(f'<text x="120" y="{y_position + (j * 20)}" font-size="12" fill="#333">{line}</text>')
            
            y_position += len(lines) * 20 + 20
        else:
            svg_lines.append(f'<text x="120" y="{y_position}" font-size="12" fill="#333">{text}</text>')
            y_position += 40
    
    svg_lines.append('</svg>')
    return '\n'.join(svg_lines)

def analyze_and_generate_diagram(solution_text: str, question_text: str) -> Dict[str, Any]:
    """
    Main function to extract diagram texts and generate combined diagram
    """
    # Extract diagram texts
    diagram_texts = extract_diagram_texts(solution_text)
    
    # Create combined diagram
    combined_diagram = create_combined_diagram(diagram_texts, question_text)
    
    return combined_diagram

# Example usage
if __name__ == "__main__":
    sample_solution = """
    To construct the perpendicular bisector, follow these steps:
    
    Step 1: Draw a line segment AB.
    [DIAGRAM: Line segment AB with length 8 cm]
    
    Step 2: Find the midpoint of AB.
    [DIAGRAM: Midpoint M marked on line segment AB]
    
    Step 3: Draw perpendicular line at midpoint.
    [DIAGRAM: Perpendicular line at point M]
    
    The construction is complete.
    """
    
    result = analyze_and_generate_diagram(sample_solution, "Construct perpendicular bisector")
    print(f"Type: {result['type']}")
    print(f"Elements: {result['elements_count']}")
    print(f"Content: {result['content']}")
