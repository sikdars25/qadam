#!/usr/bin/env python3
"""
Test script to verify diagram generation is working
"""

import requests
import json

def test_diagram_generation():
    """Test if the AI service generates diagrams for geometry questions"""
    
    # Test the triangle construction question
    test_question = {
        'question_text': 'Construct a triangle ABC in which BC = 6 cm, ∠B = 60°, and ∠C = 45°. Draw the figure with all steps of construction and label the diagram clearly',
        'subject': 'Mathematics',
        'context': 'Geometry construction',
        'solution_type': 'with-diagram'
    }
    
    print("🔍 Testing diagram generation...")
    print(f"Question: {test_question['question_text'][:60]}...")
    print(f"Solution Type: {test_question['solution_type']}")
    print()
    
    try:
        # Call the AI service directly
        ai_service_url = "http://130.107.48.221:8001/api/solve-question"
        print(f"📤 Calling AI service at: {ai_service_url}")
        
        response = requests.post(ai_service_url, json=test_question, timeout=60)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI service responded successfully")
            print()
            
            # Check for diagram-related fields
            print("🔍 Checking for diagram data:")
            print(f"  - Success: {result.get('success')}")
            print(f"  - Has Diagrams: {result.get('has_diagrams')}")
            print(f"  - Diagram Count: {result.get('diagram_count', 0)}")
            print(f"  - Diagrams Present: {'diagrams' in result}")
            
            if result.get('diagrams'):
                print(f"  - Diagram Types: {[d.get('type') for d in result['diagrams']]}")
            
            print()
            print("📝 Solution Preview (first 500 chars):")
            solution = result.get('solution', '')
            print(solution[:500] + "..." if len(solution) > 500 else solution)
            
            # Check if solution contains diagram markers
            if '[DIAGRAM:' in solution:
                print("\n✅ Solution contains diagram markers")
                diagram_markers = [line for line in solution.split('\n') if '[DIAGRAM:' in line]
                for marker in diagram_markers:
                    print(f"  - {marker.strip()}")
            else:
                print("\n❌ No diagram markers found in solution")
                
        else:
            print(f"❌ AI service error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to AI service")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_proxy_endpoint():
    """Test the proxy endpoint with diagram generation"""
    
    print("\n" + "="*60)
    print("🔍 Testing proxy endpoint...")
    
    test_question = {
        'question_text': 'Construct a triangle ABC in which BC = 6 cm, ∠B = 60°, and ∠C = 45°. Draw the figure with all steps of construction and label the diagram clearly',
        'subject': 'Mathematics',
        'solution_type': 'with-diagram'
    }
    
    try:
        # Test locally if proxy is running, otherwise show instructions
        proxy_url = "http://localhost:8000/solve-question"
        print(f"📤 Calling proxy at: {proxy_url}")
        
        response = requests.post(proxy_url, json=test_question, timeout=60)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Proxy responded successfully")
            print(f"  - Has Diagrams: {result.get('has_diagrams')}")
            print(f"  - Diagram Count: {result.get('diagram_count', 0)}")
        else:
            print(f"❌ Proxy error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to local proxy")
        print("💡 To test proxy, run it locally or test on the server")

if __name__ == "__main__":
    test_diagram_generation()
    test_proxy_endpoint()
