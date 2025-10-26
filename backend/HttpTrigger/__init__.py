"""
Azure Functions HTTP Trigger
Forwards all HTTP requests to Flask app
"""

import logging
import azure.functions as func
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create required directories
try:
    os.makedirs(os.path.join('..', 'uploads'), exist_ok=True)
    os.makedirs(os.path.join('..', 'diagrams'), exist_ok=True)
    os.makedirs(os.path.join('..', 'textbooks'), exist_ok=True)
except Exception as e:
    logging.warning(f'Could not create directories: {e}')

# Import Flask app
try:
    from app import app as flask_app
    logging.info('✅ Flask app imported successfully')
except Exception as e:
    logging.error(f'❌ Error importing Flask app: {e}')
    import traceback
    traceback.print_exc()
    raise

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main Azure Functions HTTP trigger.
    Forwards all requests to Flask app using WSGI middleware.
    """
    logging.info(f'HTTP trigger: {req.method} {req.url}')
    
    try:
        # Use WSGI middleware to handle Flask app
        return func.WsgiMiddleware(flask_app.wsgi_app).handle(req)
    except Exception as e:
        logging.error(f'Error handling request: {e}')
        import traceback
        traceback.print_exc()
        return func.HttpResponse(
            f"Internal Server Error: {str(e)}",
            status_code=500
        )
