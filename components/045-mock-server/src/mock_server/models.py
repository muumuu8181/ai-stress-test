from typing import Dict, List, Optional, Union, Callable, Any
from dataclasses import dataclass, field

@dataclass
class Request:
    """Represents an incoming HTTP request."""
    method: str
    path: str
    headers: Dict[str, str]
    body: bytes
    query: Dict[str, List[str]] = field(default_factory=dict)

@dataclass
class Response:
    """Represents an HTTP response to be returned."""
    status: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Union[str, bytes] = b""
    delay: float = 0.0

    def get_body_bytes(self) -> bytes:
        if isinstance(self.body, str):
            return self.body.encode("utf-8")
        return self.body

class Matcher:
    """Base class for request matching logic."""
    def __call__(self, request: Request) -> bool:
        raise NotImplementedError

@dataclass
class Rule:
    """Defines a matching rule and the response to return."""
    matcher: Callable[[Request], bool]
    response_generator: Callable[[Request], Response]
    is_sequential: bool = False
    responses: List[Response] = field(default_factory=list)
    _call_count: int = 0

    def matches(self, request: Request) -> bool:
        return self.matcher(request)

    def get_response(self, request: Request) -> Response:
        if self.is_sequential and self.responses:
            resp = self.responses[min(self._call_count, len(self.responses) - 1)]
            self._call_count += 1
            return resp
        return self.response_generator(request)
