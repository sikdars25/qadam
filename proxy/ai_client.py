"""
AI Client - Calls the AI Service on Azure VM
Replaces direct Groq API calls with HTTP requests to VM
"""

import os
import requests
from typing import Optional, Dict, Any

# AI Service URL - Running on Azure VM
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://130.107.48.221')

def check_ai_service() -> bool:
    """Check if AI service is available"""
    try:
        url = f"{AI_SERVICE_URL}/api/health"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def solve_question_via_vm(question_text: str, subject: str = '', context: str = '') -> str:
    """
    Solve a question using AI service on VM
    
    Args:
        question_text: The question to solve
        subject: Optional subject name
        context: Optional additional context
    
    Returns:
        Solution text
    """
    try:
        url = f"{AI_SERVICE_URL}/api/solve-question"
        
        payload = {
            'question_text': question_text,
            'subject': subject,
            'context': context
        }
        
        print(f"📤 Sending question to AI service at {url}")
        response = requests.post(url, json=payload, timeout=120)  # 2 min timeout
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('solution', '')
            else:
                error = result.get('error', 'Unknown error')
                raise Exception(f"AI service error: {error}")
        else:
            raise Exception(f"AI service returned status {response.status_code}")
    
    except requests.exceptions.Timeout:
        raise Exception('AI service timeout - question may be too complex')
    except requests.exceptions.ConnectionError:
        raise Exception('Cannot connect to AI service - please check if service is running')
    except Exception as e:
        raise Exception(f"AI service error: {str(e)}")

def generate_text_via_vm(prompt: str, model: str = 'llama-3.3-70b-versatile', 
                        max_tokens: int = 1000, temperature: float = 0.7) -> str:
    """
    Generate text using AI service on VM
    
    Args:
        prompt: Text prompt
        model: Model name
        max_tokens: Maximum tokens to generate
        temperature: Temperature for generation
    
    Returns:
        Generated text
    """
    try:
        url = f"{AI_SERVICE_URL}/api/generate-text"
        
        payload = {
            'prompt': prompt,
            'model': model,
            'max_tokens': max_tokens,
            'temperature': temperature
        }
        
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('text', '')
            else:
                error = result.get('error', 'Unknown error')
                raise Exception(f"AI service error: {error}")
        else:
            raise Exception(f"AI service returned status {response.status_code}")
    
    except Exception as e:
        raise Exception(f"AI service error: {str(e)}")

def semantic_search_via_vm(query: str, documents: list, top_k: int = 5) -> list:
    """
    Perform semantic search using AI service on VM
    
    Args:
        query: Search query
        documents: List of documents to search
        top_k: Number of top results to return
    
    Returns:
        List of search results
    """
    try:
        url = f"{AI_SERVICE_URL}/api/semantic-search"
        
        payload = {
            'query': query,
            'documents': documents,
            'top_k': top_k
        }
        
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('results', [])
            else:
                error = result.get('error', 'Unknown error')
                raise Exception(f"AI service error: {error}")
        else:
            raise Exception(f"AI service returned status {response.status_code}")
    
    except Exception as e:
        raise Exception(f"AI service error: {str(e)}")

def parse_questions_via_vm(text: str) -> list:
    """
    Parse questions from text using AI service on VM
    
    Args:
        text: Text containing questions
    
    Returns:
        List of parsed questions
    """
    try:
        url = f"{AI_SERVICE_URL}/api/parse-questions"
        
        payload = {'text': text}
        
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('questions', [])
            else:
                error = result.get('error', 'Unknown error')
                raise Exception(f"AI service error: {error}")
        else:
            raise Exception(f"AI service returned status {response.status_code}")
    
    except Exception as e:
        raise Exception(f"AI service error: {str(e)}")

def map_to_chapters_via_vm(question_text: str, chapters: list) -> dict:
    """
    Map question to relevant chapters using AI service on VM
    
    Args:
        question_text: Question to map
        chapters: List of chapters
    
    Returns:
        Mapping result
    """
    try:
        url = f"{AI_SERVICE_URL}/api/map-to-chapters"
        
        payload = {
            'question_text': question_text,
            'chapters': chapters
        }
        
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('mapping', {})
            else:
                error = result.get('error', 'Unknown error')
                raise Exception(f"AI service error: {error}")
        else:
            raise Exception(f"AI service returned status {response.status_code}")
    
    except Exception as e:
        raise Exception(f"AI service error: {str(e)}")

# Check AI service on import
AI_AVAILABLE = check_ai_service()

if AI_AVAILABLE:
    print(f"✅ AI service available at {AI_SERVICE_URL}")
else:
    print(f"⚠️ AI service not available at {AI_SERVICE_URL}")
    print("   AI features will be disabled")
