from typing import Dict, List, Optional, Set
import json
from dataclasses import dataclass, field
import datetime

@dataclass
class User:
    """Represents a user in the chat system."""
    username: str
    password: str
    current_room: Optional[str] = None
    socket_id: Optional[int] = None  # To track which socket belongs to which user

@dataclass
class Message:
    """Represents a message in the chat system."""
    sender: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    recipient: Optional[str] = None  # None for broadcast/room messages

class Room:
    """Manages users and messages within a chat room."""
    def __init__(self, name: str):
        self.name: str = name
        self.users: Set[str] = set()
        self.history: List[Message] = []

    def add_user(self, username: str) -> None:
        """Adds a user to the room."""
        self.users.add(username)

    def remove_user(self, username: str) -> None:
        """Removes a user from the room."""
        if username in self.users:
            self.users.remove(username)

    def add_message(self, message: Message) -> None:
        """Adds a message to the room's history."""
        self.history.append(message)
        # Limit history to last 100 messages
        if len(self.history) > 100:
            self.history.pop(0)

    def is_empty(self) -> bool:
        """Checks if the room is empty."""
        return len(self.users) == 0

class ChatManager:
    """Main logic for handling users, rooms, and messages."""
    def __init__(self):
        self.users: Dict[str, User] = {}  # username -> User
        self.rooms: Dict[str, Room] = {"general": Room("general")}
        self.online_users: Dict[int, str] = {}  # socket_id -> username

    def register(self, username: str, password: str) -> bool:
        """Registers a new user."""
        if not username or not password:
            return False
        if username in self.users:
            return False
        self.users[username] = User(username=username, password=password)
        return True

    def authenticate(self, username: str, password: str, socket_id: int) -> bool:
        """Authenticates a user and marks them as online."""
        user = self.users.get(username)
        if user and user.password == password:
            self.online_users[socket_id] = username
            user.socket_id = socket_id
            return True
        return False

    def logout(self, socket_id: int) -> Optional[str]:
        """Logs out a user and returns their username."""
        username = self.online_users.pop(socket_id, None)
        if username:
            user = self.users.get(username)
            if user:
                if user.current_room:
                    self.leave_room(username)
                user.socket_id = None
        return username

    def get_user_by_socket(self, socket_id: int) -> Optional[User]:
        """Returns the User object associated with a socket ID."""
        username = self.online_users.get(socket_id)
        if username:
            return self.users.get(username)
        return None

    def join_room(self, username: str, room_name: str) -> bool:
        """Moves a user to a room."""
        user = self.users.get(username)
        if not user:
            return False

        if user.current_room:
            self.leave_room(username)

        if room_name not in self.rooms:
            self.rooms[room_name] = Room(room_name)

        self.rooms[room_name].add_user(username)
        user.current_room = room_name
        return True

    def leave_room(self, username: str) -> Optional[str]:
        """Removes a user from their current room."""
        user = self.users.get(username)
        if not user or not user.current_room:
            return None

        room_name = user.current_room
        room = self.rooms.get(room_name)
        if room:
            room.remove_user(username)
            if room.is_empty() and room_name != "general":
                del self.rooms[room_name]

        user.current_room = None
        return room_name

    def list_rooms(self) -> List[str]:
        """Lists all available rooms."""
        return list(self.rooms.keys())

    def list_users_in_room(self, room_name: str) -> List[str]:
        """Lists all users in a specific room."""
        room = self.rooms.get(room_name)
        if room:
            return list(room.users)
        return []

    def change_nickname(self, old_username: str, new_username: str) -> bool:
        """Changes a user's nickname."""
        if not new_username or new_username in self.users:
            return False

        user = self.users.pop(old_username, None)
        if not user:
            return False

        user.username = new_username
        self.users[new_username] = user

        # Update online_users
        if user.socket_id is not None:
            self.online_users[user.socket_id] = new_username

        # Update rooms
        if user.current_room:
            room = self.rooms.get(user.current_room)
            if room:
                room.remove_user(old_username)
                room.add_user(new_username)

        return True

    def get_room_history(self, room_name: str) -> List[Message]:
        """Returns the message history for a room."""
        room = self.rooms.get(room_name)
        if room:
            return room.history
        return []

    def broadcast_to_room(self, sender: str, room_name: str, content: str) -> List[int]:
        """Sends a message to all users in a room and returns their socket IDs."""
        room = self.rooms.get(room_name)
        if not room or sender not in room.users:
            return []

        msg = Message(sender=sender, content=content)
        room.add_message(msg)

        recipient_sockets = []
        for username in room.users:
            user = self.users.get(username)
            if user and user.socket_id is not None:
                recipient_sockets.append(user.socket_id)
        return recipient_sockets

    def send_private_message(self, sender: str, recipient_name: str, content: str) -> Optional[int]:
        """Sends a private message to a user and returns their socket ID."""
        recipient = self.users.get(recipient_name)
        if recipient and recipient.socket_id is not None:
            # We don't store PMs in room history
            return recipient.socket_id
        return None
