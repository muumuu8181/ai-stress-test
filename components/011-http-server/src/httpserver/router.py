import re
from typing import Dict, Callable, Any, Optional, List, Tuple
from .request import HTTPRequest
from .response import HTTPResponse

HandlerType = Callable[[HTTPRequest], HTTPResponse]

class Router:
    """
    HTTP Router for mapping (method, path) to request handlers.

    Supports static paths and paths with parameters (e.g., /users/{id}).
    """

    def __init__(self) -> None:
        # Map of method -> list of (path_regex, handler)
        self.routes: Dict[str, List[Tuple[re.Pattern, HandlerType]]] = {}

    def add_route(self, method: str, path: str, handler: HandlerType) -> None:
        """
        Adds a new route.

        Args:
            method: The HTTP method (GET, POST, etc.)
            path: The URL path. Can contain parameters like {name}.
            handler: The function to handle the request.
        """
        method = method.upper()
        if method not in self.routes:
            self.routes[method] = []

        # Convert path pattern {param} to regex group
        # Special case: {param*} for matching everything until the end of the path
        pattern = re.sub(r'\{([a-zA-Z0-9_]+)\*\}', r'(?P<\1>.*)', path)
        pattern = re.sub(r'\{([a-zA-Z0-9_]+)\}', r'(?P<\1>[^/]+)', pattern)
        pattern = f'^{pattern}$'

        self.routes[method].append((re.compile(pattern), handler))

    def resolve(self, request: HTTPRequest) -> HTTPResponse:
        """
        Resolves a request to a handler and executes it.

        Args:
            request: The HTTPRequest instance.

        Returns:
            The HTTPResponse from the handler or error response.
        """
        method = request.method.upper()

        # Check if any route matches the path
        matched_handler: Optional[HandlerType] = None
        path_params: Dict[str, str] = {}

        # First, check if the method exists
        if method not in self.routes:
            # Check if path exists for other methods (405 Method Not Allowed)
            for m in self.routes:
                for pattern, _ in self.routes[m]:
                    if pattern.match(request.path):
                        return HTTPResponse(status_code=405)
            return HTTPResponse(status_code=404)

        for pattern, handler in self.routes[method]:
            match = pattern.match(request.path)
            if match:
                matched_handler = handler
                path_params = match.groupdict()
                break

        if not matched_handler:
            # Check if path exists for other methods (405 Method Not Allowed)
            for m in self.routes:
                if m == method:
                    continue
                for pattern, _ in self.routes[m]:
                    if pattern.match(request.path):
                        return HTTPResponse(status_code=405)
            return HTTPResponse(status_code=404)

        # Add path parameters to request object
        request.path_params = path_params

        try:
            return matched_handler(request)
        except Exception as e:
            print(f"Error handling request: {e}")
            return HTTPResponse(status_code=500, body=f"Internal Server Error: {e}")

    # Helper decorators
    def get(self, path: str):
        def decorator(handler: HandlerType):
            self.add_route('GET', path, handler)
            return handler
        return decorator

    def post(self, path: str):
        def decorator(handler: HandlerType):
            self.add_route('POST', path, handler)
            return handler
        return decorator

    def put(self, path: str):
        def decorator(handler: HandlerType):
            self.add_route('PUT', path, handler)
            return handler
        return decorator

    def delete(self, path: str):
        def decorator(handler: HandlerType):
            self.add_route('DELETE', path, handler)
            return handler
        return decorator

    def head(self, path: str):
        def decorator(handler: HandlerType):
            self.add_route('HEAD', path, handler)
            return handler
        return decorator
