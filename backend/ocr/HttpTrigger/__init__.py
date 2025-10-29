"""
Azure Function HTTP Trigger for OCR Function App
"""

import azure.functions as func
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import Flask app
from app import app

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Main Azure Function entry point"""
    logging.info('🌐 OCR HTTP trigger function processed a request.')
    logging.info(f'   Method: {req.method}')
    logging.info(f'   URL: {req.url}')
    
    try:
        # Use WSGI middleware to handle Flask app
        return func.WsgiMiddleware(app.wsgi_app).handle(req, context)
    except Exception as e:
        logging.error(f'❌ Error handling request: {e}')
        import traceback
        logging.error(f'📋 Full traceback:\n{traceback.format_exc()}')
        raise
