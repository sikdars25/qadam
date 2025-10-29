"""
OCR Client - Calls the separate OCR Function App
"""

import os
import requests
from typing import Optional, Dict, Any

# OCR Function App URL
OCR_SERVICE_URL = os.getenv('OCR_SERVICE_URL', 'https://qadam-ocr.azurewebsites.net')

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
                response = requests.post(url, files=files, data=data, timeout=60)
        else:
            # File object
            files = {'file': image_file}
            data = {'language': language}
            response = requests.post(url, files=files, data=data, timeout=60)
        
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
