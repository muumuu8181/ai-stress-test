import json
from typing import Dict, Optional, Any, Union

class HTTPResponse:
    """
    Represents an HTTP response.

    Provides methods to construct an HTTP response with a status code,
    headers, and body.
    """

    # Common HTTP status codes
    STATUS_CODES = {
        200: "OK",
        201: "Created",
        204: "No Content",
        301: "Moved Permanently",
        302: "Found",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error"
    }

    def __init__(
        self,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        body: Union[bytes, str] = b""
    ) -> None:
        self.status_code = status_code
        self.headers = headers or {}
        if isinstance(body, str):
            self.body = body.encode('utf-8')
        else:
            self.body = body

        # Set default Content-Length if body exists
        if len(self.body) > 0 and 'Content-Length' not in self.headers:
            self.headers['Content-Length'] = str(len(self.body))

    @classmethod
    def json(cls, data: Any, status_code: int = 200, headers: Optional[Dict[str, str]] = None) -> 'HTTPResponse':
        """
        Creates an HTTPResponse with a JSON body.

        Args:
            data: The data to be serialized to JSON.
            status_code: The HTTP status code.
            headers: Additional headers.

        Returns:
            An HTTPResponse instance.
        """
        headers = headers or {}
        headers['Content-Type'] = 'application/json'
        body = json.dumps(data)
        return cls(status_code, headers, body)

    @classmethod
    def html(cls, content: str, status_code: int = 200, headers: Optional[Dict[str, str]] = None) -> 'HTTPResponse':
        """
        Creates an HTTPResponse with an HTML body.

        Args:
            content: The HTML content.
            status_code: The HTTP status code.
            headers: Additional headers.

        Returns:
            An HTTPResponse instance.
        """
        headers = headers or {}
        headers['Content-Type'] = 'text/html; charset=utf-8'
        return cls(status_code, headers, content)

    def to_bytes(self) -> bytes:
        """
        Converts the HTTPResponse instance into raw bytes for sending over a socket.

        Returns:
            The raw HTTP response bytes.
        """
        status_message = self.STATUS_CODES.get(self.status_code, "Unknown Status")
        response_line = f"HTTP/1.1 {self.status_code} {status_message}\r\n"

        headers_lines = []
        for key, value in self.headers.items():
            headers_lines.append(f"{key}: {value}\r\n")

        header_part = response_line + "".join(headers_lines) + "\r\n"
        return header_part.encode('utf-8') + self.body

    def set_header(self, name: str, value: str) -> None:
        """
        Sets a response header.

        Args:
            name: The header name.
            value: The header value.
        """
        self.headers[name] = value
