# 🔧 Fix ImportError on VM - Manual Instructions

## 🐛 Problem Identified

The `comprehensive_diagram_generator.py` file on the VM is empty (0 bytes), causing the ImportError:

```
ImportError: cannot import name 'analyze_and_generate_diagram' from 'comprehensive_diagram_generator'
```

## ✅ Solution - Manual Fix on VM

### **Step 1: SSH to VM**

```bash
ssh qadamuser@130.107.48.166
```

### **Step 2: Navigate to Proxy Directory**

```bash
cd /opt/qadam-backend/proxy
```

### **Step 3: Check File Status**

```bash
ls -la comprehensive_diagram_generator.py
# Should show 0 bytes (empty file)

wc -l comprehensive_diagram_generator.py
# Should show 0 lines
```

### **Step 4: Remove Empty File**

```bash
rm comprehensive_diagram_generator.py
```

### **Step 5: Create New File with Content**

```bash
cat > comprehensive_diagram_generator.py << 'EOF'
#!/usr/bin/env python3
"""
Comprehensive Diagram Generator
Analyzes all diagram texts from AI solution and creates a single unified diagram
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
            'line_with_angles': r'\[DIAGRAM:\s*(?:A )?simple line segment\s*([A-Z]+)\s*with angle measurements\s*for\s*([A-Z]+)\s*and\s*([A-Z]+)(?:\s*(.+?))?\]',
            'triangle': r'\[DIAGRAM:\s*(?:A )?triangle\s*([A-Z]+)(?:\s*(.+?))?\]',
            'perpendicular': r'\[DIAGRAM:\s*(?:A )?perpendicular\s+(?:bisector|line)\s*(?:of\s*)?(?:line segment\s*)?([A-Z]+)(?:\s*(.+?))?\]',
            'circle': r'\[DIAGRAM:\s*(?:A )?circle\s*(?:with\s*)?(?:center\s*)?([A-Z]+)(?:\s*(.+?))?\]',
            'angle': r'\[DIAGRAM:\s*(?:An )?angle\s*([A-Z]+)(?:\s*(.+?))?\]',
            'general': r'\[DIAGRAM:\s*(.+?)\]'
        }
    
    def extract_diagram_elements(self, solution_text: str) -> List[DiagramElement]:
        """Extract all diagram elements from solution text"""
        elements = []
        
        for pattern_name, pattern in self.diagram_patterns.items():
            matches = re.finditer(pattern, solution_text, re.IGNORECASE)
            
            for match in matches:
                if pattern_name == 'general' and any(other_match in elements for other_match in elements):
                    continue  # Skip general pattern if specific patterns matched
                
                element = self._parse_diagram_match(match, pattern_name)
                if element:
                    elements.append(element)
        
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
            
            elif pattern_name == 'line_with_angles':
                points = [match.group(1), match.group(2), match.group(3)]
                return DiagramElement(
                    text=text,
                    element_type='line_with_angles',
                    points=points,
                    measurements={},
                    description=f"Line segment {points[0]} with angle measurements for {points[1]} and {points[2]}"
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
            
            elif pattern_name == 'circle':
                points = [match.group(1)]
                return DiagramElement(
                    text=text,
                    element_type='circle',
                    points=points,
                    measurements={},
                    description=f"Circle with center {points[0]}"
                )
            
            elif pattern_name == 'angle':
                points = [match.group(1)]
                return DiagramElement(
                    text=text,
                    element_type='angle',
                    points=points,
                    measurements={},
                    description=f"Angle {points[0]}"
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
        
        # Analyze elements to determine the best unified representation
        diagram_type = self._determine_diagram_type(elements)
        
        if diagram_type == 'construction_sequence':
            return self._generate_construction_sequence(elements, question_text)
        elif diagram_type == 'geometric_figure':
            return self._generate_geometric_figure(elements, question_text)
        else:
            return self._generate_combined_diagram(elements, question_text)
    
    def _determine_diagram_type(self, elements: List[DiagramElement]) -> str:
        """Determine the type of unified diagram to create"""
        types = [elem.element_type for elem in elements]
        
        if 'perpendicular' in types or 'line_with_length' in types:
            return 'construction_sequence'
        elif 'triangle' in types or 'circle' in types:
            return 'geometric_figure'
        else:
            return 'combined'
    
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
    
    def _generate_geometric_figure(self, elements: List[DiagramElement], question_text: str) -> Dict[str, Any]:
        """Generate a geometric figure diagram"""
        svg_content = self._create_geometric_svg(elements, question_text)
        
        return {
            'type': 'geometric_figure',
            'svg': svg_content,
            'description': f"Geometric construction for: {question_text[:50]}...",
            'elements_count': len(elements),
            'components': [elem.description for elem in elements]
        }
    
    def _generate_combined_diagram(self, elements: List[DiagramElement], question_text: str) -> Dict[str, Any]:
        """Generate a combined diagram with multiple elements"""
        svg_content = self._create_combined_svg(elements, question_text)
        
        return {
            'type': 'combined',
            'svg': svg_content,
            'description': f"Combined diagram for: {question_text[:50]}...",
            'elements_count': len(elements),
            'parts': [elem.description for elem in elements]
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
        
        # Process each element
        for i, element in enumerate(elements):
            x = start_x + (i * step_spacing)
            
            # Add connection line
            if i > 0:
                prev_x = start_x + ((i-1) * step_spacing)
                svg_lines.append(f'<line x1="{prev_x + 60}" y1="{start_y}" x2="{x - 20}" y2="{start_y}" stroke="#007bff" stroke-width="2" stroke-dasharray="5,5"/>')
                svg_lines.append(f'<text x="{prev_x + step_spacing//2}" y="{start_y - 10}" font-size="10" fill="#007bff" text-anchor="middle">Step {i}</text>')
            
            # Add specific construction based on element type
            if element.element_type == 'line_with_length':
                length = element.measurements.get('length', '6')
                svg_lines.extend(self._create_line_segment(x, start_y, element.points[0], length))
            elif element.element_type == 'perpendicular':
                svg_lines.extend(self._create_perpendicular_bisector(x, start_y, element.points[0]))
            elif element.element_type == 'triangle':
                svg_lines.extend(self._create_triangle(x, start_y, element.points[0]))
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
        return [
            f'<g transform="translate({x - 30}, {y - 30})">',
            '<line x1="0" y1="30" x2="60" y2="30" stroke="#333" stroke-width="2"/>',
            '<circle cx="0" cy="30" r="3" fill="#dc3545"/>',
            '<circle cx="60" cy="30" r="3" fill="#dc3545"/>',
            f'<text x="-5" y="25" font-size="10" font-weight="bold" fill="#333">{point_name[0] if len(point_name) > 0 else "B"}</text>',
            f'<text x="65" y="25" font-size="10" font-weight="bold" fill="#333">{point_name[1] if len(point_name) > 1 else "C"}</text>',
            f'<text x="25" y="20" font-size="8" fill="#007bff" text-anchor="middle">{length}</text>',
            '<path d="M 0 35 L 60 35" stroke="#007bff" stroke-width="1"/>',
            '<path d="M 55 30 L 60 35 L 55 40" stroke="#007bff" stroke-width="1" fill="none"/>',
            '</g>'
        ]
    
    def _create_perpendicular_bisector(self, x: int, y: int, point_name: str) -> List[str]:
        """Create a perpendicular bisector"""
        return [
            f'<g transform="translate({x - 30}, {y - 40})">',
            '<line x1="0" y1="40" x2="60" y2="40" stroke="#333" stroke-width="2"/>',
            '<line x1="30" y1="20" x2="30" y2="60" stroke="#007bff" stroke-width="2"/>',
            '<circle cx="0" cy="40" r="3" fill="#dc3545"/>',
            '<circle cx="60" cy="40" r="3" fill="#dc3545"/>',
            '<circle cx="30" cy="40" r="3" fill="#007bff"/>',
            f'<text x="-5" y="35" font-size="10" font-weight="bold" fill="#333">{point_name[0] if len(point_name) > 0 else "P"}</text>',
            f'<text x="65" y="35" font-size="10" font-weight="bold" fill="#333">{point_name[1] if len(point_name) > 1 else "Q"}</text>',
            f'<text x="32" y="18" font-size="10" font-weight="bold" fill="#007bff">M</text>',
            '<rect x="25" y="35" width="10" height="10" fill="none" stroke="#007bff" stroke-width="1"/>',
            '</g>'
        ]
    
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
    
    def _create_geometric_svg(self, elements: List[DiagramElement], question_text: str) -> str:
        """Create SVG for geometric figures"""
        # Similar to construction but with different layout
        return self._create_construction_svg(elements, question_text)
    
    def _create_combined_svg(self, elements: List[DiagramElement], question_text: str) -> str:
        """Create SVG for combined elements"""
        # Similar to construction but with different layout
        return self._create_construction_svg(elements, question_text)

def analyze_and_generate_diagram(solution_text: str, question_text: str) -> Dict[str, Any]:
    """
    Main function to analyze solution text and generate unified diagram
    
    Args:
        solution_text: The AI solution text containing diagram markers
        question_text: The original question text
        
    Returns:
        Dictionary containing the unified diagram
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
    # Test with sample solution text
    sample_solution = """
    To solve this problem, we need to construct a perpendicular bisector.
    
    [DIAGRAM: Line segment BC with a length of 6 cm marked on it]
    
    First, we draw the line segment and mark the measurements.
    
    [DIAGRAM: A simple line segment BC with angle measurements for B and C]
    
    Then we construct the perpendicular bisector.
    
    [DIAGRAM: Perpendicular bisector of line segment BC]
    
    The final construction shows the perpendicular bisector.
    """
    
    sample_question = "Construct the perpendicular bisector of line segment BC with length 6cm"
    
    result = analyze_and_generate_diagram(sample_solution, sample_question)
    print(json.dumps(result, indent=2))
EOF
```

