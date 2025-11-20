"""
Diagram Generator for Mathematical and Scientific Solutions
Generates ASCII art diagrams and structured diagram data for frontend rendering
"""

import re
from typing import Dict, List, Any, Optional

class DiagramGenerator:
    """Generate diagrams for mathematical and scientific concepts"""
    
    @staticmethod
    def identify_diagram_needs(question_text: str, subject: str = '') -> List[str]:
        """
        Identify what types of diagrams would be helpful for the question
        
        Args:
            question_text: The question text
            subject: Subject context
            
        Returns:
            List of diagram types needed
        """
        diagram_types = []
        question_lower = question_text.lower()
        
        # Geometry diagrams
        if any(keyword in question_lower for keyword in [
            'triangle', 'circle', 'rectangle', 'square', 'polygon',
            'angle', 'perpendicular', 'parallel', 'diagonal',
            'radius', 'diameter', 'chord', 'tangent', 'arc',
            'vertex', 'vertices', 'side', 'base', 'height'
        ]):
            diagram_types.append('geometry')
        
        # Graph/Function diagrams
        if any(keyword in question_lower for keyword in [
            'graph', 'plot', 'function', 'curve', 'parabola',
            'line', 'slope', 'intercept', 'axis', 'coordinate',
            'quadratic', 'linear', 'polynomial', 'equation y='
        ]):
            diagram_types.append('graph')
        
        # Number line diagrams
        if any(keyword in question_lower for keyword in [
            'number line', 'inequality', 'interval', 'range',
            'greater than', 'less than', 'between'
        ]):
            diagram_types.append('number_line')
        
        # Vector diagrams
        if any(keyword in question_lower for keyword in [
            'vector', 'force', 'velocity', 'displacement',
            'magnitude', 'direction', 'component'
        ]):
            diagram_types.append('vector')
        
        # Tree diagrams (probability, logic)
        if any(keyword in question_lower for keyword in [
            'probability tree', 'decision tree', 'outcomes',
            'branches', 'sample space'
        ]):
            diagram_types.append('tree')
        
        # Venn diagrams
        if any(keyword in question_lower for keyword in [
            'venn', 'sets', 'union', 'intersection',
            'subset', 'universal set'
        ]):
            diagram_types.append('venn')
        
        # Physics diagrams
        if any(keyword in question_lower for keyword in [
            'circuit', 'pulley', 'incline', 'free body',
            'projectile', 'motion', 'trajectory'
        ]):
            diagram_types.append('physics')
        
        return diagram_types
    
    @staticmethod
    def generate_geometry_diagram(description: str) -> Dict[str, Any]:
        """Generate geometry diagram data"""
        description_lower = description.lower()
        
        # Triangle
        if 'triangle' in description_lower:
            if 'right' in description_lower:
                ascii_art = """
        |\
        | \
        |  \
      b |   \ c
        |    \
        |     \
        |______\
           a
"""
                return {
                    'type': 'geometry',
                    'subtype': 'right_triangle',
                    'ascii': ascii_art,
                    'description': 'Right Triangle',
                    'labels': ['a (base)', 'b (height)', 'c (hypotenuse)']
                }
            else:
                ascii_art = """
          /\
         /  \
      b /    \ c
       /      \
      /________\
          a
"""
                return {
                    'type': 'geometry',
                    'subtype': 'triangle',
                    'ascii': ascii_art,
                    'description': 'Triangle',
                    'labels': ['a', 'b', 'c (sides)']
                }
        
        # Circle
        elif 'circle' in description_lower:
            ascii_art = """
        * * *
      *       *
     *    •    *  ← radius (r)
    *           *
     *         *
      *       *
        * * *
       center
"""
            return {
                'type': 'geometry',
                'subtype': 'circle',
                'ascii': ascii_art,
                'description': 'Circle',
                'labels': ['r (radius)', 'center']
            }
        
        # Rectangle
        elif 'rectangle' in description_lower or 'square' in description_lower:
            ascii_art = """
    ___________
    |         |
  h |         | h
    |         |
    |_________|
        w
"""
            return {
                'type': 'geometry',
                'subtype': 'rectangle',
                'ascii': ascii_art,
                'description': 'Rectangle',
                'labels': ['w (width)', 'h (height)']
            }
        
        return None
    
    @staticmethod
    def generate_graph_diagram(equation: str = None) -> Dict[str, Any]:
        """Generate coordinate graph diagram"""
        ascii_art = """
      y
      |
    4 |     *
    3 |   *
    2 | *
    1 *
    0 +----------- x
     -2 -1 0 1 2
   -1 |
   -2 |
"""
        return {
            'type': 'graph',
            'subtype': 'coordinate_plane',
            'ascii': ascii_art,
            'description': f'Graph of {equation}' if equation else 'Coordinate Plane',
            'equation': equation
        }
    
    @staticmethod
    def generate_number_line(range_start: int = -5, range_end: int = 5, 
                            highlight: List[int] = None) -> Dict[str, Any]:
        """Generate number line diagram"""
        ascii_art = f"""
    <---|---|---|---|---|---|---|---|---|---|---|----->
       {range_start}  -3  -1   0   1   3   5   7   9  {range_end}
"""
        if highlight:
            ascii_art += f"\n    Highlighted: {', '.join(map(str, highlight))}"
        
        return {
            'type': 'number_line',
            'ascii': ascii_art,
            'description': 'Number Line',
            'range': [range_start, range_end],
            'highlight': highlight or []
        }
    
    @staticmethod
    def generate_vector_diagram(vectors: List[str] = None) -> Dict[str, Any]:
        """Generate vector diagram"""
        ascii_art = """
      y
      |
      |    →
      |   v₂
      |  /
      | /
      |/___→___ x
           v₁
"""
        return {
            'type': 'vector',
            'ascii': ascii_art,
            'description': 'Vector Diagram',
            'vectors': vectors or ['v₁', 'v₂']
        }
    
    @staticmethod
    def generate_step_diagram(step_number: int, step_description: str, 
                             diagram_type: str, context: str = '') -> Dict[str, Any]:
        """
        Generate diagram for a specific solution step
        
        Args:
            step_number: Step number in solution
            step_description: Description of the step
            diagram_type: Type of diagram needed
            context: Additional context
            
        Returns:
            Diagram data structure
        """
        diagram = None
        
        if diagram_type == 'geometry':
            diagram = DiagramGenerator.generate_geometry_diagram(step_description + ' ' + context)
        elif diagram_type == 'graph':
            # Extract equation if present
            equation_match = re.search(r'y\s*=\s*[^,\n]+', step_description)
            equation = equation_match.group(0) if equation_match else None
            diagram = DiagramGenerator.generate_graph_diagram(equation)
        elif diagram_type == 'number_line':
            diagram = DiagramGenerator.generate_number_line()
        elif diagram_type == 'vector':
            diagram = DiagramGenerator.generate_vector_diagram()
        
        if diagram:
            diagram['step_number'] = step_number
            diagram['step_description'] = step_description
            
        return diagram
    
    @staticmethod
    def create_diagram_prompt_addition(diagram_types: List[str]) -> str:
        """
        Create additional prompt text to request diagram descriptions
        
        Args:
            diagram_types: List of diagram types needed
            
        Returns:
            Additional prompt text
        """
        if not diagram_types:
            return ""
        
        diagram_instructions = """

IMPORTANT - DIAGRAM INTEGRATION:
This question requires visual diagrams. For each relevant step:
1. Indicate where a diagram would be helpful by adding: [DIAGRAM: description]
2. Describe what the diagram should show
3. Continue with the explanation

Example:
### Step 1: Understanding the Triangle
[DIAGRAM: Right triangle with sides a=3, b=4, c=?]
We have a right triangle where...

### Step 2: Apply Pythagorean Theorem
Using the formula c² = a² + b²
[DIAGRAM: Show the equation with the triangle]
Substituting values: c² = 3² + 4²

Include diagrams at these points:
"""
        
        for dtype in diagram_types:
            if dtype == 'geometry':
                diagram_instructions += "\n- When introducing geometric shapes or relationships"
            elif dtype == 'graph':
                diagram_instructions += "\n- When discussing functions or coordinate points"
            elif dtype == 'number_line':
                diagram_instructions += "\n- When showing inequalities or ranges"
            elif dtype == 'vector':
                diagram_instructions += "\n- When explaining vector operations"
        
        return diagram_instructions
    
    @staticmethod
    def parse_solution_with_diagrams(solution_text: str, 
                                     diagram_types: List[str]) -> Dict[str, Any]:
        """
        Parse solution text and extract diagram markers
        
        Args:
            solution_text: The solution text with [DIAGRAM: ...] markers
            diagram_types: Types of diagrams to generate
            
        Returns:
            Structured solution with diagrams
        """
        # Find all diagram markers
        diagram_pattern = r'\[DIAGRAM:\s*([^\]]+)\]'
        diagram_matches = list(re.finditer(diagram_pattern, solution_text))
        
        if not diagram_matches:
            return {
                'solution': solution_text,
                'diagrams': [],
                'has_diagrams': False
            }
        
        # Generate diagrams
        diagrams = []
        for i, match in enumerate(diagram_matches):
            description = match.group(1).strip()
            
            # Determine diagram type from description or use first available
            diagram_type = diagram_types[0] if diagram_types else 'geometry'
            
            # Generate diagram
            diagram = DiagramGenerator.generate_step_diagram(
                step_number=i + 1,
                step_description=description,
                diagram_type=diagram_type,
                context=description
            )
            
            if diagram:
                diagram['position'] = match.start()
                diagram['marker'] = match.group(0)
                diagrams.append(diagram)
        
        # Replace markers with diagram placeholders
        solution_with_placeholders = solution_text
        for i, diagram in enumerate(diagrams):
            placeholder = f"\n\n{{{{DIAGRAM_{i}}}}}\n\n"
            solution_with_placeholders = solution_with_placeholders.replace(
                diagram['marker'], placeholder, 1
            )
        
        return {
            'solution': solution_with_placeholders,
            'diagrams': diagrams,
            'has_diagrams': True,
            'diagram_count': len(diagrams)
        }


def generate_diagrams_for_solution(question_text: str, solution_text: str, 
                                   subject: str = '') -> Dict[str, Any]:
    """
    Main function to generate diagrams for a solution
    
    Args:
        question_text: Original question
        solution_text: Solution text (may contain [DIAGRAM: ...] markers)
        subject: Subject context
        
    Returns:
        Solution with embedded diagrams
    """
    generator = DiagramGenerator()
    
    # Identify what diagrams are needed
    diagram_types = generator.identify_diagram_needs(question_text, subject)
    
    # Parse solution and generate diagrams
    result = generator.parse_solution_with_diagrams(solution_text, diagram_types)
    
    # Add metadata
    result['diagram_types'] = diagram_types
    result['question_text'] = question_text
    
    return result
