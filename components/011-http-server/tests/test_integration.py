import socket
import threading
import time
import urllib.request
import urllib.error
import json
import pytest
from httpserver.server import HTTPServer
from httpserver.response import HTTPResponse

def test_server_integration():
    """
    Test the server by starting it in a separate thread and making real HTTP requests.
    """
    # Start server in a background thread
    server = HTTPServer(host="127.0.0.1", port=9000)

    @server.get("/hello")
    def hello(req):
        return HTTPResponse.json({"message": "Hello World"})

    @server.post("/echo")
    def echo(req):
        return HTTPResponse.json(req.json)

    def run_server():
        server.start()

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Give server time to start
    time.sleep(1)

    try:
        # 1. Test GET /hello
        with urllib.request.urlopen("http://127.0.0.1:9000/hello") as response:
            assert response.status == 200
            data = json.loads(response.read().decode())
            assert data["message"] == "Hello World"

        # 2. Test POST /echo
        req_data = json.dumps({"foo": "bar"}).encode('utf-8')
        req = urllib.request.Request(
            "http://127.0.0.1:9000/echo",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as response:
            assert response.status == 200
            data = json.loads(response.read().decode())
            assert data["foo"] == "bar"

        # 3. Test 404
        with pytest.raises(urllib.error.HTTPError) as excinfo:
            urllib.request.urlopen("http://127.0.0.1:9000/not-existent")
        assert excinfo.value.code == 404

    finally:
        server.stop()
        server_thread.join(timeout=2)

def test_server_concurrency():
    """
    Test that the server can handle multiple concurrent requests.
    """
    server = HTTPServer(host="127.0.0.1", port=9001)

    @server.get("/slow")
    def slow(req):
        time.sleep(0.5)
        return HTTPResponse(200, body="Slow Response")

    def run_server():
        server.start()

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    time.sleep(1)

    try:
        start_time = time.time()

        # Start multiple threads to make requests simultaneously
        def make_request():
            with urllib.request.urlopen("http://127.0.0.1:9001/slow") as response:
                assert response.read() == b"Slow Response"

        threads = [threading.Thread(target=make_request) for _ in range(3)]
        for t in threads: t.start()
        for t in threads: t.join()

        duration = time.time() - start_time
        # If requests were serial, duration would be at least 1.5s (3 * 0.5s)
        # Since they are concurrent, it should be much less than 1.5s
        assert duration < 1.0

    finally:
        server.stop()
        server_thread.join(timeout=2)
