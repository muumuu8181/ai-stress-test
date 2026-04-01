import pytest
import asyncio
from event_emitter.emitter import EventEmitter

def test_basic_on_emit():
    emitter = EventEmitter()
    called = []
    def listener(data):
        called.append(data)

    emitter.on('test', listener)
    emitter.emit('test', 'hello')

    assert called == ['hello']

def test_once():
    emitter = EventEmitter()
    called = []
    def listener():
        called.append(True)

    emitter.once('test', listener)
    emitter.emit('test')
    emitter.emit('test')

    assert len(called) == 1

def test_off():
    emitter = EventEmitter()
    called = []
    def listener():
        called.append(True)

    emitter.on('test', listener)
    emitter.off('test', listener)
    emitter.emit('test')

    assert len(called) == 0

def test_off_all():
    emitter = EventEmitter()
    called = []
    def l1(): called.append(1)
    def l2(): called.append(2)

    emitter.on('test', l1)
    emitter.on('test', l2)
    emitter.off('test')
    emitter.emit('test')

    assert len(called) == 0

def test_wildcard_single_segment():
    emitter = EventEmitter()
    called = []
    emitter.on('foo.*', lambda x: called.append(x))

    emitter.emit('foo.bar', 1)
    emitter.emit('foo.baz', 2)
    emitter.emit('foo.bar.baz', 3) # Should not match

    assert called == [1, 2]

def test_wildcard_multi_segment():
    emitter = EventEmitter()
    called = []
    emitter.on('foo.**', lambda x: called.append(x))

    emitter.emit('foo.bar', 1)
    emitter.emit('foo.bar.baz', 2)
    emitter.emit('bar.foo', 3) # Should not match

    assert called == [1, 2]

def test_wildcard_global():
    emitter = EventEmitter()
    called = []
    emitter.on('**', lambda x: called.append(x))

    emitter.emit('foo', 1)
    emitter.emit('foo.bar', 2)

    assert called == [1, 2]

def test_emit_async():
    emitter = EventEmitter()
    called = []

    async def async_listener(data):
        await asyncio.sleep(0.01)
        called.append(data)

    def sync_listener(data):
        called.append(data + 1)

    emitter.on('test', async_listener)
    emitter.on('test', sync_listener)

    asyncio.run(emitter.emit_async('test', 10))

    assert 10 in called
    assert 11 in called
    assert len(called) == 2

def test_error_handling():
    emitter = EventEmitter()
    errors = []

    def listener():
        raise ValueError("Oops")

    def error_handler(err):
        errors.append(err)

    emitter.on('test', listener)
    emitter.on('error', error_handler)

    emitter.emit('test')

    assert len(errors) == 1
    assert isinstance(errors[0], ValueError)

def test_max_listeners_warning(caplog):
    emitter = EventEmitter(max_listeners=1)
    emitter.on('test', lambda: None)
    emitter.on('test', lambda: None)

    assert "Max listeners (1) exceeded for event: test" in caplog.text

def test_history():
    emitter = EventEmitter()
    # Use a listener that accepts anything
    emitter.on('test', lambda *a, **kw: None)
    emitter.emit('test', 1, key='val')

    history = emitter.get_history()
    assert len(history) == 1
    assert history[0]['event'] == 'test'
    assert history[0]['args'] == (1,)
    assert history[0]['kwargs'] == {'key': 'val'}
    assert 'timestamp' in history[0]

def test_off_with_once():
    emitter = EventEmitter()
    called = []
    def listener():
        called.append(True)

    emitter.once('test', listener)
    emitter.off('test', listener)
    emitter.emit('test')

    assert len(called) == 0

def test_remove_all_listeners():
    emitter = EventEmitter()
    emitter.on('a', lambda: None)
    emitter.on('b', lambda: None)

    emitter.remove_all_listeners()
    assert len(emitter._listeners) == 0

