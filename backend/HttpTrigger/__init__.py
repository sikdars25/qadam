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

from app import app as flask_app

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main Azure Functions HTTP trigger.
    Forwards all requests to Flask app using WSGI middleware.
    """
    logging.info(f'HTTP trigger: {req.method} {req.url}')
    
    # Use WSGI middleware to handle Flask app
    return func.WsgiMiddleware(flask_app.wsgi_app).handle(req)
