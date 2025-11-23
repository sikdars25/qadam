#!/usr/bin/env python3
"""
Test diagram generation locally without API calls
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from diagram_generator import DiagramGenerator, generate_diagrams_for_solution

def test_diagram_identification():
    """Test if diagram needs are identified correctly"""
    
    print("🔍 Testing Diagram Identification...")
    print("="*50)
    
    test_questions = [
        {
            'question': 'Construct a triangle ABC in which BC = 6 cm, ∠B = 60°, and ∠C = 45°. Draw the figure with all steps of construction and label the diagram clearly',
            'subject': 'Mathematics'
        },
        {
            'question': 'What is 2 + 2?',
            'subject': 'Mathematics'
        },
        {
            'question': 'Draw a circle with radius 5 cm',
            'subject': 'Mathematics'
        },
        {
            'question': 'Plot the function y = x²',
            'subject': 'Mathematics'
        }
    ]
    
    generator = DiagramGenerator()
    
    for i, test in enumerate(test_questions, 1):
        print(f"\nTest {i}: {test['question'][:50]}...")
        diagram_types = generator.identify_diagram_needs(test['question'], test['subject'])
        print(f"Diagram Types Needed: {diagram_types}")
        
        if diagram_types:
            prompt_addition = generator.create_diagram_prompt_addition(diagram_types)
            print(f"Prompt Addition: {prompt_addition[:100]}...")

def test_diagram_processing():
    """Test diagram processing with sample solution"""
    
    print("\n" + "="*50)
    print("🔍 Testing Diagram Processing...")
    print("="*50)
    
    # Sample solution with diagram markers
    sample_solution = """
### Step 1: Understanding the Triangle
[DIAGRAM: Triangle ABC with side BC = 6 cm and angles B = 60°, C = 45°]
We need to construct a triangle with the given measurements.

### Step 2: Construction Steps
[DIAGRAM: Step-by-step construction showing base BC first]
1. Draw base BC = 6 cm
2. At point B, construct angle of 60°
3. At point C, construct angle of 45°
4. The intersection gives point A

### Step 3: Final Triangle
[DIAGRAM: Complete triangle ABC with all labels]
The triangle is now complete with all sides and angles labeled.
"""
    
    question = "Construct a triangle ABC in which BC = 6 cm, ∠B = 60°, and ∠C = 45°"
    
    result = generate_diagrams_for_solution(question, sample_solution, "Mathematics")
    
    print(f"Has Diagrams: {result.get('has_diagrams')}")
    print(f"Diagram Count: {result.get('diagram_count', 0)}")
    print(f"Diagram Types: {result.get('diagram_types', [])}")
    
    if result.get('diagrams'):
        print("\nDiagrams Found:")
        for i, diagram in enumerate(result['diagrams'], 1):
            print(f"  {i}. Type: {diagram.get('type')}")
            print(f"     Content: {diagram.get('content', 'No content')[:50]}...")
    
    print(f"\nProcessed Solution Preview:")
    print(result.get('solution', 'No solution')[:300] + "...")

if __name__ == "__main__":
    test_diagram_identification()
    test_diagram_processing()
