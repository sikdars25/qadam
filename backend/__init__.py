"""
Azure Functions V1 Programming Model Entry Point
This file makes the backend folder a Python package and provides
the main entry point for Azure Functions.
"""

import azure.functions as func
from app import app as flask_app

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    Main Azure Functions entry point.
    Forwards all HTTP requests to Flask app using WSGI.
    """
    return func.WsgiMiddleware(flask_app.wsgi_app).handle(req, context)
