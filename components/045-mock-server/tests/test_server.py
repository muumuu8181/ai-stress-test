import urllib.request
import time
import pytest
from mock_server.server import MockServer
from mock_server.models import Response

def test_server_when_fixed_response():
    with MockServer() as server:
        server.when("GET", "/test", status=201, response_body="OK", response_headers={"X-Result": "Success"})

        url = f"{server.url}/test"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 201
            assert resp.read() == b"OK"
            assert resp.headers["X-Result"] == "Success"

def test_server_on_dynamic_response():
    with MockServer() as server:
        @server.on("POST", "/data")
        def handle_post(req):
            return Response(status=202, body=f"Got {len(req.body)} bytes")

        url = f"{server.url}/data"
        req = urllib.request.Request(url, data=b"hello world", method="POST")
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 202
            assert resp.read() == b"Got 11 bytes"

def test_server_sequential_response():
    with MockServer() as server:
        server.sequential("GET", "/seq", [
            Response(status=200, body="one"),
            Response(status=200, body="two")
        ])

        url = f"{server.url}/seq"
        with urllib.request.urlopen(url) as r1:
            assert r1.read() == b"one"
        with urllib.request.urlopen(url) as r2:
            assert r2.read() == b"two"
        with urllib.request.urlopen(url) as r3:
            assert r3.read() == b"two"

def test_server_delay():
    with MockServer() as server:
        server.when("GET", "/slow", delay=0.2)

        start = time.time()
        urllib.request.urlopen(f"{server.url}/slow")
        duration = time.time() - start

        assert duration >= 0.2

def test_server_history_and_clear():
    with MockServer() as server:
        server.when("GET", "/a")
        server.when("GET", "/b")

        urllib.request.urlopen(f"{server.url}/a")
        urllib.request.urlopen(f"{server.url}/b")

        history = server.get_history()
        assert len(history) == 2
        assert history[0].path == "/a"
        assert history[1].path == "/b"

        server.clear_history()
        assert len(server.get_history()) == 0

def test_server_replay():
    with MockServer() as server:
        server.when("GET", "/target", response_body="1")

        # Initial call with query
        urllib.request.urlopen(f"{server.url}/target?q=test")
        assert len(server.get_history()) == 1

        # Replay should trigger another call with the same query
        server.replay()
        assert len(server.get_history()) == 2
        assert server.get_history()[1].path == "/target"
        assert server.get_history()[1].query == {"q": ["test"]}

def test_server_advanced_matching():
    with MockServer() as server:
        server.when("POST", "/match", match_headers={"X-Auth": "Secret"}, match_body="Login", response_body="Access Granted")
        server.when("POST", "/match", response_body="Access Denied") # Default for this path

        # Match
        req1 = urllib.request.Request(f"{server.url}/match", data=b"Login", method="POST", headers={"X-Auth": "Secret"})
        with urllib.request.urlopen(req1) as r1:
            assert r1.read() == b"Access Granted"

        # No match (wrong header)
        req2 = urllib.request.Request(f"{server.url}/match", data=b"Login", method="POST", headers={"X-Auth": "Wrong"})
        with urllib.request.urlopen(req2) as r2:
            assert r2.read() == b"Access Denied"

        # Match by query
        server.when("GET", "/search", match_query={"q": ["python"]}, response_body="Found Python")

        with urllib.request.urlopen(f"{server.url}/search?q=python") as r3:
            assert r3.read() == b"Found Python"
