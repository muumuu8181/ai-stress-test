import time
from typing import Callable
from ..request import HTTPRequest
from ..response import HTTPResponse

def logging_middleware(request: HTTPRequest, next_handler: Callable[[HTTPRequest], HTTPResponse]) -> HTTPResponse:
    """
    Middleware for logging HTTP requests.
    """
    start_time = time.time()
    response = next_handler(request)
    duration = (time.time() - start_time) * 1000

    print(f"[{request.method}] {request.path} - {response.status_code} ({duration:.2f}ms)")

    return response
