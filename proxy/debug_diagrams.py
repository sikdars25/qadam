#!/usr/bin/env python3
"""
Debug script to test diagram generation end-to-end
"""

import requests
import json
import sys

def test_ai_service():
    """Test the AI service directly for diagram generation"""
    
    print("🔍 Testing AI Service Diagram Generation...")
    print("="*60)
    
    test_cases = [
        {
            'name': 'Triangle Construction',
            'data': {
                'question_text': 'Construct a triangle ABC in which BC = 6 cm, ∠B = 60°, and ∠C = 45°. Draw the figure with all steps of construction and label the diagram clearly',
                'subject': 'Mathematics',
                'context': 'Geometry construction',
                'solution_type': 'with-diagram'
            }
        },
        {
            'name': 'Simple Geometry',
            'data': {
                'question_text': 'Draw a circle with radius 5 cm and mark its center',
                'subject': 'Mathematics',
                'solution_type': 'with-diagram'
            }
        },
        {
            'name': 'Step-by-step (no diagrams)',
            'data': {
                'question_text': 'What is 2 + 2?',
                'subject': 'Mathematics',
                'solution_type': 'step-by-step'
            }
        }
    ]
    
    ai_service_url = "http://130.107.48.221:8001/api/solve-question"
    
    for test_case in test_cases:
        print(f"\n📝 Test Case: {test_case['name']}")
        print(f"Solution Type: {test_case['data']['solution_type']}")
        print("-" * 40)
        
        try:
            response = requests.post(ai_service_url, json=test_case['data'], timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Success: {result.get('success')}")
                print(f"Has Diagrams: {result.get('has_diagrams')}")
                print(f"Diagram Count: {result.get('diagram_count', 0)}")
                
                if result.get('diagrams'):
                    print(f"Diagram Data: {len(result['diagrams'])} items")
                    for i, diagram in enumerate(result['diagrams']):
                        print(f"  - Diagram {i+1}: {diagram.get('type', 'unknown')} - {diagram.get('description', 'no description')[:50]}")
                
                # Check solution text for diagram markers
                solution = result.get('solution', '')
                if '[DIAGRAM:' in solution:
                    print("✅ Solution contains diagram markers")
                    markers = [line.strip() for line in solution.split('\n') if '[DIAGRAM:' in line]
                    for marker in markers[:3]:  # Show first 3 markers
                        print(f"  Marker: {marker}")
                else:
                    print("❌ No diagram markers in solution text")
                
                # Show solution preview
                print(f"\nSolution Preview (first 300 chars):")
                print(solution[:300] + "..." if len(solution) > 300 else solution)
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to AI service")
            print("   Check if AI service is running at: http://130.107.48.221:8001")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_proxy_service():
    """Test the proxy service"""
    
    print("\n" + "="*60)
    print("🔍 Testing Proxy Service...")
    print("="*60)
    
    proxy_url = "http://130.107.48.166:5000/solve-question"
    
    test_data = {
        'question_text': 'Construct a triangle ABC in which BC = 6 cm, ∠B = 60°, and ∠C = 45°. Draw the figure with all steps of construction and label the diagram clearly',
        'subject': 'Mathematics',
        'solution_type': 'with-diagram'
    }
    
    try:
        print(f"📤 Calling proxy: {proxy_url}")
        response = requests.post(proxy_url, json=test_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Proxy responded successfully")
            print(f"Success: {result.get('success')}")
            print(f"Has Diagrams: {result.get('has_diagrams')}")
            print(f"Diagram Count: {result.get('diagram_count', 0)}")
            
            if result.get('diagrams'):
                print(f"Diagrams returned: {len(result['diagrams'])}")
            
        else:
            print(f"❌ Proxy Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to proxy service")
        print("   The proxy service may not be running or accessible")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_ai_service_health():
    """Check if AI service is running at all"""
    
    print("\n" + "="*60)
    print("🔍 Checking AI Service Health...")
    print("="*60)
    
    health_url = "http://130.107.48.221:8001/api/health"
    
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print("✅ AI service is running and healthy")
            print(f"Response: {response.json()}")
        else:
            print(f"⚠️ AI service returned: {response.status_code}")
    except Exception as e:
        print(f"❌ AI service not accessible: {e}")

if __name__ == "__main__":
    check_ai_service_health()
    test_ai_service()
    test_proxy_service()
