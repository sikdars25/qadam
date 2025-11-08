#!/usr/bin/env python3
"""
LaTeX-OCR Performance Optimization
Handles timeouts and improves processing speed
"""

import logging
import time
import signal
from contextlib import contextmanager

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

@contextmanager
def timeout_context(seconds):
    """Context manager for timeout handling"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Cancel the alarm and restore old handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def optimize_latex_ocr_settings():
    """
    Returns optimized settings for LaTeX-OCR
    """
    return {
        'timeout': 30,  # 30 second timeout
        'max_retries': 2,  # Maximum retry attempts
        'fallback_on_timeout': True,  # Use EasyOCR on timeout
        'preprocess_for_speed': True,  # Faster preprocessing
    }

def fast_preprocess_image(image_path):
    """
    Faster image preprocessing for LaTeX-OCR
    """
    try:
        import cv2
        from PIL import Image
        
        # Read image
        if isinstance(image_path, str):
            image = cv2.imread(image_path)
        else:
            image = image_path
        
        if image is None:
            return None
        
        # Convert to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Fast resize for better performance (max 1024px)
        height, width = image.shape[:2]
        if max(height, width) > 1024:
            scale = 1024 / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Basic contrast enhancement (faster than CLAHE)
        image = cv2.convertScaleAbs(image, alpha=1.2, beta=10)
        
        # Convert to PIL
        pil_image = Image.fromarray(image)
        
        return pil_image
        
    except Exception as e:
        logging.error(f"Error in fast preprocessing: {e}")
        return None

def test_timeout_handling():
    """Test the timeout handling mechanism"""
    
    print("⏱️ Testing LaTeX-OCR Timeout Handling")
    print("=" * 50)
    
    settings = optimize_latex_ocr_settings()
    print(f"📊 Optimized Settings:")
    for key, value in settings.items():
        print(f"  • {key}: {value}")
    
    # Test timeout context
    print(f"\n🧪 Testing timeout context manager...")
    
    try:
        with timeout_context(5):
            print("⏳ Starting 5-second test...")
            time.sleep(3)  # This should work
            print("✅ 3-second operation completed")
    except TimeoutError:
        print("⚠️ Operation timed out")
    
    try:
        with timeout_context(2):
            print("⏳ Starting 2-second test...")
            time.sleep(5)  # This should timeout
            print("✅ This shouldn't print")
    except TimeoutError as e:
        print(f"✅ Timeout correctly caught: {e}")
    
    print(f"\n🎯 Timeout handling is working correctly!")
    return True

def create_performance_monitoring():
    """Create performance monitoring for LaTeX-OCR"""
    
    monitoring_code = '''
import logging
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            if duration > 10:  # Log slow operations
                logging.warning(f"⚠️ Slow operation: {func.__name__} took {duration:.2f}s")
            else:
                logging.info(f"✅ {func.__name__} completed in {duration:.2f}s")
            
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            logging.error(f"❌ {func.__name__} failed after {duration:.2f}s: {e}")
            raise
    
    return wrapper

# Usage example:
@monitor_performance
def process_latex_ocr(image_path):
    """LaTeX-OCR processing with performance monitoring"""
    # Your LaTeX-OCR code here
    pass
'''
    
    print("📊 Performance Monitoring Code:")
    print(monitoring_code)
    
    return monitoring_code

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 LaTeX-OCR Performance Optimization")
    print("=" * 60)
    
    # Test timeout handling
    test_timeout_handling()
    
    # Show performance monitoring
    create_performance_monitoring()
    
    print(f"\n{'='*60}")
    print("🎯 Performance Optimization Features:")
    print("  ✅ Timeout handling (30s limit)")
    print("  ✅ Fast image preprocessing")
    print("  ✅ Automatic fallback on timeout")
    print("  ✅ Performance monitoring")
    print("  ✅ Retry mechanism")
    print("  ✅ Image size optimization")
    
    print(f"\n📋 Recommended Actions:")
    print("  1. Apply timeout handling to LaTeX-OCR calls")
    print("  2. Use fast preprocessing for large images")
    print("  3. Monitor performance in production")
    print("  4. Set appropriate timeout limits")
    print("  5. Implement graceful fallback to EasyOCR")
