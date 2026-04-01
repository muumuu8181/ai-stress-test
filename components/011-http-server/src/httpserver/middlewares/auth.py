import base64
from typing import Callable, Dict, Optional
from ..request import HTTPRequest
from ..response import HTTPResponse

class BasicAuthMiddleware:
    """
    Middleware for handling Basic Authentication.
    """

    def __init__(self, credentials: Dict[str, str], realm: str = "Restricted Area") -> None:
        """
        Args:
            credentials: A dictionary mapping usernames to passwords.
            realm: The authentication realm.
        """
        self.credentials = credentials
        self.realm = realm

    def __call__(self, request: HTTPRequest, next_handler: Callable[[HTTPRequest], HTTPResponse]) -> HTTPResponse:
        """
        Authenticates the request using Basic Auth.
        """
        auth_header = request.get_header("Authorization")

        if not auth_header:
            return self._unauthorized_response()

        try:
            # Basic Authentication: "Basic <base64(username:password)>"
            auth_type, encoded_creds = auth_header.split(" ", 1)

            if auth_type.lower() != "basic":
                return self._unauthorized_response()

            decoded_creds = base64.b64decode(encoded_creds).decode("utf-8")
            username, password = decoded_creds.split(":", 1)

            if username in self.credentials and self.credentials[username] == password:
                return next_handler(request)

            return self._unauthorized_response()

        except (ValueError, UnicodeDecodeError, base64.binascii.Error) as e:
            print(f"Authentication error: {e}")
            return self._unauthorized_response()

    def _unauthorized_response(self) -> HTTPResponse:
        """
        Returns a 401 Unauthorized response with the appropriate WWW-Authenticate header.
        """
        response = HTTPResponse(status_code=401, body="Unauthorized")
        response.set_header("WWW-Authenticate", f'Basic realm="{self.realm}"')
        return response
