# EventEmitter with Wildcards

A pure Python implementation of a Node.js-style EventEmitter with support for namespaces and wildcards.

## Features

- **Wildcards**: Listen to events using `*` (single segment) and `**` (recursive).
- **Namespaces**: Use dot notation for event names (e.g., `user.login`).
- **Sync/Async**: Support for both synchronous `emit()` and asynchronous `emit_async()`.
- **Once**: Register listeners that only run once.
- **Max Listeners**: Set a limit on the number of listeners per event.
- **Error Handling**: Catch exceptions in listeners and emit an `error` event.
- **Event History**: Track recently emitted events.

## Usage

### Basic Usage

```python
from event_emitter.emitter import EventEmitter

emitter = EventEmitter()

def on_user_login(user_id):
    print(f"User {user_id} logged in")

emitter.on('user.login', on_user_login)
emitter.emit('user.login', 123)
```

### Wildcards

```python
# Match single segment
emitter.on('user.*', lambda data: print(f"User event: {data}"))
emitter.emit('user.login', 'login_data') # Matches
emitter.emit('user.logout', 'logout_data') # Matches
emitter.emit('user.settings.change', 'data') # Does NOT match

# Match multiple segments
emitter.on('user.**', lambda data: print(f"Any user event: {data}"))
emitter.emit('user.settings.change', 'data') # Matches
```

### Asynchronous Events

```python
import asyncio

async def async_listener(data):
    await asyncio.sleep(1)
    print(f"Async received: {data}")

emitter.on('data', async_listener)

# Use emit_async to await all listeners
asyncio.run(emitter.emit_async('data', 'some_data'))
```

### Once and Off

```python
emitter.once('init', lambda: print("Initialized"))
emitter.emit('init') # Prints "Initialized"
emitter.emit('init') # Does nothing

def my_listener():
    pass

emitter.on('test', my_listener)
emitter.off('test', my_listener)
```

## API

### `EventEmitter(max_listeners=10)`
Initializes the emitter.

### `on(event: str, listener: Callable) -> EventEmitter`
Registers a listener for the specified event.

### `once(event: str, listener: Callable) -> EventEmitter`
Registers a one-time listener.

### `off(event: str, listener: Callable = None) -> EventEmitter`
Removes a listener. If no listener is provided, removes all listeners for the event.

### `emit(event: str, *args, **kwargs) -> bool`
Synchronously emits an event.

### `async emit_async(event: str, *args, **kwargs) -> bool`
Asynchronously emits an event and awaits all async listeners.

### `set_max_listeners(n: int) -> EventEmitter`
Sets the maximum number of listeners allowed per event.

### `get_history() -> List[Dict]`
Returns the event history.
