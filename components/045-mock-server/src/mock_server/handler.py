import time
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler
from .models import Request, Response, Rule

class MockHTTPHandler(BaseHTTPRequestHandler):
    """Handler to process HTTP requests and match them against rules."""

    def _get_request_data(self) -> Request:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        parsed_url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)

        return Request(
            method=self.command,
            path=parsed_url.path,
            headers={k.lower(): v for k, v in self.headers.items()},
            body=body,
            query=query
        )

    def do_GET(self): self._handle_request()
    def do_POST(self): self._handle_request()
    def do_PUT(self): self._handle_request()
    def do_DELETE(self): self._handle_request()
    def do_PATCH(self): self._handle_request()
    def do_HEAD(self): self._handle_request()
    def do_OPTIONS(self): self._handle_request()

    def _handle_request(self):
        req = self._get_request_data()
        self.server.record_request(req)

        rule, response = self.server.match_request(req)

        if response.delay > 0:
            time.sleep(response.delay)

        self.send_response(response.status)
        for key, value in response.headers.items():
            self.send_header(key, value)

        body_bytes = response.get_body_bytes()
        if not any(k.lower() == "content-length" for k in response.headers):
            self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()

        if self.command != "HEAD":
            self.wfile.write(body_bytes)

    def log_message(self, format, *args):
        # Silence default logging
        pass
