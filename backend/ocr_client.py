"""
OCR Client - Calls the separate OCR Function App
Version: 1.1 - Fixed timeout and added warmup
"""

import os
import requests
from typing import Optional, Dict, Any

# OCR Function App URL
OCR_SERVICE_URL = os.getenv('OCR_SERVICE_URL', 'https://qadam-ocr-addrcugfg4d4drg7.canadacentral-01.azurewebsites.net')

def ocr_image(image_file, language: str = 'en') -> Dict[str, Any]:
    """
    Extract text from image using OCR service
    
    Args:
        image_file: File object or file path
        language: Language code (default: 'en')
    
    Returns:
        {
            'success': bool,
            'text': str,
            'confidence': float,
            'details': list
        }
    """
    try:
        url = f"{OCR_SERVICE_URL}/api/ocr/image"
        
        # Prepare file
        if isinstance(image_file, str):
            # File path
            with open(image_file, 'rb') as f:
                files = {'file': f}
                data = {'language': language}
                response = requests.post(url, files=files, data=data, timeout=120)  # 2 min timeout for model download
        else:
            # File object
            files = {'file': image_file}
            data = {'language': language}
            response = requests.post(url, files=files, data=data, timeout=120)  # 2 min timeout for model download
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'success': False,
                'error': f"OCR service error: {response.status_code}",
                'text': ''
            }
    
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'OCR service timeout',
            'text': ''
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'text': ''
        }

def ocr_pdf(pdf_file, language: str = 'en') -> Dict[str, Any]:
    """
    Extract text from PDF using OCR service
    
    Args:
        pdf_file: File object or file path
        language: Language code (default: 'en')
    
    Returns:
        {
            'success': bool,
            'text': str,
            'total_pages': int,
            'pages': list
        }
    """
    try:
        url = f"{OCR_SERVICE_URL}/api/ocr/pdf"
        
        # Prepare file
        if isinstance(pdf_file, str):
            # File path
            with open(pdf_file, 'rb') as f:
                files = {'file': f}
                data = {'language': language}
                response = requests.post(url, files=files, data=data, timeout=300)  # 5 min timeout for PDFs
        else:
            # File object
            files = {'file': pdf_file}
            data = {'language': language}
            response = requests.post(url, files=files, data=data, timeout=300)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'success': False,
                'error': f"OCR service error: {response.status_code}",
                'text': '',
                'pages': []
            }
    
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'OCR service timeout',
            'text': '',
            'pages': []
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'text': '',
            'pages': []
        }

def check_ocr_service() -> bool:
    """Check if OCR service is available"""
    try:
        url = f"{OCR_SERVICE_URL}/api/health"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def warmup_ocr_service() -> bool:
    """
    Warmup OCR service by sending a small test image
    This triggers model downloads on first run
    """
    try:
        import base64
        print(f"🔥 Warming up OCR service at {OCR_SERVICE_URL}")
        
        # 1x1 pixel PNG image
        tiny_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        url = f"{OCR_SERVICE_URL}/api/ocr/image"
        payload = {
            'image_base64': tiny_image,
            'language': 'en'
        }
        
        print(f"📤 Sending warmup request to {url}")
        response = requests.post(url, json=payload, timeout=180)  # 3 min timeout for first warmup
        
        if response.status_code == 200:
            print("✅ Warmup successful!")
            return True
        else:
            print(f"⚠️ Warmup returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Warmup failed: {e}")
        return False

def get_supported_languages() -> Dict[str, str]:
    """Get list of supported languages from OCR service"""
    try:
        url = f"{OCR_SERVICE_URL}/api/ocr/languages"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.json().get('languages', {})
        else:
            return {}
    except:
        return {}

# Check OCR service on import
OCR_AVAILABLE = check_ocr_service()

if OCR_AVAILABLE:
    print(f"✅ OCR service available at {OCR_SERVICE_URL}")
else:
    print(f"⚠️ OCR service not available at {OCR_SERVICE_URL}")
    print("   Image OCR features will be disabled")
