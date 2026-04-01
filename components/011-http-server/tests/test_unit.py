import pytest
import json
from httpserver.request import HTTPRequest
from httpserver.response import HTTPResponse
from httpserver.router import Router
from httpserver.middleware import MiddlewareManager
from httpserver.middlewares.logging import logging_middleware
from httpserver.middlewares.cors import CORSMiddleware
from httpserver.middlewares.auth import BasicAuthMiddleware
from httpserver.static_handler import StaticHandler
import os

# --- Request Tests ---

def test_request_parsing():
    raw = b"GET /path?a=1&b=2 HTTP/1.1\r\nHost: localhost\r\n\r\n"
    req = HTTPRequest.from_raw_data(raw)
    assert req.method == "GET"
    assert req.path == "/path"
    assert req.query_params == {"a": "1", "b": "2"}
    assert req.headers["host"] == "localhost"

def test_request_json_parsing():
    body = json.dumps({"key": "value"}).encode('utf-8')
    raw = b"POST /api HTTP/1.1\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body
    req = HTTPRequest.from_raw_data(raw)
    assert req.json == {"key": "value"}

def test_request_invalid_parsing():
    with pytest.raises(ValueError):
        HTTPRequest.from_raw_data(b"INVALID")

# --- Response Tests ---

def test_response_to_bytes():
    res = HTTPResponse(200, {"X-Test": "Value"}, "Hello")
    raw = res.to_bytes()
    assert b"HTTP/1.1 200 OK" in raw
    assert b"X-Test: Value" in raw
    assert b"Content-Length: 5" in raw
    assert raw.endswith(b"\r\n\r\nHello")

def test_response_json_helper():
    res = HTTPResponse.json({"status": "ok"})
    assert res.headers["Content-Type"] == "application/json"
    assert res.body == b'{"status": "ok"}'

# --- Router Tests ---

def test_router_resolve():
    router = Router()
    @router.get("/hello/{name}")
    def hello(req):
        return HTTPResponse(200, body=f"Hello {req.path_params['name']}")

    req = HTTPRequest("GET", "/hello/world", {}, b"", {})
    res = router.resolve(req)
    assert res.status_code == 200
    assert res.body == b"Hello world"

def test_router_404():
    router = Router()
    req = HTTPRequest("GET", "/notfound", {}, b"", {})
    res = router.resolve(req)
    assert res.status_code == 404

def test_router_405():
    router = Router()
    @router.post("/api")
    def api(req): return HTTPResponse(200)

    req = HTTPRequest("GET", "/api", {}, b"", {})
    res = router.resolve(req)
    assert res.status_code == 405

def test_router_methods_decorators():
    router = Router()
    @router.put("/put")
    def handle_put(req): return HTTPResponse(200)
    @router.delete("/delete")
    def handle_delete(req): return HTTPResponse(200)
    @router.head("/head")
    def handle_head(req): return HTTPResponse(200)

    assert router.resolve(HTTPRequest("PUT", "/put", {}, b"", {})).status_code == 200
    assert router.resolve(HTTPRequest("DELETE", "/delete", {}, b"", {})).status_code == 200
    assert router.resolve(HTTPRequest("HEAD", "/head", {}, b"", {})).status_code == 200

# --- Middleware Tests ---

def test_middleware_manager():
    manager = MiddlewareManager()
    calls = []

    def mid1(req, next_handler):
        calls.append(1)
        return next_handler(req)

    def mid2(req, next_handler):
        calls.append(2)
        return next_handler(req)

    manager.add(mid1)
    manager.add(mid2)

    handler = manager.wrap(lambda req: HTTPResponse(200, body="Done"))
    res = handler(HTTPRequest("GET", "/", {}, b"", {}))

    assert calls == [1, 2]
    assert res.body == b"Done"

# --- Specific Middleware Tests ---

def test_cors_middleware():
    cors = CORSMiddleware(allow_origins=["example.com"])
    def handler(req): return HTTPResponse(200)

    # Preflight
    req_options = HTTPRequest("OPTIONS", "/", {}, b"", {})
    res_options = cors(req_options, handler)
    assert res_options.status_code == 204
    assert res_options.headers["Access-Control-Allow-Origin"] == "example.com"

    # Normal request
    req_get = HTTPRequest("GET", "/", {}, b"", {})
    res_get = cors(req_get, handler)
    assert res_get.headers["Access-Control-Allow-Origin"] == "example.com"

def test_logging_middleware(capsys):
    def handler(req): return HTTPResponse(200)
    req = HTTPRequest("GET", "/log", {}, b"", {})
    logging_middleware(req, handler)
    captured = capsys.readouterr()
    assert "[GET] /log - 200" in captured.out

def test_auth_middleware():
    auth = BasicAuthMiddleware({"admin": "password"})
    def handler(req): return HTTPResponse(200, body="Secret")

    # No auth
    req_no_auth = HTTPRequest("GET", "/", {}, b"", {})
    res_no_auth = auth(req_no_auth, handler)
    assert res_no_auth.status_code == 401

    # Correct auth
    import base64
    creds = base64.b64encode(b"admin:password").decode()
    req_auth = HTTPRequest("GET", "/", {"authorization": f"Basic {creds}"}, b"", {})
    res_auth = auth(req_auth, handler)
    assert res_auth.status_code == 200
    assert res_auth.body == b"Secret"

# --- Static Handler Tests ---

def test_static_handler(tmp_path):
    d = tmp_path / "static"
    d.mkdir()
    f = d / "test.txt"
    f.write_text("static content")

    handler = StaticHandler(str(d))

    # Normal file
    req = HTTPRequest("GET", "/test.txt", {}, b"", {})
    req.path_params = {"filepath": "test.txt"}
    res = handler(req)
    assert res.status_code == 200
    assert res.body == b"static content"
    assert res.headers["Content-Type"] == "text/plain"

    # Directory traversal attempt
    req_evil = HTTPRequest("GET", "/../test.txt", {}, b"", {})
    req_evil.path_params = {"filepath": "../test.txt"}
    res_evil = handler(req_evil)
    assert res_evil.status_code == 403

    # File not found
    req_404 = HTTPRequest("GET", "/none", {}, b"", {})
    req_404.path_params = {"filepath": "none"}
    assert handler(req_404).status_code == 404

    # Index.html
    (d / "index.html").write_text("index")
    req_idx = HTTPRequest("GET", "/", {}, b"", {})
    req_idx.path_params = {"filepath": ""}
    assert handler(req_idx).body == b"index"