### **Step 6: Verify File Creation**

```bash
ls -la comprehensive_diagram_generator.py
# Should show non-zero size

wc -l comprehensive_diagram_generator.py
# Should show 388 lines
```

### **Step 7: Test Import**

```bash
python3 -c "from comprehensive_diagram_generator import analyze_and_generate_diagram; print('Import successful!')"
```

### **Step 8: Test Functionality**

```bash
python3 comprehensive_diagram_generator.py
# Should output sample diagram analysis
```

### **Step 9: Start Diagram Service**

```bash
python3 diagram_endpoint.py
```

## 🧪 Alternative: Use Git to Restore File

If the manual creation doesn't work, you can use git to restore the file:

```bash
cd /opt/qadam-backend
git checkout backend-proxy
git pull origin backend-proxy

# Verify file is restored
ls -la proxy/comprehensive_diagram_generator.py
```

## ✅ Verification

After fixing the file:

1. **Import works**: `from comprehensive_diagram_generator import analyze_and_generate_diagram`
2. **Service starts**: `python3 diagram_endpoint.py` runs without ImportError
3. **Endpoint works**: `curl http://localhost:5001/analyze-diagrams` returns responses
4. **Diagrams generate**: Frontend displays unified diagrams

## 🎯 Expected Result

The ImportError will be resolved and the diagram service will start successfully, allowing the comprehensive diagram analysis to work end-to-end with the AI service integration.
