import json
from typing import Dict, Optional, Any
from urllib.parse import urlparse, parse_qs

class HTTPRequest:
    """
    Represents an HTTP request.

    Parses raw bytes from a socket and provides access to method, path, headers,
    query parameters, and body.
    """

    def __init__(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: bytes,
        query_params: Dict[str, Any]
    ) -> None:
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.query_params = query_params
        self.path_params: Dict[str, str] = {}
        self._json_body: Optional[Any] = None

    @classmethod
    def from_raw_data(cls, raw_data: bytes) -> 'HTTPRequest':
        """
        Parses raw HTTP request bytes into an HTTPRequest object.

        Args:
            raw_data: The raw bytes received from the socket.

        Returns:
            An HTTPRequest instance.
        """
        if not raw_data:
            raise ValueError("Empty request data")

        try:
            # Split headers and body
            header_part, _, body = raw_data.partition(b'\r\n\r\n')
            lines = header_part.decode('utf-8').split('\r\n')

            if not lines:
                raise ValueError("Invalid request line")

            # Parse request line
            request_line = lines[0].split(' ')
            if len(request_line) < 3:
                raise ValueError(f"Malformed request line: {lines[0]}")

            method = request_line[0]
            full_path = request_line[1]

            # Parse URL and query parameters
            parsed_url = urlparse(full_path)
            path = parsed_url.path
            query_params = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed_url.query).items()}

            # Parse headers
            headers = {}
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()

            return cls(method, path, headers, body, query_params)
        except Exception as e:
            raise ValueError(f"Failed to parse request: {e}")

    @property
    def json(self) -> Any:
        """
        Parses the request body as JSON and returns it.

        Returns:
            The parsed JSON data.

        Raises:
            ValueError: If the body is not valid JSON or Content-Type is not application/json.
        """
        if self._json_body is not None:
            return self._json_body

        content_type = self.headers.get('content-type', '')
        if 'application/json' not in content_type:
            raise ValueError("Content-Type is not application/json")

        try:
            self._json_body = json.loads(self.body.decode('utf-8'))
            return self._json_body
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse JSON body: {e}")

    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Gets the value of a header by name (case-insensitive).

        Args:
            name: The header name.
            default: The default value if the header is not found.

        Returns:
            The header value or the default.
        """
        return self.headers.get(name.lower(), default)
