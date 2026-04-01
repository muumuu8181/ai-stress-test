# HTTP Mock Server

A pure Python HTTP mock server for testing, with no external dependencies (except for `pytest` in tests/fixtures).

## Features

- **Request Matching**: Match by method, path, headers, and body.
- **Fixed Responses**: Return pre-defined status, headers, and body.
- **Dynamic Responses**: Use callback functions for custom response logic.
- **Sequential Responses**: Return a sequence of different responses for repeated calls.
- **Response Delay**: Simulate network latency.
- **Request History**: Record all incoming requests for inspection.
- **Expectation Verification**: Assert that specific requests were made.
- **Request Replay**: Re-trigger recorded requests.
- **Context Manager**: Easy setup and teardown.
- **Pytest Fixture**: Seamless integration with `pytest`.

## Usage

### Basic Usage with Context Manager

```python
from mock_server.server import MockServer

with MockServer() as server:
    # Setup a rule
    server.when("GET", "/api/hello", status=200, response_body="Hello World")

    # The server is now running on a background thread
    print(f"Server running at {server.url}")

    # Make requests (using any HTTP client)
    # response = requests.get(f"{server.url}/api/hello")
```

### Advanced Matching

```python
# Match on headers and body
server.when("POST", "/auth",
            match_headers={"Content-Type": "application/json"},
            match_body='{"user": "admin"}',
            status=200, response_body='{"token": "secret"}')

# Match on query parameters
server.when("GET", "/search",
            match_query={"q": ["test"]},
            response_body="Search results for test")
```

### Dynamic Responses

```python
from mock_server.models import Response

@server.on("POST", "/echo", headers={"X-Required": "present"})
def handle_echo(request):
    return Response(status=200, body=request.body)
```

### Sequential Responses (Stateful Mock)

```python
server.sequential("GET", "/job-status", [
    Response(status=200, body="PENDING"),
    Response(status=200, body="RUNNING"),
    Response(status=200, body="COMPLETED"),
])
```

### Expectation Verification

```python
with MockServer() as server:
    server.when("POST", "/submit", status=201)

    # ... code that makes a request ...

    history = server.get_history()
    history.assert_called(count=1, method="POST", path="/submit")
    history.assert_called_with(method="POST", path="/submit", body=b"expected_data")
```

### Pytest Fixture

Add `mock_server` to your test parameters:

```python
def test_my_api(mock_server):
    mock_server.when("GET", "/health", body="OK")
    # ...
```

## Quality

- **Coverage**: >95% unit and integration test coverage.
- **Type Safety**: Fully type-hinted public API.
- **Standards**: Built on top of Python's `http.server` standard library.
