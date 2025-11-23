#!/usr/bin/env python3
"""
Comprehensive Diagram Generator
Analyzes all diagram texts from AI solution and creates a single unified diagram
Enhanced with fallback extraction for triangle constructions
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DiagramElement:
    """Represents a single diagram element extracted from solution text"""
    text: str
    element_type: str
    points: List[str]
    measurements: Dict[str, str]
    description: str

class ComprehensiveDiagramAnalyzer:
    """Analyzes diagram texts and creates unified construction diagrams"""
    
    def __init__(self):
        self.diagram_patterns = {
            'line_segment': r'\[DIAGRAM:\s*(?:A )?simple line segment\s*([A-Z]+)(?:\s*with\s*(.+?))?\]',
            'line_with_length': r'\[DIAGRAM:\s*Line segment\s*([A-Z]+)\s*with a length of\s*(\d+(?:\.\d+)?)\s*cm\s*(.+?)?\]',
            'triangle': r'\[DIAGRAM:\s*(?:A )?triangle\s*([A-Z]+)(?:\s*(.+?))?\]',
            'perpendicular': r'\[DIAGRAM:\s*(?:A )?perpendicular\s+(?:bisector|line)\s*(?:of\s*)?(?:line segment\s*)?([A-Z]+)(?:\s*(.+?))?\]',
            'construction': r'\[DIAGRAM:\s*(?:construction|construct|draw|step)\s*(.+?)\]',
            'angle': r'\[DIAGRAM:\s*(?:angle|∠)\s*([A-Z]+)(?:\s*=\s*(\d+(?:\.\d+)?)\s*(?:degrees|°))?(?:\s*(.+?))?\]',
            'base': r'\[DIAGRAM:\s*(?:base|draw)\s*(?:segment|line)\s*([A-Z]+)(?:\s*(.+?))?\]',
            'general': r'\[DIAGRAM:\s*(.+?)\]'
        }
    
    def extract_diagram_elements(self, solution_text: str) -> List[DiagramElement]:
        """Extract all diagram elements from solution text"""
        elements = []
        
        # First try to extract explicit [DIAGRAM: ...] markers
        for pattern_name, pattern in self.diagram_patterns.items():
            matches = re.finditer(pattern, solution_text, re.IGNORECASE)
            
            for match in matches:
                if pattern_name == 'general' and any(other_match in elements for other_match in elements):
                    continue
                
                element = self._parse_diagram_match(match, pattern_name)
                if element:
                    elements.append(element)
        
        # If no explicit markers found, try to infer from construction language
        if not elements:
            elements = self._extract_construction_from_text(solution_text)
        
        return elements
    
    def _extract_construction_from_text(self, solution_text: str) -> List[DiagramElement]:
        """Extract construction elements from plain text when no markers are present"""
        elements = []
        
        # Look for triangle construction keywords
        if re.search(r'construct\s+triangle|triangle\s+ABC|triangle.*construction', solution_text, re.IGNORECASE):
            elements.append(DiagramElement(
                text="[INFERRED: Triangle construction]",
                element_type='triangle',
                points=['ABC'],
                measurements={},
                description='Triangle ABC construction'
            ))
        
        # Look for base/segment construction (more flexible pattern)
        base_match = re.search(r'(?:base|segment|line)\s+([A-Z]{1,2})\s*(?:=)?\s*(\d+(?:\.\d+)?)\s*cm|([A-Z]{1,2})\s*(?:=)?\s*(\d+(?:\.\d+)?)\s*cm', solution_text, re.IGNORECASE)
        if base_match:
            if base_match.group(1) and base_match.group(2):
                points = [base_match.group(1)]
                length = base_match.group(2)
            else:
                points = [base_match.group(3)]
                length = base_match.group(4)
            elements.append(DiagramElement(
                text=f"[INFERRED: Base {points[0]} = {length}cm]",
                element_type='line_with_length',
                points=points,
                measurements={'length': f"{length}cm"},
                description=f"Base segment {points[0]} with length {length}cm"
            ))
        
        # Look for angle constructions
        angle_matches = re.findall(r'angle\s+([A-Z])\s*(?:=)?\s*(\d+(?:\.\d+)?)\s*(?:degrees|°)', solution_text, re.IGNORECASE)
        for point, angle in angle_matches:
            elements.append(DiagramElement(
                text=f"[INFERRED: Angle {point} = {angle}°]",
                element_type='angle',
                points=[point],
                measurements={'angle': angle},
                description=f"Angle {point} = {angle}°"
            ))
        
        # Look for general construction steps
        step_matches = re.findall(r'(?:step\s+\d+:|draw|construct|mark|measure)\s+([^.\n]+)', solution_text, re.IGNORECASE)
        for step_desc in step_matches[:3]:  # Limit to first 3 steps
            elements.append(DiagramElement(
                text=f"[INFERRED: {step_desc.strip()}]",
                element_type='construction',
                points=[],
                measurements={},
                description=f"Construction step: {step_desc.strip()}"
            ))
        
        return elements
    
    def _parse_diagram_match(self, match, pattern_name: str) -> Optional[DiagramElement]:
        """Parse a regex match into a DiagramElement"""
        try:
            text = match.group(0)
            
            if pattern_name == 'line_segment':
                points = [match.group(1)]
                return DiagramElement(
                    text=text,
                    element_type='line_segment',
                    points=points,
                    measurements={},
                    description=f"Line segment {points[0]}"
                )
            elif pattern_name == 'line_with_length':
                points = [match.group(1)]
                length = match.group(2)
                return DiagramElement(
                    text=text,
                    element_type='line_with_length',
                    points=points,
                    measurements={'length': f"{length}cm"},
                    description=f"Line segment {points[0]} with length {length}cm"
                )
            elif pattern_name == 'triangle':
                points = [match.group(1)]
                return DiagramElement(
                    text=text,
                    element_type='triangle',
                    points=points,
                    measurements={},
                    description=f"Triangle {points[0]}"
                )
            elif pattern_name == 'perpendicular':
                points = [match.group(1)]
                return DiagramElement(
                    text=text,
                    element_type='perpendicular',
                    points=points,
                    measurements={},
                    description=f"Perpendicular bisector of {points[0]}"
                )
            elif pattern_name == 'construction':
                description = match.group(1)
                return DiagramElement(
                    text=text,
                    element_type='construction',
                    points=[],
                    measurements={},
                    description=f"Construction step: {description}"
                )
            elif pattern_name == 'angle':
                points = [match.group(1)]
                angle_value = match.group(2) if len(match.groups()) > 1 else None
                description = f"Angle {points[0]}"
                if angle_value:
                    description += f" = {angle_value}°"
                return DiagramElement(
                    text=text,
                    element_type='angle',
                    points=points,
                    measurements={'angle': angle_value} if angle_value else {},
                    description=description
                )
            elif pattern_name == 'base':
                points = [match.group(1)]
                return DiagramElement(
                    text=text,
                    element_type='base',
                    points=points,
                    measurements={},
                    description=f"Base segment {points[0]}"
                )
            elif pattern_name == 'general':
                description = match.group(1)
                return DiagramElement(
                    text=text,
                    element_type='general',
                    points=[],
                    measurements={},
                    description=description
                )
                
        except Exception as e:
            logger.error(f"Error parsing diagram match: {e}")
            return None
    
    def generate_unified_diagram(self, elements: List[DiagramElement], question_text: str) -> Dict[str, Any]:
        """Generate a single unified diagram from all elements"""
        if not elements:
            return self._generate_empty_diagram()
        
        return self._generate_construction_sequence(elements, question_text)
    
    def _generate_construction_sequence(self, elements: List[DiagramElement], question_text: str) -> Dict[str, Any]:
        """Generate a construction sequence diagram"""
        svg_content = self._create_construction_svg(elements, question_text)
        
        return {
            'type': 'construction_sequence',
            'svg': svg_content,
            'description': f"Construction sequence for: {question_text[:50]}...",
            'elements_count': len(elements),
            'steps': [elem.description for elem in elements]
        }
    
    def _generate_empty_diagram(self) -> Dict[str, Any]:
        """Generate an empty/placeholder diagram"""
        svg_content = '''
        <svg width="400" height="200" viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="200" fill="#f8f9fa" stroke="#dee2e6" stroke-width="2" rx="10"/>
            <text x="200" y="100" font-size="16" fill="#666" text-anchor="middle">No diagram elements detected</text>
        </svg>
        '''
        
        return {
            'type': 'empty',
            'svg': svg_content,
            'description': 'No diagram elements found in solution',
            'elements_count': 0
        }
    
    def _create_construction_svg(self, elements: List[DiagramElement], question_text: str) -> str:
        """Create SVG for construction sequence"""
        width = 600
        height = 300
        step_spacing = 150
        start_x = 50
        start_y = 150
        
        svg_lines = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
            f'<text x="{width//2}" y="30" font-size="18" font-weight="bold" fill="#333" text-anchor="middle">Construction Sequence</text>',
            f'<text x="{width//2}" y="50" font-size="12" fill="#666" text-anchor="middle" font-style="italic">{question_text[:60]}...</text>'
        ]
        
        for i, element in enumerate(elements):
            x = start_x + (i * step_spacing)
            
            # Add connection line
            if i > 0:
                prev_x = start_x + ((i-1) * step_spacing)
                svg_lines.append(f'<line x1="{prev_x + 60}" y1="{start_y}" x2="{x - 20}" y2="{start_y}" stroke="#007bff" stroke-width="2" stroke-dasharray="5,5"/>')
                svg_lines.append(f'<text x="{prev_x + step_spacing//2}" y="{start_y - 10}" font-size="10" fill="#007bff" text-anchor="middle">Step {i}</text>')
            
            # Draw specific construction based on element type
            if element.element_type == 'line_with_length':
                length = element.measurements.get('length', '6')
                svg_lines.extend(self._create_line_segment(x, start_y, element.points[0], length))
            elif element.element_type == 'triangle':
                svg_lines.extend(self._create_triangle(x, start_y, element.points[0]))
            elif element.element_type == 'angle':
                svg_lines.extend(self._create_angle(x, start_y, element.points[0], element.measurements.get('angle', '')))
            elif element.element_type == 'base':
                svg_lines.extend(self._create_line_segment(x, start_y, element.points[0], ''))
            elif element.element_type == 'construction':
                svg_lines.extend(self._create_construction_step(x, start_y, element.description))
            else:
                svg_lines.extend(self._create_default_element(x, start_y, element.description))
            
            # Add step number
            svg_lines.append(f'<text x="{x}" y="{start_y + 80}" font-size="12" fill="#666" text-anchor="middle">Step {i+1}</text>')
        
        # Add flow arrow
        if len(elements) > 1:
            last_x = start_x + ((len(elements) - 1) * step_spacing)
            svg_lines.append(f'<path d="M {last_x + 60} {start_y} L {last_x + 100} {start_y}" stroke="#28a745" stroke-width="2" marker-end="url(#arrowhead)"/>')
            svg_lines.append('<defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#28a745"/></marker></defs>')
        
        svg_lines.append('</svg>')
        return '\n'.join(svg_lines)
    
    def _create_line_segment(self, x: int, y: int, point_name: str, length: str) -> List[str]:
        """Create a line segment with length measurement"""
        result = [
            f'<g transform="translate({x - 30}, {y - 30})">',
            '<line x1="0" y1="30" x2="60" y2="30" stroke="#333" stroke-width="2"/>',
            '<circle cx="0" cy="30" r="3" fill="#dc3545"/>',
            '<circle cx="60" cy="30" r="3" fill="#dc3545"/>',
            f'<text x="-5" y="25" font-size="10" font-weight="bold" fill="#333">{point_name[0] if len(point_name) > 0 else "B"}</text>',
            f'<text x="65" y="25" font-size="10" font-weight="bold" fill="#333">{point_name[1] if len(point_name) > 1 else "C"}</text>',
        ]
        if length:
            result.append(f'<text x="25" y="20" font-size="8" fill="#007bff" text-anchor="middle">{length}</text>')
        result.append('</g>')
        return result
    
    def _create_triangle(self, x: int, y: int, point_name: str) -> List[str]:
        """Create a triangle"""
        return [
            f'<g transform="translate({x - 30}, {y - 50})">',
            '<polygon points="30,10 10,60 50,60" fill="none" stroke="#333" stroke-width="2"/>',
            '<circle cx="30" cy="10" r="3" fill="#dc3545"/>',
            '<circle cx="10" cy="60" r="3" fill="#dc3545"/>',
            '<circle cx="50" cy="60" r="3" fill="#dc3545"/>',
            f'<text x="28" y="8" font-size="10" font-weight="bold" fill="#333">A</text>',
            f'<text x="5" y="70" font-size="10" font-weight="bold" fill="#333">B</text>',
            f'<text x="52" y="70" font-size="10" font-weight="bold" fill="#333">C</text>',
            '</g>'
        ]
    
    def _create_angle(self, x: int, y: int, point_name: str, angle_value: str) -> List[str]:
        """Create an angle representation"""
        result = [
            f'<g transform="translate({x - 30}, {y - 30})">',
            '<line x1="0" y1="30" x2="30" y2="30" stroke="#333" stroke-width="2"/>',
            '<line x1="30" y1="30" x2="45" y2="15" stroke="#333" stroke-width="2"/>',
            '<path d="M 10 30 A 10 10 0 0 1 20 22" fill="none" stroke="#007bff" stroke-width="1"/>',
            f'<text x="-5" y="25" font-size="10" font-weight="bold" fill="#333">{point_name}</text>',
        ]
        if angle_value:
            result.append(f'<text x="15" y="35" font-size="8" fill="#007bff">{angle_value}°</text>')
        result.append('</g>')
        return result
    
    def _create_construction_step(self, x: int, y: int, description: str) -> List[str]:
        """Create a construction step representation"""
        return [
            f'<g transform="translate({x - 30}, {y - 30})">',
            '<rect x="0" y="10" width="60" height="40" fill="none" stroke="#007bff" stroke-width="1" stroke-dasharray="2,2"/>',
            f'<text x="30" y="30" font-size="6" fill="#666" text-anchor="middle">{description[:20]}...</text>',
            '</g>'
        ]
    
    def _create_default_element(self, x: int, y: int, description: str) -> List[str]:
        """Create a default element representation"""
        return [
            f'<g transform="translate({x - 30}, {y - 30})">',
            '<line x1="0" y1="30" x2="60" y2="30" stroke="#333" stroke-width="2"/>',
            '<circle cx="0" cy="30" r="3" fill="#dc3545"/>',
            '<circle cx="60" cy="30" r="3" fill="#dc3545"/>',
            '<text x="-5" y="25" font-size="10" font-weight="bold" fill="#333">A</text>',
            '<text x="65" y="25" font-size="10" font-weight="bold" fill="#333">B</text>',
            f'<text x="30" y="15" font-size="6" fill="#666" text-anchor="middle">{description[:20]}...</text>',
            '</g>'
        ]

def analyze_and_generate_diagram(solution_text: str, question_text: str) -> Dict[str, Any]:
    """
    Main function to analyze solution text and generate unified diagram
    """
    analyzer = ComprehensiveDiagramAnalyzer()
    
    # Extract diagram elements
    elements = analyzer.extract_diagram_elements(solution_text)
    
    logger.info(f"Extracted {len(elements)} diagram elements")
    for elem in elements:
        logger.info(f"  - {elem.element_type}: {elem.description}")
    
    # Generate unified diagram
    unified_diagram = analyzer.generate_unified_diagram(elements, question_text)
    
    return unified_diagram

# Example usage and testing
if __name__ == "__main__":
    sample_solution = """
    To solve this problem, we need to construct a perpendicular bisector.
    
    [DIAGRAM: Line segment BC with a length of 6 cm marked on it]
    
    First, we draw the line segment and mark the measurements.
    
    [DIAGRAM: Perpendicular bisector of line segment BC]
    
    The final construction shows the perpendicular bisector.
    """
    
    sample_question = "Construct the perpendicular bisector of line segment BC with length 6cm"
    
    result = analyze_and_generate_diagram(sample_solution, sample_question)
    print(json.dumps(result, indent=2))
