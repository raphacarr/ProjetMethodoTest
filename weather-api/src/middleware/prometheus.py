from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP Requests Count',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP Request Latency',
    ['method', 'endpoint']
)

REQUEST_IN_PROGRESS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint']
)

EXTERNAL_API_CALLS = Counter(
    'api_external_calls_total',
    'Total External API Calls',
    ['api_name', 'status']
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        path = request.url.path
        
        # Skip metrics endpoint to avoid recursion
        if path == "/metrics":
            return await call_next(request)
        
        REQUEST_IN_PROGRESS.labels(method=method, endpoint=path).inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Record request count and latency
            REQUEST_COUNT.labels(method=method, endpoint=path, status_code=status_code).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=path).observe(time.time() - start_time)
            
            return response
        except Exception as e:
            # Record request count for exceptions
            REQUEST_COUNT.labels(method=method, endpoint=path, status_code=500).inc()
            raise e
        finally:
            REQUEST_IN_PROGRESS.labels(method=method, endpoint=path).dec()

# Function to track external API calls
def track_external_api_call(api_name: str, success: bool = True):
    """
    Track external API calls for monitoring.
    
    Args:
        api_name: Name of the external API (e.g., 'open_meteo', 'openweather')
        success: Whether the call was successful
    """
    status = "success" if success else "failure"
    EXTERNAL_API_CALLS.labels(api_name=api_name, status=status).inc()

# Endpoint to expose metrics
async def metrics(request: Request):
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
