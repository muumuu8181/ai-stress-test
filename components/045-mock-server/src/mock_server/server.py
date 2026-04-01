import threading
from http.server import HTTPServer
from typing import List, Tuple, Optional, Dict, Any, Callable, Union
from .models import Request, Response, Rule
from .handler import MockHTTPHandler
from .history import RequestHistory

class MockServer:
    """The HTTP Mock Server class managing the server thread and rules."""

    def __init__(self, host: str = "localhost", port: int = 0):
        self.host = host
        self.port = port
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._rules: List[Rule] = []
        self._history: List[Request] = []
        self._lock = threading.Lock()
        self._default_response = Response(status=404, body=b"Not Found")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @property
    def url(self) -> str:
        if self._server:
            return f"http://{self.host}:{self.port}"
        return ""

    def start(self):
        """Starts the mock server in a background thread."""
        self._server = HTTPServer((self.host, self.port), MockHTTPHandler)
        # Update port if it was randomly assigned
        self.port = self._server.server_port
        # Inject server instance back to handler access (HTTPServer uses it internally)
        self._server.record_request = self.record_request
        self._server.match_request = self.match_request

        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        """Stops the mock server."""
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread:
            self._thread.join()
            self._thread = None

    def record_request(self, request: Request):
        with self._lock:
            self._history.append(request)

    def match_request(self, request: Request) -> Tuple[Optional[Rule], Response]:
        rule = None
        with self._lock:
            for r in self._rules:
                if r.matches(request):
                    rule = r
                    break

        if rule:
            return rule, rule.get_response(request)
        return None, self._default_response

    def get_history(self) -> RequestHistory:
        with self._lock:
            return RequestHistory(list(self._history))

    def clear_history(self):
        with self._lock:
            self._history.clear()

    def clear_rules(self) -> None:
        """Clears all registered rules."""
        with self._lock:
            self._rules.clear()

    def replay(self, requests: Optional[List[Request]] = None) -> None:
        """Replays recorded requests from history or a provided list."""
        import http.client
        import urllib.parse
        if requests is None:
            with self._lock:
                requests = list(self._history)

        for req in requests:
            conn = http.client.HTTPConnection(self.host, self.port)
            # Filter headers that might cause issues when replaying
            headers = {k: v for k, v in req.headers.items() if k.lower() not in ("content-length", "host")}

            # Reconstruct the path with query parameters
            full_path = req.path
            if req.query:
                query_string = urllib.parse.urlencode(req.query, doseq=True)
                full_path = f"{full_path}?{query_string}"

            conn.request(req.method, full_path, body=req.body, headers=headers)
            conn.getresponse()
            conn.close()

    def add_rule(self, rule: Rule) -> None:
        """Adds a matching rule to the server."""
        with self._lock:
            self._rules.append(rule)

    def _create_matcher(self, method: str, path: str,
                        headers: Optional[Dict[str, str]] = None,
                        body: Optional[Union[str, bytes]] = None,
                        query: Optional[Dict[str, List[str]]] = None) -> Callable[[Request], bool]:
        """Creates a matcher function based on the provided criteria."""
        def matcher(req: Request) -> bool:
            if req.method.upper() != method.upper():
                return False
            if req.path != path:
                return False
            if headers:
                for k, v in headers.items():
                    if req.headers.get(k.lower()) != v:
                        return False
            if body is not None:
                expected_body = body.encode("utf-8") if isinstance(body, str) else body
                if req.body != expected_body:
                    return False
            if query:
                for k, v in query.items():
                    if req.query.get(k) != v:
                        return False
            return True
        return matcher

    def on(self, method: str, path: str,
           headers: Optional[Dict[str, str]] = None,
           body: Optional[Union[str, bytes]] = None,
           query: Optional[Dict[str, List[str]]] = None) -> Callable[[Callable[[Request], Response]], Callable[[Request], Response]]:
        """Decorator/helper to add a fixed or dynamic response rule."""
        def decorator(func: Callable[[Request], Response]) -> Callable[[Request], Response]:
            matcher = self._create_matcher(method, path, headers, body, query)
            self.add_rule(Rule(matcher=matcher, response_generator=func))
            return func
        return decorator

    def when(self, method: str, path: str,
             match_headers: Optional[Dict[str, str]] = None,
             match_body: Optional[Union[str, bytes]] = None,
             match_query: Optional[Dict[str, List[str]]] = None,
             status: int = 200,
             response_headers: Optional[Dict[str, str]] = None,
             response_body: Union[str, bytes] = b"",
             delay: float = 0.0) -> 'MockServer':
        """Helper to add a fixed response rule."""
        matcher = self._create_matcher(method, path, match_headers, match_body, match_query)
        response = Response(status=status, headers=response_headers or {}, body=response_body, delay=delay)
        self.add_rule(Rule(matcher=matcher, response_generator=lambda req: response))
        return self

    def sequential(self, method: str, path: str, responses: List[Response]) -> 'MockServer':
        """Helper to add a sequential response rule."""
        if not responses:
            raise ValueError("The responses list cannot be empty for a sequential rule.")

        def matcher(req: Request) -> bool:
            return req.method.upper() == method.upper() and req.path == path

        self.add_rule(Rule(matcher=matcher, response_generator=lambda req: responses[0], is_sequential=True, responses=responses))
        return self
