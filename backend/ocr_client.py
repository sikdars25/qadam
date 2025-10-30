"""
OCR Client - Calls the separate OCR Function App
Version: 1.2 - Added automatic image resizing
"""

import os
import requests
from typing import Optional, Dict, Any
from PIL import Image
import io

# OCR Function App URL
OCR_SERVICE_URL = os.getenv('OCR_SERVICE_URL', 'https://qadam-ocr-addrcugfg4d4drg7.canadacentral-01.azurewebsites.net')

def preprocess_image(image_bytes: bytes, max_dimension: int = 2048) -> bytes:
    """
    Preprocess image before OCR:
    - Resize if too large
    - Optimize file size
    - Validate format
    
    Args:
        image_bytes: Raw image bytes
        max_dimension: Maximum width or height (default: 2048)
    
    Returns:
        Processed image bytes
    """
    try:
        # Open image
        img = Image.open(io.BytesIO(image_bytes))
        original_size = img.size
        
        # Check if resize needed
        if max(img.size) > max_dimension:
            print(f"📏 Resizing image from {img.size} to fit {max_dimension}px")
            
            # Calculate new size maintaining aspect ratio
            ratio = max_dimension / max(img.size)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            
            # Resize with high-quality algorithm
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            print(f"✅ Resized to {img.size}")
        
        # Convert to RGB if needed (remove alpha channel)
        if img.mode in ('RGBA', 'LA', 'P'):
            print(f"🎨 Converting {img.mode} to RGB")
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # Save optimized
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        processed_bytes = buffer.getvalue()
        
        # Log size reduction
        original_kb = len(image_bytes) / 1024
        processed_kb = len(processed_bytes) / 1024
        if original_kb > processed_kb:
            print(f"💾 Reduced size: {original_kb:.1f}KB → {processed_kb:.1f}KB")
        
        return processed_bytes
        
    except Exception as e:
        print(f"⚠️ Image preprocessing failed: {e}")
        # Return original if preprocessing fails
        return image_bytes

def ocr_image_with_retry(image_file, language: str = 'en', max_retries: int = 3) -> Dict[str, Any]:
    """
    Extract text from image with automatic retry on failure
    
    Args:
        image_file: File object or file path
        language: Language code (default: 'en')
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        OCR result dictionary
    """
    import time
    
    for attempt in range(max_retries):
        result = ocr_image(image_file, language)
        
        if result.get('success'):
            return result
        
        # Check if error is retryable
        error = result.get('error', '')
        is_retryable = (
            'could not execute a primitive' in error or
            'RuntimeError' in error or
            'timeout' in error.lower() or
            '500' in error
        )
        
        if is_retryable and attempt < max_retries - 1:
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            print(f"⚠️ OCR failed (attempt {attempt + 1}/{max_retries}): {error}")
            print(f"   Retrying in {wait_time}s...")
            time.sleep(wait_time)
            continue
        
        # Non-retryable error or max retries reached
        return result
    
    return {'success': False, 'error': 'Max retries exceeded', 'text': ''}

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
        
        # Read image bytes
        if isinstance(image_file, str):
            # File path
            with open(image_file, 'rb') as f:
                image_bytes = f.read()
        else:
            # File object
            image_bytes = image_file.read()
        
        # Preprocess image (resize if needed)
        print(f"📸 Original image size: {len(image_bytes) / 1024:.1f}KB")
        processed_bytes = preprocess_image(image_bytes)
        print(f"📸 Processed image size: {len(processed_bytes) / 1024:.1f}KB")
        
        # Send to OCR service
        files = {'file': ('image.png', io.BytesIO(processed_bytes), 'image/png')}
        data = {'language': language}
        response = requests.post(url, files=files, data=data, timeout=120)  # 2 min timeout
        
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
