import socket
import threading
import json
from typing import Dict, Any, Optional
from logic import ChatManager

class ChatServer:
    """TCP Socket Chat Server."""
    def __init__(self, host: str = '0.0.0.0', port: int = 12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.manager = ChatManager()
        self.clients: Dict[int, socket.socket] = {}  # socket_id -> socket
        self.running = False

    def start(self) -> None:
        """Starts the server."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        print(f"Server started on {self.host}:{self.port}")

        try:
            while self.running:
                client_socket, addr = self.server_socket.accept()
                socket_id = client_socket.fileno()
                self.clients[socket_id] = client_socket
                print(f"Connection from {addr}, socket_id: {socket_id}")
                threading.Thread(target=self.handle_client, args=(client_socket, socket_id), daemon=True).start()
        except Exception as e:
            if self.running:
                print(f"Server error: {e}")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stops the server."""
        self.running = False
        for client_socket in self.clients.values():
            client_socket.close()
        self.server_socket.close()
        print("Server stopped.")

    def handle_client(self, client_socket: socket.socket, socket_id: int) -> None:
        """Handles communication with a single client."""
        buffer = ""
        try:
            while self.running:
                try:
                    data = client_socket.recv(4096).decode('utf-8')
                except OSError:
                    break
                if not data:
                    break

                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if not line.strip():
                        continue
                    try:
                        message = json.loads(line)
                        response = self.process_command(socket_id, message)
                        if response:
                            self.send_to_client(socket_id, response)
                    except json.JSONDecodeError:
                        self.send_to_client(socket_id, {"status": "error", "message": "Invalid JSON format"})
        except ConnectionResetError:
            pass
        finally:
            self.cleanup_client(socket_id)

    def cleanup_client(self, socket_id: int) -> None:
        """Cleans up after a client disconnects."""
        username = self.manager.logout(socket_id)
        if username:
            print(f"User {username} disconnected.")
        if socket_id in self.clients:
            self.clients[socket_id].close()
            del self.clients[socket_id]
        print(f"Socket {socket_id} cleaned up.")

    def send_to_client(self, socket_id: int, message: Dict[str, Any]) -> None:
        """Sends a JSON message to a specific client."""
        client_socket = self.clients.get(socket_id)
        if client_socket:
            try:
                client_socket.sendall(json.dumps(message).encode('utf-8') + b'\n')
            except Exception as e:
                print(f"Error sending to client {socket_id}: {e}")

    def process_command(self, socket_id: int, command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processes a command from a client."""
        action = command.get("action")
        user = self.manager.get_user_by_socket(socket_id)

        if action == "register":
            success = self.manager.register(command.get("username"), command.get("password"))
            return {"status": "ok" if success else "error", "message": "Registration successful" if success else "Username already exists or invalid input"}

        if action == "login":
            success = self.manager.authenticate(command.get("username"), command.get("password"), socket_id)
            if success:
                # Automatically join 'general' room on login
                self.manager.join_room(command.get("username"), "general")
                return {"status": "ok", "message": f"Logged in as {command.get('username')}. Joined 'general'.", "username": command.get("username")}
            return {"status": "error", "message": "Authentication failed"}

        if not user:
            return {"status": "error", "message": "Not authenticated"}

        if action == "join":
            room_name = command.get("room")
            if self.manager.join_room(user.username, room_name):
                history = self.manager.get_room_history(room_name)
                # Convert history objects to dicts for JSON serialization
                history_dicts = [{"sender": m.sender, "content": m.content, "timestamp": m.timestamp} for m in history]
                return {"status": "ok", "message": f"Joined room {room_name}", "room": room_name, "history": history_dicts}
            return {"status": "error", "message": f"Could not join room {room_name}"}

        if action == "leave":
            room_name = self.manager.leave_room(user.username)
            if room_name:
                # Automatically join 'general' after leaving another room
                self.manager.join_room(user.username, "general")
                return {"status": "ok", "message": f"Left room {room_name}. Joined 'general'."}
            return {"status": "error", "message": "Not in a room that can be left"}

        if action == "list_rooms":
            rooms = self.manager.list_rooms()
            return {"status": "ok", "rooms": rooms}

        if action == "list_users":
            room_name = command.get("room", user.current_room)
            users = self.manager.list_users_in_room(room_name)
            return {"status": "ok", "room": room_name, "users": users}

        if action == "msg":
            content = command.get("content")
            if not content:
                return {"status": "error", "message": "Message content cannot be empty"}

            if user.current_room:
                recipient_sockets = self.manager.broadcast_to_room(user.username, user.current_room, content)
                broadcast_msg = {
                    "status": "msg",
                    "sender": user.username,
                    "room": user.current_room,
                    "content": content,
                    "timestamp": self.manager.get_room_history(user.current_room)[-1].timestamp if self.manager.get_room_history(user.current_room) else ""
                }
                for s_id in recipient_sockets:
                    if s_id != socket_id:  # Don't send back to sender
                        self.send_to_client(s_id, broadcast_msg)
                return {"status": "ok"}
            return {"status": "error", "message": "Join a room first"}

        if action == "private_msg":
            recipient_name = command.get("to")
            content = command.get("content")
            recipient_socket_id = self.manager.send_private_message(user.username, recipient_name, content)
            if recipient_socket_id:
                pm = {
                    "status": "private_msg",
                    "sender": user.username,
                    "content": content
                }
                self.send_to_client(recipient_socket_id, pm)
                return {"status": "ok", "message": f"PM sent to {recipient_name}"}
            return {"status": "error", "message": f"User {recipient_name} not found or offline"}

        if action == "nick":
            new_nick = command.get("nickname")
            if self.manager.change_nickname(user.username, new_nick):
                return {"status": "ok", "message": f"Nickname changed to {new_nick}"}
            return {"status": "error", "message": "Nickname already taken or invalid"}

        if action == "quit":
            self.cleanup_client(socket_id)
            return None

        return {"status": "error", "message": "Unknown action"}

if __name__ == "__main__":
    server = ChatServer()
    server.start()
