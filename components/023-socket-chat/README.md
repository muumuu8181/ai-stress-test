# TCP Socket Chat Server

A multi-client TCP socket chat server implemented in Python using only the standard library.

## Features

- **Multi-client support**: Handles multiple simultaneous connections using threading.
- **Chat Rooms**: Users can create, join, and leave rooms. Rooms are automatically deleted when empty (except for 'general').
- **Private Messages**: Users can send direct messages to each other.
- **Authentication**: Simple username/password registration and login.
- **Message History**: Joining a room provides the last 100 messages of history.
- **Commands**: Support for common chat commands (e.g., `/join`, `/msg`, `/nick`).

## Installation

No external dependencies required (other than `pytest` and `pytest-cov` for testing).

## Usage

### Starting the Server

```bash
python3 components/023-socket-chat/src/server.py
```

### Running the Client

```bash
python3 components/023-socket-chat/src/client.py
```

### Client Commands

- `/register <username> <password>`: Register a new account.
- `/login <username> <password>`: Log in to your account.
- `/join <room_name>`: Join a specific chat room.
- `/leave`: Leave the current room and return to 'general'.
- `/list`: List all active chat rooms.
- `/users [room_name]`: List users in the specified room (or current room).
- `/msg <content>`: Send a message to the current room.
- `/pm <username> <content>`: Send a private message to a user.
- `/nick <new_nickname>`: Change your username.
- `/quit`: Disconnect from the server.

*Note: Any text entered without a '/' prefix will be treated as a `/msg` if you are logged in.*

## Project Structure

- `src/logic.py`: Core business logic (User, Room, ChatManager).
- `src/server.py`: TCP server implementation.
- `src/client.py`: REPL-based CLI client.
- `tests/test_logic.py`: Unit tests for core logic.
- `tests/test_integration.py`: Integration tests for server-client interaction.

## Testing

To run the tests and check coverage:

```bash
python3 -m pytest --cov=components/023-socket-chat/src components/023-socket-chat/tests/
```
