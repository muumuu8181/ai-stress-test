from typing import Callable, List
from .request import HTTPRequest
from .response import HTTPResponse

# A middleware is a function that takes a request and the next handler in the chain,
# and returns a response.
MiddlewareType = Callable[[HTTPRequest, Callable[[HTTPRequest], HTTPResponse]], HTTPResponse]

class MiddlewareManager:
    """
    Manages a chain of middlewares and executes them in order.
    """

    def __init__(self) -> None:
        self.middlewares: List[MiddlewareType] = []

    def add(self, middleware: MiddlewareType) -> None:
        """
        Adds a middleware to the chain.
        """
        self.middlewares.append(middleware)

    def wrap(self, handler: Callable[[HTTPRequest], HTTPResponse]) -> Callable[[HTTPRequest], HTTPResponse]:
        """
        Wraps a handler with the registered middlewares.

        Args:
            handler: The final request handler (e.g., router.resolve).

        Returns:
            A wrapped handler that executes the middleware chain.
        """
        wrapped = handler

        # We wrap from last to first so they execute in the order they were added
        for middleware in reversed(self.middlewares):
            wrapped = self._make_wrapped_handler(middleware, wrapped)

        return wrapped

    def _make_wrapped_handler(
        self,
        middleware: MiddlewareType,
        next_handler: Callable[[HTTPRequest], HTTPResponse]
    ) -> Callable[[HTTPRequest], HTTPResponse]:
        def wrapped_handler(request: HTTPRequest) -> HTTPResponse:
            return middleware(request, next_handler)
        return wrapped_handler
