"""
Azure Functions HTTP Trigger
Forwards all HTTP requests to Flask app
"""

import logging
import azure.functions as func
import sys
import os
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to import app
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
logger.info(f'📁 Added to path: {parent_dir}')
logger.info(f'📁 Current directory: {os.getcwd()}')
logger.info(f'📁 __file__ location: {__file__}')

# Create required directories
try:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    for folder in ['uploads', 'diagrams', 'textbooks']:
        folder_path = os.path.join(base_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        logger.info(f'✅ Created directory: {folder_path}')
except Exception as e:
    logger.warning(f'⚠️ Could not create directories: {e}')

# Import Flask app with detailed error handling
flask_app = None
import_error = None

try:
    logger.info('🔄 Attempting to import Flask app...')
    from app import app as flask_app
    logger.info('✅ Flask app imported successfully!')
except Exception as e:
    import_error = e
    error_details = traceback.format_exc()
    logger.error(f'❌ CRITICAL: Error importing Flask app: {e}')
    logger.error(f'📋 Full traceback:\n{error_details}')
    logger.error(f'📁 sys.path: {sys.path}')
    logger.error(f'📁 Files in parent dir: {os.listdir(parent_dir) if os.path.exists(parent_dir) else "DIR NOT FOUND"}')

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main Azure Functions HTTP trigger.
    Forwards all requests to Flask app using WSGI middleware.
    """
    logger.info(f'🌐 HTTP trigger: {req.method} {req.url}')
    
    # If Flask app failed to import, return detailed error
    if flask_app is None:
        error_msg = f"""
❌ Flask App Import Failed

Error: {str(import_error)}

Traceback:
{traceback.format_exception(type(import_error), import_error, import_error.__traceback__) if import_error else 'No traceback available'}

System Info:
- Current directory: {os.getcwd()}
- Parent directory: {parent_dir}
- sys.path: {sys.path}
- Files in parent: {os.listdir(parent_dir) if os.path.exists(parent_dir) else 'DIR NOT FOUND'}

Request Info:
- Method: {req.method}
- URL: {req.url}
- Route: {req.route_params}
"""
        logger.error(error_msg)
        return func.HttpResponse(
            error_msg,
            status_code=500,
            mimetype="text/plain"
        )
    
    try:
        # Use WSGI middleware to handle Flask app
        logger.info('✅ Forwarding request to Flask app via WSGI')
        return func.WsgiMiddleware(flask_app.wsgi_app).handle(req)
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f'❌ Error handling request: {e}')
        logger.error(f'📋 Full traceback:\n{error_details}')
        return func.HttpResponse(
            f"Internal Server Error:\n\n{str(e)}\n\nTraceback:\n{error_details}",
            status_code=500,
            mimetype="text/plain"
        )
