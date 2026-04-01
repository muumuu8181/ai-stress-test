import socket
import threading
from typing import Optional, Callable, List
from .request import HTTPRequest
from .response import HTTPResponse
from .router import Router
from .middleware import MiddlewareManager

class HTTPServer:
    """
    Multi-threaded HTTP Server.

    Uses standard socket and threading modules to handle requests concurrently.
    Integrates with Router and MiddlewareManager.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        self.host = host
        self.port = port
        self.router = Router()
        self.middleware_manager = MiddlewareManager()
        self._running = False
        self._socket: Optional[socket.socket] = None

    def add_middleware(self, middleware: Callable) -> None:
        """
        Adds a middleware to the server's middleware chain.
        """
        self.middleware_manager.add(middleware)

    def start(self) -> None:
        """
        Starts the HTTP server.
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.host, self.port))
        self._socket.listen(5)
        self._socket.settimeout(1.0)  # Allow checking self._running periodically
        self._running = True

        print(f"Server starting on {self.host}:{self.port}...")

        # Prepare the request handler chain once
        self.handler_chain = self.middleware_manager.wrap(self.router.resolve)

        try:
            while self._running:
                try:
                    client_socket, client_address = self._socket.accept()
                except socket.timeout:
                    continue
                except OSError:
                    if not self._running:
                        break
                    raise

                # Handle each request in a new thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\nServer stopping...")
        finally:
            self.stop()

    def stop(self) -> None:
        """
        Stops the HTTP server.
        """
        self._running = False
        if self._socket:
            self._socket.close()
            self._socket = None
        print("Server stopped.")

    def _handle_client(self, client_socket: socket.socket) -> None:
        """
        Handles an individual client connection.
        """
        try:
            # Set a timeout for reading the request
            client_socket.settimeout(5.0)

            # Read the request (simple version, limited to 64KB for now)
            # For a more robust server, we should read headers first to know Content-Length
            raw_request = client_socket.recv(65536)

            if not raw_request:
                client_socket.close()
                return

            try:
                request = HTTPRequest.from_raw_data(raw_request)
                response = self.handler_chain(request)
            except ValueError as e:
                # Malformed request
                response = HTTPResponse(status_code=400, body=str(e))
            except Exception as e:
                # Server error during processing
                print(f"Internal Error: {e}")
                response = HTTPResponse(status_code=500, body="Internal Server Error")

            # Send the response back to the client
            client_socket.sendall(response.to_bytes())
        except socket.timeout:
            print("Client connection timed out.")
        except Exception as e:
            print(f"Error handling client request: {e}")
        finally:
            client_socket.close()

    # Route helpers for convenience
    def get(self, path: str):
        return self.router.get(path)

    def post(self, path: str):
        return self.router.post(path)

    def put(self, path: str):
        return self.router.put(path)

    def delete(self, path: str):
        return self.router.delete(path)

    def head(self, path: str):
        return self.router.head(path)
