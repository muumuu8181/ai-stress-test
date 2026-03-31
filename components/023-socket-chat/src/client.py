import socket
import threading
import json
import sys
from typing import Optional

class ChatClient:
    """REPL-based TCP Chat Client."""
    def __init__(self, host: str = '127.0.0.1', port: int = 12345):
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
        self.running = False
        self.username: Optional[str] = None

    def connect(self) -> bool:
        """Connects to the chat server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.running = True
            threading.Thread(target=self.receive_messages, daemon=True).start()
            return True
        except Exception as e:
            print(f"Could not connect to server: {e}")
            return False

    def receive_messages(self) -> None:
        """Continuously receives messages from the server."""
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(4096).decode('utf-8')
                if not data:
                    print("\nDisconnected from server.")
                    self.running = False
                    break

                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        self.handle_server_message(json.loads(line))
            except Exception as e:
                if self.running:
                    print(f"\nError receiving: {e}")
                self.running = False
                break

    def handle_server_message(self, message: dict) -> None:
        """Handles and displays messages from the server."""
        status = message.get("status")
        if status == "msg":
            print(f"\n[{message.get('room')}] {message.get('sender')}: {message.get('content')}")
        elif status == "private_msg":
            print(f"\n[PM] {message.get('sender')}: {message.get('content')}")
        elif status == "ok":
            if "message" in message:
                print(f"\nServer: {message.get('message')}")
            if "rooms" in message:
                print(f"\nAvailable rooms: {', '.join(message.get('rooms'))}")
            if "users" in message:
                print(f"\nUsers in {message.get('room')}: {', '.join(message.get('users'))}")
            if "history" in message:
                print("\n--- Room History ---")
                for msg in message.get("history"):
                    print(f"[{msg['timestamp']}] {msg['sender']}: {msg['content']}")
                print("--------------------")
        elif status == "error":
            print(f"\nError: {message.get('message')}")

        print("> ", end="", flush=True)

    def send_command(self, action: str, **kwargs) -> None:
        """Sends a JSON command to the server."""
        if not self.sock:
            return
        command = {"action": action, **kwargs}
        self.sock.sendall((json.dumps(command) + '\n').encode('utf-8'))

    def run(self) -> None:
        """Main REPL loop."""
        if not self.connect():
            return

        print("Connected to Chat Server.")
        print("Commands: /register <u/p>, /login <u/p>, /join <room>, /leave, /list, /users <room>, /msg <content>, /pm <user> <content>, /nick <name>, /quit")

        try:
            while self.running:
                user_input = input("> ").strip()
                if not user_input:
                    continue

                if user_input.startswith("/"):
                    parts = user_input.split(" ", 1)
                    cmd = parts[0][1:]
                    args = parts[1] if len(parts) > 1 else ""

                    if cmd == "register":
                        u_p = args.split(" ")
                        if len(u_p) == 2:
                            self.send_command("register", username=u_p[0], password=u_p[1])
                        else:
                            print("Usage: /register <username> <password>")
                    elif cmd == "login":
                        u_p = args.split(" ")
                        if len(u_p) == 2:
                            self.send_command("login", username=u_p[0], password=u_p[1])
                            self.username = u_p[0]
                        else:
                            print("Usage: /login <username> <password>")
                    elif cmd == "join":
                        if args:
                            self.send_command("join", room=args)
                        else:
                            print("Usage: /join <room_name>")
                    elif cmd == "leave":
                        self.send_command("leave")
                    elif cmd == "list":
                        self.send_command("list_rooms")
                    elif cmd == "users":
                        self.send_command("list_users", room=args if args else None)
                    elif cmd == "msg":
                        if args:
                            self.send_command("msg", content=args)
                        else:
                            print("Usage: /msg <content>")
                    elif cmd == "pm":
                        u_c = args.split(" ", 1)
                        if len(u_c) == 2:
                            self.send_command("private_msg", to=u_c[0], content=u_c[1])
                        else:
                            print("Usage: /pm <username> <content>")
                    elif cmd == "nick":
                        if args:
                            self.send_command("nick", nickname=args)
                        else:
                            print("Usage: /nick <new_nickname>")
                    elif cmd == "quit":
                        self.send_command("quit")
                        self.running = False
                        break
                    else:
                        print(f"Unknown command: /{cmd}")
                else:
                    # Default behavior for non-command input is to send as a message if logged in
                    if self.username:
                        self.send_command("msg", content=user_input)
                    else:
                        print("Please login first or use /commands.")
        except KeyboardInterrupt:
            self.send_command("quit")
            self.running = False
        finally:
            if self.sock:
                self.sock.close()
            print("Goodbye!")

if __name__ == "__main__":
    client = ChatClient()
    client.run()
