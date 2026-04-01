from typing import Callable, List, Dict, Any, Union, Optional
import collections
import logging
import re
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class EventEmitter:
    """
    A Node.js-style EventEmitter implementation with support for namespaces and wildcards.
    """

    def __init__(self, max_listeners: int = 10):
        """
        Initialize the EventEmitter.

        Args:
            max_listeners: The maximum number of listeners allowed per event.
        """
        self._listeners: Dict[str, List[Callable]] = collections.defaultdict(list)
        self._max_listeners = max_listeners
        self._max_history = 100
        self._history: collections.deque = collections.deque(maxlen=self._max_history)

    def on(self, event: str, listener: Callable) -> 'EventEmitter':
        """
        Register a listener for an event.

        Args:
            event: The event name.
            listener: The listener function.

        Returns:
            The EventEmitter instance.
        """
        if len(self._listeners[event]) >= self._max_listeners:
            logger.warning(f"Max listeners ({self._max_listeners}) exceeded for event: {event}")

        self._listeners[event].append(listener)
        return self

    def once(self, event: str, listener: Callable) -> 'EventEmitter':
        """
        Register a listener that will be called at most once for an event.

        Args:
            event: The event name.
            listener: The listener function.

        Returns:
            The EventEmitter instance.
        """
        def wrapper(*args, **kwargs):
            # Synchronously remove the wrapper to avoid race conditions.
            self.off(event, wrapper)
            return listener(*args, **kwargs)

        wrapper._original_listener = listener
        return self.on(event, wrapper)

    def off(self, event: Optional[str] = None, listener: Optional[Callable] = None) -> 'EventEmitter':
        """
        Remove a listener for an event.

        Args:
            event: The event name. If None, remove all listeners for all events.
            listener: The listener function to remove. If None, remove all listeners for the event.

        Returns:
            The EventEmitter instance.
        """
        if event is None:
            self._listeners.clear()
            return self

        if event not in self._listeners:
            return self

        if listener is None:
            del self._listeners[event]
        else:
            new_listeners = []
            for l in self._listeners[event]:
                if l == listener or getattr(l, '_original_listener', None) == listener:
                    continue
                new_listeners.append(l)
            if new_listeners:
                self._listeners[event] = new_listeners
            else:
                del self._listeners[event]

        return self

    def remove_all_listeners(self, event: Optional[str] = None) -> 'EventEmitter':
        """
        Remove all listeners, or those of the specified event.

        Args:
            event: The event name.

        Returns:
            The EventEmitter instance.
        """
        return self.off(event)

    def _match_listeners(self, event_name: str) -> List[Callable]:
        """
        Find all listeners that match the event name, including wildcards.

        Args:
            event_name: The event name to match.

        Returns:
            A list of matching listeners.
        """
        matched_listeners = []

        for registered_event, listeners in self._listeners.items():
            if self._event_matches(registered_event, event_name):
                matched_listeners.extend(listeners)

        return matched_listeners

    def _event_matches(self, pattern: str, event_name: str) -> bool:
        """
        Check if an event name matches a pattern (including wildcards).

        Patterns:
        - 'foo.bar' matches 'foo.bar'
        - 'foo.*' matches 'foo.bar', 'foo.baz' but NOT 'foo.bar.baz'
        - 'foo.**' matches 'foo.bar', 'foo.bar.baz', etc.
        - '*' matches any single segment.
        - '**' matches everything.

        Args:
            pattern: The registered event pattern (possibly with wildcards).
            event_name: The name of the emitted event.

        Returns:
            True if it matches, False otherwise.
        """
        if pattern == event_name:
            return True

        if '*' not in pattern:
            return False

        # Convert pattern to regex
        # Escape . but keep * and **
        # ** -> (\..*)?
        # * -> [^.]+

        # First escape all special regex chars
        regex_pattern = re.escape(pattern)

        # re.escape will escape '*' as well.
        # Our tokens are now '\*' and '\.\*' and '\.\*\*' etc.

        # Match 'foo.**' -> 'foo(\..*)?'
        # Note: pattern must match exactly.
        # Replace escaped sequences back to regex wildcards
        regex_pattern = regex_pattern.replace(r'\.\*\*', r'(\..*)?')
        regex_pattern = regex_pattern.replace(r'\*\*', r'.*')
        regex_pattern = regex_pattern.replace(r'\.\*', r'\.[^.]+')
        regex_pattern = regex_pattern.replace(r'\*', r'[^.]+')

        # Ensure it matches the whole string
        return re.fullmatch(regex_pattern, event_name) is not None

    def emit(self, event: str, *args, **kwargs) -> bool:
        """
        Synchronously call each of the listeners registered for the event.

        Args:
            event: The event name.
            *args: Arguments to pass to listeners.
            **kwargs: Keyword arguments to pass to listeners.

        Returns:
            True if the event had listeners, False otherwise.
        """
        listeners = self._match_listeners(event)

        # Track history
        if self._max_history > 0:
            self._history.append({
                "event": event,
                "args": args,
                "kwargs": kwargs,
                "timestamp": datetime.now().isoformat()
            })

        if not listeners:
            if event == 'error':
                if args and isinstance(args[0], Exception):
                    raise args[0]
                raise ValueError(f"Unhandled error event: {args}")
            return False

        for listener in listeners:
            try:
                result = listener(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    # We can't await here since emit is sync, but we can schedule it
                    asyncio.create_task(result)
            except Exception as e:
                if event == 'error':
                    raise e
                self.emit('error', e)

        return True

    async def emit_async(self, event: str, *args, **kwargs) -> bool:
        """
        Asynchronously call each of the listeners registered for the event.

        Args:
            event: The event name.
            *args: Arguments to pass to listeners.
            **kwargs: Keyword arguments to pass to listeners.

        Returns:
            True if the event had listeners, False otherwise.
        """
        listeners = self._match_listeners(event)

        # Track history
        if self._max_history > 0:
            self._history.append({
                "event": event,
                "args": args,
                "kwargs": kwargs,
                "timestamp": datetime.now().isoformat()
            })

        if not listeners:
            if event == 'error':
                if args and isinstance(args[0], Exception):
                    raise args[0]
                raise ValueError(f"Unhandled error event: {args}")
            return False

        tasks = []
        for listener in listeners:
            try:
                result = listener(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    tasks.append(result)
            except Exception as e:
                if event == 'error':
                    raise e
                self.emit('error', e)

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, Exception):
                    if event == 'error':
                        raise res
                    self.emit('error', res)

        return True

    def set_max_listeners(self, n: int) -> 'EventEmitter':
        """
        Set the maximum number of listeners allowed per event.

        Args:
            n: The maximum number of listeners.

        Returns:
            The EventEmitter instance.
        """
        self._max_listeners = n
        return self

    def set_max_history(self, n: int) -> 'EventEmitter':
        """
        Set the maximum number of history records to keep.

        Args:
            n: The maximum number of history records.

        Returns:
            The EventEmitter instance.
        """
        self._max_history = max(0, n)
        # Re-initialize history with new maxlen
        new_history = collections.deque(self._history, maxlen=self._max_history)
        self._history = new_history
        return self

    def clear_history(self) -> 'EventEmitter':
        """
        Clear the event history.

        Returns:
            The EventEmitter instance.
        """
        self._history.clear()
        return self

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the event history.

        Returns:
            A list of event records.
        """
        return list(self._history)
