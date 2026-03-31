import socket
import threading
import json
import time
import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from server import ChatServer

@pytest.fixture(scope="module")
def chat_server():
    server = ChatServer(host='127.0.0.1', port=0)  # Port 0 lets OS pick an available port
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    time.sleep(0.5)  # Let server start
    yield server
    server.stop()

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

class ClientMock:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.buffer = ""

    def send(self, action, **kwargs):
        cmd = {"action": action, **kwargs}
        self.sock.sendall((json.dumps(cmd) + '\n').encode('utf-8'))

    def receive(self, timeout=2):
        self.sock.settimeout(timeout)
        try:
            while '\n' not in self.buffer:
                data = self.sock.recv(4096).decode('utf-8')
                if not data:
                    return None
                self.buffer += data

            line, self.buffer = self.buffer.split('\n', 1)
            return json.loads(line)
        except socket.timeout:
            return None

    def close(self):
        self.sock.close()

def test_full_integration(chat_server):
    port = chat_server.server_socket.getsockname()[1]

    # Alice registers and logs in
    alice = ClientMock('127.0.0.1', port)
    alice.send("register", username="alice", password="abc")
    assert alice.receive()["status"] == "ok"

    alice.send("login", username="alice", password="abc")
    res = alice.receive()
    assert res["status"] == "ok"
    assert "Joined 'general'" in res["message"]

    # Bob registers and logs in
    bob = ClientMock('127.0.0.1', port)
    bob.send("register", username="bob", password="123")
    assert bob.receive()["status"] == "ok"

    bob.send("login", username="bob", password="123")
    assert bob.receive()["status"] == "ok"

    # Alice sends a message in general, Bob should receive it
    alice.send("msg", content="Hello Bob!")
    assert alice.receive()["status"] == "ok"

    received_by_bob = bob.receive()
    assert received_by_bob["status"] == "msg"
    assert received_by_bob["sender"] == "alice"
    assert received_by_bob["content"] == "Hello Bob!"

    # Alice creates and joins a private room
    alice.send("join", room="secret_room")
    res = alice.receive()
    assert res["status"] == "ok"
    assert res["room"] == "secret_room"

    # Alice sends a message in secret_room, Bob should NOT receive it
    alice.send("msg", content="Hidden message")
    alice.receive() # ok response
    assert bob.receive(timeout=0.1) is None

    # Bob joins secret_room
    bob.send("join", room="secret_room")
    res = bob.receive()
    assert res["status"] == "ok"
    # History check
    assert len(res["history"]) == 1
    assert res["history"][0]["content"] == "Hidden message"

    # Private message
    alice.send("private_msg", to="bob", content="PM test")
    assert alice.receive()["status"] == "ok"
    pm = bob.receive()
    assert pm["status"] == "private_msg"
    assert pm["sender"] == "alice"
    assert pm["content"] == "PM test"

    # Logout cleanup
    alice.send("quit")
    time.sleep(0.1)

    # Check if Bob can still see Alice in room list
    bob.send("list_users", room="secret_room")
    res = bob.receive()
    assert "alice" not in res["users"]

    alice.close()
    bob.close()

def test_edge_cases(chat_server):
    port = chat_server.server_socket.getsockname()[1]
    client = ClientMock('127.0.0.1', port)

    # Not logged in
    client.send("msg", content="who am i?")
    res = client.receive()
    assert res["status"] == "error"
    assert "Not authenticated" in res["message"]

    # Invalid JSON
    client.sock.sendall(b"not a json\n")
    res = client.receive()
    assert res["status"] == "error"
    assert "Invalid JSON format" in res["message"]

    client.close()
