from typing import List, Optional, Dict, Any, Callable, Union
from .models import Request

class RequestHistory:
    """Helper class to interact with request history."""

    def __init__(self, history: List[Request]):
        self._history = history

    def __len__(self):
        return len(self._history)

    def __getitem__(self, index):
        return self._history[index]

    def find(self, method: Optional[str] = None, path: Optional[str] = None, query: Optional[Dict[str, List[str]]] = None) -> List[Request]:
        """Finds requests in history matching criteria."""
        results = []
        for req in self._history:
            if method and req.method.upper() != method.upper():
                continue
            if path and req.path != path:
                continue
            if query:
                match = True
                for k, v in query.items():
                    if req.query.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
            results.append(req)
        return results

    def last(self) -> Optional[Request]:
        """Returns the most recent request."""
        return self._history[-1] if self._history else None

    def assert_called(self, count: Optional[int] = None, method: Optional[str] = None, path: Optional[str] = None):
        """Asserts that a certain number of requests were made."""
        matches = self.find(method, path)
        if count is not None:
            if len(matches) != count:
                raise AssertionError(f"Expected {count} calls, but got {len(matches)}.")
        elif len(matches) == 0:
            raise AssertionError(f"Expected at least one call, but got none.")

    def assert_called_with(self, method: str, path: str, body: Optional[Union[str, bytes]] = None, headers: Optional[Dict[str, str]] = None, query: Optional[Dict[str, List[str]]] = None):
        """Asserts that at least one request matches specific criteria."""
        matches = self.find(method, path, query)
        expected_body = body.encode("utf-8") if isinstance(body, str) else body

        for req in matches:
            body_match = expected_body is None or req.body == expected_body
            header_match = True
            if headers:
                for k, v in headers.items():
                    if req.headers.get(k.lower()) != v:
                        header_match = False
                        break
            if body_match and header_match:
                return
        raise AssertionError(f"No request found matching {method} {path} with specified body/headers/query.")
