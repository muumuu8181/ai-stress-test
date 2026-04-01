from typing import Callable, List, Optional
from ..request import HTTPRequest
from ..response import HTTPResponse

class CORSMiddleware:
    """
    Middleware for handling Cross-Origin Resource Sharing (CORS).
    """

    def __init__(
        self,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None
    ) -> None:
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
        self.allow_headers = allow_headers or ["Content-Type", "Authorization"]

    def __call__(self, request: HTTPRequest, next_handler: Callable[[HTTPRequest], HTTPResponse]) -> HTTPResponse:
        """
        Processes the request and adds CORS headers to the response.
        Handles preflight OPTIONS requests.
        """
        # Handle preflight request
        if request.method == "OPTIONS":
            response = HTTPResponse(status_code=204)
            self._add_cors_headers(response)
            return response

        # Call the next handler
        response = next_handler(request)

        # Add CORS headers to the response
        self._add_cors_headers(response)

        return response

    def _add_cors_headers(self, response: HTTPResponse) -> None:
        """
        Adds CORS-related headers to an HTTPResponse object.
        """
        response.set_header("Access-Control-Allow-Origin", ", ".join(self.allow_origins))
        response.set_header("Access-Control-Allow-Methods", ", ".join(self.allow_methods))
        response.set_header("Access-Control-Allow-Headers", ", ".join(self.allow_headers))
