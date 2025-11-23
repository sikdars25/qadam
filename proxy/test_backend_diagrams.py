#!/usr/bin/env python3
"""
Test if the backend is generating diagram data correctly
"""

import requests
import json

def test_proxy_diagrams():
    """Test the proxy endpoint directly for diagram generation"""
    
    print("🔍 Testing Backend Proxy for Diagram Generation...")
    print("="*60)
    
    proxy_url = "http://localhost:8000/solve-question"
    
    test_data = {
        'question_text': 'Construct a triangle ABC in which BC = 6 cm, ∠B = 60°, and ∠C = 45°. Draw the figure with all steps of construction and label the diagram clearly',
        'subject': 'Mathematics',
        'solution_type': 'with-diagram'
    }
    
    print(f"📤 Testing with: {test_data['question_text'][:60]}...")
    print(f"Solution Type: {test_data['solution_type']}")
    print(f"Proxy URL: {proxy_url}")
    print("-" * 40)
    
    try:
        response = requests.post(proxy_url, json=test_data, timeout=60)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Proxy responded successfully")
            print(f"Success: {result.get('success')}")
            print(f"Has Diagrams: {result.get('has_diagrams')}")
            print(f"Diagram Count: {result.get('diagram_count', 0)}")
            
            # Check if solution exists
            solution = result.get('solution', '')
            if solution:
                print(f"Solution Length: {len(solution)} characters")
                
                # Check for diagram markers in solution
                if '[DIAGRAM:' in solution:
                    print("✅ Solution contains diagram markers")
                    markers = [line.strip() for line in solution.split('\n') if '[DIAGRAM:' in line]
                    print(f"Found {len(markers)} diagram markers:")
                    for marker in markers[:3]:
                        print(f"  - {marker}")
                else:
                    print("❌ No diagram markers in solution text")
                
                # Show solution preview
                print(f"\nSolution Preview (first 500 chars):")
                print(solution[:500] + "..." if len(solution) > 500 else solution)
                
            else:
                print("❌ No solution in response")
                
            # Show full response structure
            print(f"\n📋 Response Keys: {list(result.keys())}")
            
        else:
            print(f"❌ Proxy Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to proxy service")
        print("💡 The proxy service is not running locally")
        print("💡 This test needs to be run on the server: 130.107.48.166")
        
        print("\n" + "="*60)
        print("🔍 Testing AI Service Directly...")
        print("="*60)
        
        test_ai_service_direct()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_ai_service_direct():
    """Test the AI service directly"""
    
    ai_url = "http://130.107.48.221:8001/api/solve-question"
    
    test_data = {
        'question_text': 'Construct a triangle ABC in which BC = 6 cm, ∠B = 60°, and ∠C = 45°. Draw the figure with all steps of construction and label the diagram clearly',
        'subject': 'Mathematics',
        'solution_type': 'with-diagram'
    }
    
    print(f"📤 Testing AI Service: {ai_url}")
    
    try:
        response = requests.post(ai_url, json=test_data, timeout=60)
        
        print(f"📥 AI Service Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Service responded")
            print(f"Success: {result.get('success')}")
            print(f"Has Diagrams: {result.get('has_diagrams')}")
            print(f"Diagram Count: {result.get('diagram_count', 0)}")
            
            solution = result.get('final_answer', '')
            if '[DIAGRAM:' in solution:
                print("✅ AI service generates diagram markers")
            else:
                print("❌ AI service not generating diagram markers")
                
        else:
            print(f"❌ AI Service Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ AI Service Error: {e}")

def check_local_backend():
    """Check if local backend is configured correctly"""
    
    print("\n" + "="*60)
    print("🔍 Checking Local Backend Configuration...")
    print("="*60)
    
    try:
        # Import ai_client to check configuration
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from ai_client import AI_SERVICE_URL, AI_ENABLED, check_ai_service
        
        print(f"AI_SERVICE_URL: {AI_SERVICE_URL}")
        print(f"AI_ENABLED: {AI_ENABLED}")
        
        # Check if AI service is available
        ai_available = check_ai_service()
        print(f"AI Service Available: {ai_available}")
        
        if not ai_available:
            print("❌ AI service is not reachable from this backend")
            print("💡 This means diagrams won't be generated")
            print("💡 Frontend fallback diagrams should still work")
        
    except ImportError as e:
        print(f"❌ Cannot import ai_client: {e}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")

if __name__ == "__main__":
    check_local_backend()
    test_proxy_diagrams()
