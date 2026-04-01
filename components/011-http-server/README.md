# HTTP Server from Scratch

A multi-threaded HTTP/1.1 server built using only the Python standard library (no `http.server`).

## Features

- **HTTP/1.1 support**: GET, POST, PUT, DELETE, HEAD
- **Routing**: Path and method-based routing with support for path parameters (e.g., `/users/{id}`) and wildcards (e.g., `{filepath*}`).
- **Parsing**: Automatic parsing of headers, query parameters, and JSON bodies.
- **Middleware**: Chainable middleware system. Includes:
  - `LoggingMiddleware`: Logs request method, path, status, and processing time.
  - `CORSMiddleware`: Handles Cross-Origin Resource Sharing and preflight requests.
  - `BasicAuthMiddleware`: Simple username/password authentication.
- **Static Files**: Serve files from a directory with automatic MIME type detection and directory traversal protection.
- **Concurrency**: Multi-threaded request handling using the `threading` module.

## Installation

No external dependencies required. Only Python 3.7+ is needed.

## Usage Example

```python
from httpserver.server import HTTPServer
from httpserver.response import HTTPResponse
from httpserver.middlewares.logging import logging_middleware
from httpserver.middlewares.cors import CORSMiddleware
from httpserver.static_handler import serve_static

# Initialize server
server = HTTPServer(host="127.0.0.1", port=8080)

# Add middlewares
server.add_middleware(logging_middleware)
server.add_middleware(CORSMiddleware(allow_origins=["*"]))

# Define routes
@server.get("/hello/{name}")
def hello_handler(request):
    name = request.path_params.get("name", "World")
    return HTTPResponse.json({"message": f"Hello, {name}!"})

@server.post("/echo")
def echo_handler(request):
    try:
        data = request.json
        return HTTPResponse.json(data)
    except ValueError as e:
        return HTTPResponse(400, body=str(e))

# Serve static files from './public' at '/static/'
serve_static("./public", server.router, path_prefix="/static/")

# Start server
if __name__ == "__main__":
    server.start()
```

## API Reference

### `HTTPServer(host="0.0.0.0", port=8080)`
- `start()`: Starts the server.
- `stop()`: Stops the server.
- `add_middleware(middleware)`: Registers a middleware function.
- `get|post|put|delete|head(path)`: Decorators for registering routes.

### `HTTPRequest`
- `method`: HTTP method string.
- `path`: URL path string.
- `headers`: Dictionary of lowercase header names to values.
- `query_params`: Dictionary of query parameters.
- `path_params`: Dictionary of captured path parameters.
- `body`: Raw bytes of the request body.
- `json`: Property that parses and returns the JSON body.

### `HTTPResponse(status_code=200, headers=None, body=b"")`
- `json(data, status_code=200)`: Class method to create a JSON response.
- `html(content, status_code=200)`: Class method to create an HTML response.
- `set_header(name, value)`: Sets a response header.

## Testing

Run tests using pytest:
```bash
PYTHONPATH=src pytest tests/
```