def test_wildcard_matching_edge_cases():
    emitter = EventEmitter()

    # Pattern: foo.*
    assert emitter._event_matches('foo.*', 'foo.bar') is True
    assert emitter._event_matches('foo.*', 'foo.bar.baz') is False
    assert emitter._event_matches('foo.*', 'foo') is False

    # Pattern: foo.**
    assert emitter._event_matches('foo.**', 'foo.bar') is True
    assert emitter._event_matches('foo.**', 'foo.bar.baz') is True
    assert emitter._event_matches('foo.**', 'foo') is True # foo.** should match foo?
    # Actually, with current implementation:
    # regex_pattern = foo(\..*)?
    # f"^{regex_pattern}$" matches "foo"

    # Pattern: *.bar
    assert emitter._event_matches('*.bar', 'foo.bar') is True
    assert emitter._event_matches('*.bar', 'a.b.bar') is False

def test_wildcard_dots_literal():
    emitter = EventEmitter()
    # Pattern 'foo.**' should match 'foo.bar' but not 'foo-bar'
    assert emitter._event_matches('foo.**', 'foo.bar') is True
    assert emitter._event_matches('foo.**', 'foo-bar') is False

def test_off_non_existent():
    emitter = EventEmitter()
    emitter.off('non_existent')
    # Should not raise any error

def test_emit_no_listeners():
    emitter = EventEmitter()
    assert emitter.emit('no_one_listening') is False

@pytest.mark.asyncio
async def test_emit_async_no_listeners():
    emitter = EventEmitter()
    assert await emitter.emit_async('no_one_listening') is False

def test_emit_error_no_handler():
    emitter = EventEmitter()
    with pytest.raises(ValueError):
        emitter.emit('error', ValueError("unhandled"))

def test_emit_async_error_no_handler():
    emitter = EventEmitter()
    with pytest.raises(ValueError):
        asyncio.run(emitter.emit_async('error', ValueError("unhandled")))

def test_emit_async_with_sync_error():
    emitter = EventEmitter()
    errors = []
    emitter.on('error', lambda e: errors.append(e))

    def buggy_listener():
        raise RuntimeError("Bug")

    emitter.on('test', buggy_listener)
    asyncio.run(emitter.emit_async('test'))
    assert len(errors) == 1

def test_set_max_history():
    emitter = EventEmitter()
    emitter.set_max_history(2)
    emitter.on('test', lambda: None)
    emitter.emit('test')
    emitter.emit('test')
    emitter.emit('test')
    assert len(emitter.get_history()) == 2

    emitter.set_max_history(0)
    assert len(emitter.get_history()) == 0
    emitter.emit('test')
    assert len(emitter.get_history()) == 0

def test_clear_history():
    emitter = EventEmitter()
    emitter.on('test', lambda: None)
    emitter.emit('test')
    emitter.clear_history()
    assert len(emitter.get_history()) == 0

def test_once_async():
    emitter = EventEmitter()
    called = []

    async def async_listener(data):
        await asyncio.sleep(0.01)
        called.append(data)

    emitter.once('test', async_listener)
    asyncio.run(emitter.emit_async('test', 1))
    asyncio.run(emitter.emit_async('test', 2))

    assert called == [1]

def test_once_async_race():
    emitter = EventEmitter()
    called = []

    async def async_listener():
        await asyncio.sleep(0.01)
        called.append(True)

    emitter.once('test', async_listener)

    # Emit twice in the same event loop turn (using a small helper)
    async def run_race():
        # Both calls to emit_async should be started, but the listener
        # should only be added to tasks once because it removes itself
        # synchronously when called.
        await asyncio.gather(
            emitter.emit_async('test'),
            emitter.emit_async('test')
        )

    asyncio.run(run_race())
    assert len(called) == 1

def test_emit_no_loop_sync_async_listener(caplog):
    emitter = EventEmitter()

    async def async_listener():
        pass

    emitter.on('test', async_listener)

    # This should log an error but not raise RuntimeError: no running event loop
    emitter.emit('test')
    assert "Cannot schedule async listener in sync emit: no running event loop" in caplog.text

def test_emit_async_error_awaits_tasks():
    emitter = EventEmitter()

    called = []
    async def slow_listener():
        await asyncio.sleep(0.1)
        called.append('slow')

    def crashing_listener():
        raise ValueError("Crash")

    emitter.on('test', slow_listener)
    emitter.on('test', crashing_listener)

    # Even if crashing_listener raises an exception,
    # slow_listener should still be awaited and finish.
    # If no 'error' listener is present, emit_async will raise the error.
    with pytest.raises(ValueError):
        asyncio.run(emitter.emit_async('test'))

    assert called == ['slow']
