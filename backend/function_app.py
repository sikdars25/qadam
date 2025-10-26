import azure.functions as func
import logging

# Import Flask app
from app import app as flask_app

# Create Azure Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="{*route}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Functions HTTP trigger that forwards all requests to Flask app.
    Catches all routes and forwards to Flask using WSGI middleware.
    """
    logging.info(f'HTTP trigger: {req.method} {req.url}')
    
    # Use WSGI middleware to handle Flask app
    return func.WsgiMiddleware(flask_app.wsgi_app).handle(req)
