#!/usr/bin/env python3
"""
Test script to verify AI service is returning diagram data
Run this on the AI VM to check the response
"""

import requests
import json

def test_ai_diagrams():
    """Test if AI service returns diagram data"""
    
    print("🔍 Testing AI Service Diagram Generation...")
    print("="*60)
    
    url = "http://localhost:8001/api/solve-question"
    
    test_data = {
        'question_text': 'Construct a triangle ABC in which BC = 6 cm, ∠B = 60°, and ∠C = 45°. Draw the figure with all steps of construction and label the diagram clearly',
        'subject': 'Mathematics',
        'solution_type': 'with-diagram'
    }
    
    print(f"📤 Testing: {test_data['question_text'][:60]}...")
    print(f"Solution Type: {test_data['solution_type']}")
    print(f"URL: {url}")
    print("-" * 40)
    
    try:
        response = requests.post(url, json=test_data, timeout=60)
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ AI Service Responded Successfully")
            print(f"Success: {result.get('success')}")
            print(f"Has Diagrams: {result.get('has_diagrams')}")
            print(f"Diagram Count: {result.get('diagram_count', 0)}")
            
            # Check solution content
            solution = result.get('solution', '')
            if solution:
                print(f"Solution Length: {len(solution)} characters")
                
                # Check for diagram markers
                if '[DIAGRAM:' in solution:
                    print("✅ Solution contains diagram markers!")
                    markers = [line.strip() for line in solution.split('\n') if '[DIAGRAM:' in line]
                    print(f"Found {len(markers)} diagram markers:")
                    for i, marker in enumerate(markers[:3], 1):
                        print(f"  {i}. {marker}")
                else:
                    print("❌ No diagram markers in solution")
                
                # Show solution preview
                print(f"\nSolution Preview (first 800 chars):")
                print(solution[:800] + "..." if len(solution) > 800 else solution)
            
            # Check diagrams array
            diagrams = result.get('diagrams', [])
            if diagrams:
                print(f"\n✅ Diagrams array contains {len(diagrams)} items:")
                for i, diagram in enumerate(diagrams[:2], 1):
                    print(f"  Diagram {i}: {diagram}")
            else:
                print("\n❌ Diagrams array is empty")
            
            # Show all response keys
            print(f"\n📋 Response Keys: {list(result.keys())}")
            
            # Critical check
            has_diagrams = result.get('has_diagrams', False)
            if has_diagrams:
                print("\n🎉 SUCCESS: AI service is generating diagrams!")
                print("Frontend should receive diagram data and display diagrams.")
            else:
                print("\n❌ ISSUE: AI service not generating diagrams")
                print("Check the diagram generation logic in intelligent_question_solver.py")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_ai_diagrams()
