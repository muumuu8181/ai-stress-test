import os
import mimetypes
from .request import HTTPRequest
from .response import HTTPResponse

class StaticHandler:
    """
    Handler for serving static files from a directory.
    """

    def __init__(self, root_dir: str) -> None:
        """
        Args:
            root_dir: The directory from which to serve files.
        """
        self.root_dir = os.path.abspath(root_dir)

    def __call__(self, request: HTTPRequest) -> HTTPResponse:
        """
        Serves the requested file from the root directory.
        """
        # Get path from parameters if available, otherwise use request.path
        path = request.path_params.get('filepath', request.path)
        path = path.lstrip('/')

        file_path = os.path.abspath(os.path.join(self.root_dir, path))

        # Security check: Ensure the file is within the root directory
        if not file_path.startswith(self.root_dir):
            return HTTPResponse(status_code=403, body="Forbidden")

        if not os.path.exists(file_path):
            return HTTPResponse(status_code=404, body="File Not Found")

        if os.path.isdir(file_path):
            # Try to serve index.html if it exists
            index_path = os.path.join(file_path, 'index.html')
            if os.path.exists(index_path):
                file_path = index_path
            else:
                return HTTPResponse(status_code=404, body="Directory listing not supported")

        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            mime_type, _ = mimetypes.guess_type(file_path)
            headers = {
                'Content-Type': mime_type or 'application/octet-stream'
            }

            return HTTPResponse(status_code=200, headers=headers, body=content)
        except Exception as e:
            print(f"Error reading file: {e}")
            return HTTPResponse(status_code=500, body="Internal Server Error")

def serve_static(root_dir: str, router: 'Router', path_prefix: str = '/static/') -> None:
    """
    Helper function to register a static file handler to a router.

    Args:
        root_dir: The directory to serve files from.
        router: The Router instance.
        path_prefix: The URL prefix for static files.
    """
    handler = StaticHandler(root_dir)
    # Use {filepath*} to match all components under the prefix
    pattern = f"{path_prefix.rstrip('/')}/{{filepath*}}"
    router.add_route('GET', pattern, handler)
