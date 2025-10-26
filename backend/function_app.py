import azure.functions as func
import logging
from app import app as flask_app

# Create Azure Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="HttpTrigger")
@app.route(route="{*route}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Functions HTTP trigger that forwards all requests to Flask app.
    This allows Flask routes to work in Azure Functions.
    """
    logging.info(f'Python HTTP trigger function processed a request: {req.method} {req.url}')
    
    # Use WSGI middleware to handle Flask app
    return func.WsgiMiddleware(flask_app).handle(req)
