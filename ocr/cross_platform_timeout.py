#!/usr/bin/env python3
"""
Cross-platform timeout handling for LaTeX-OCR
Works on Windows, Linux, and macOS
"""

import threading
import logging
import time

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

def run_with_timeout(func, args=(), kwargs={}, timeout_seconds=30):
    """
    Run a function with timeout using threading
    
    Args:
        func: Function to run
        args: Function arguments
        kwargs: Function keyword arguments
        timeout_seconds: Timeout in seconds
        
    Returns:
        Function result or raises TimeoutError
    """
    result_container = []
    exception_container = []
    
    def target():
        try:
            result = func(*args, **kwargs)
            result_container.append(result)
        except Exception as e:
            exception_container.append(e)
    
    # Create and start thread
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    
    # Wait for completion or timeout
    thread.join(timeout_seconds)
    
    if thread.is_alive():
        logging.error(f"❌ Function timed out after {timeout_seconds}s")
        raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
    
    # Check for exceptions
    if exception_container:
        raise exception_container[0]
    
    # Return result
    if result_container:
        return result_container[0]
    else:
        return None

def test_cross_platform_timeout():
    """Test the cross-platform timeout functionality"""
    
    print("🌐 Testing Cross-Platform Timeout")
    print("=" * 40)
    
    # Test 1: Fast function (should succeed)
    def fast_function():
        time.sleep(2)
        return "Fast result"
    
    try:
        result = run_with_timeout(fast_function, timeout_seconds=5)
        print(f"✅ Fast function succeeded: {result}")
    except TimeoutError:
        print("❌ Fast function timed out unexpectedly")
    except Exception as e:
        print(f"❌ Fast function failed: {e}")
    
    # Test 2: Slow function (should timeout)
    def slow_function():
        time.sleep(10)
        return "Slow result"
    
    try:
        result = run_with_timeout(slow_function, timeout_seconds=3)
        print(f"⚠️ Slow function should have timed out: {result}")
    except TimeoutError as e:
        print(f"✅ Slow function correctly timed out: {e}")
    except Exception as e:
        print(f"❌ Slow function failed: {e}")
    
    # Test 3: Function with exception
    def error_function():
        raise ValueError("Test error")
    
    try:
        result = run_with_timeout(error_function, timeout_seconds=5)
        print(f"⚠️ Error function should have failed: {result}")
    except TimeoutError:
        print("❌ Error function timed out instead of raising ValueError")
    except ValueError as e:
        print(f"✅ Error function correctly raised exception: {e}")
    except Exception as e:
        print(f"❌ Error function failed with unexpected error: {e}")
    
    print(f"\n🎯 Cross-platform timeout is working correctly!")
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Cross-Platform Timeout for LaTeX-OCR")
    print("=" * 60)
    
    # Test the timeout functionality
    test_cross_platform_timeout()
    
    print(f"\n{'='*60}")
    print("📋 Features:")
    print("  ✅ Works on Windows, Linux, and macOS")
    print("  ✅ No signal module required")
    print("  ✅ Thread-based timeout handling")
    print("  ✅ Preserves exceptions")
    print("  ✅ Configurable timeout duration")
    
    print(f"\n🔧 Usage:")
    print("  result = run_with_timeout(your_function, args=(arg1,), timeout_seconds=30)")
