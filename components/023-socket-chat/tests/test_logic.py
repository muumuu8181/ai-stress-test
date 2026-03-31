import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from logic import ChatManager, User, Room, Message

def test_register_user():
    manager = ChatManager()
    assert manager.register("alice", "password123") is True
    assert manager.register("alice", "another") is False  # Duplicate
    assert manager.register("", "pass") is False  # Empty username
    assert manager.register("bob", "") is False  # Empty password

def test_authenticate_user():
    manager = ChatManager()
    manager.register("alice", "password123")
    assert manager.authenticate("alice", "password123", 101) is True
    assert manager.authenticate("alice", "wrong", 102) is False
    assert manager.authenticate("unknown", "pass", 103) is False

def test_logout():
    manager = ChatManager()
    manager.register("alice", "password123")
    manager.authenticate("alice", "password123", 101)
    assert manager.get_user_by_socket(101).username == "alice"
    assert manager.logout(101) == "alice"
    assert manager.get_user_by_socket(101) is None

def test_room_management():
    manager = ChatManager()
    manager.register("alice", "pass")
    manager.authenticate("alice", "pass", 101)

    assert "general" in manager.list_rooms()
    manager.join_room("alice", "lobby")
    assert "lobby" in manager.list_rooms()
    assert "alice" in manager.list_users_in_room("lobby")

    manager.leave_room("alice")
    assert "alice" not in manager.list_users_in_room("lobby")
    # Lobby should be deleted since it's empty and not 'general'
    assert "lobby" not in manager.list_rooms()

def test_broadcast_to_room():
    manager = ChatManager()
    manager.register("alice", "pass")
    manager.register("bob", "pass")
    manager.authenticate("alice", "pass", 101)
    manager.authenticate("bob", "pass", 102)

    manager.join_room("alice", "general")
    manager.join_room("bob", "general")

    sockets = manager.broadcast_to_room("alice", "general", "Hello everyone!")
    assert 101 in sockets
    assert 102 in sockets

    history = manager.get_room_history("general")
    assert len(history) == 1
    assert history[0].content == "Hello everyone!"
    assert history[0].sender == "alice"

def test_private_message():
    manager = ChatManager()
    manager.register("alice", "pass")
    manager.register("bob", "pass")
    manager.authenticate("alice", "pass", 101)
    manager.authenticate("bob", "pass", 102)

    recipient_socket = manager.send_private_message("alice", "bob", "Secret message")
    assert recipient_socket == 102

    # Send to offline user
    manager.logout(102)
    assert manager.send_private_message("alice", "bob", "You there?") is None

def test_change_nickname():
    manager = ChatManager()
    manager.register("alice", "pass")
    manager.authenticate("alice", "pass", 101)
    manager.join_room("alice", "general")

    assert manager.change_nickname("alice", "alicia") is True
    assert manager.get_user_by_socket(101).username == "alicia"
    assert "alicia" in manager.list_users_in_room("general")
    assert "alice" not in manager.list_users_in_room("general")

    # Try changing to an existing name
    manager.register("bob", "pass")
    assert manager.change_nickname("alicia", "bob") is False

def test_room_history_limit():
    room = Room("test")
    for i in range(150):
        room.add_message(Message(sender="user", content=f"msg {i}"))

    assert len(room.history) == 100
    assert room.history[0].content == "msg 50"
    assert room.history[-1].content == "msg 149"
