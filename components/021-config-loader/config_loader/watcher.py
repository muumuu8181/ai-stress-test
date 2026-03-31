import os
import time
import threading
from pathlib import Path
from typing import Callable, List, Dict, Optional

class ConfigWatcher:
    def __init__(
        self,
        file_paths: List[Path],
        callback: Callable[[], None],
        interval: float = 1.0
    ):
        """
        Watches a list of files for changes and calls a callback when a change is detected.

        Args:
            file_paths (List[Path]): List of file paths to watch.
            callback (Callable[[], None]): Function to call when a file changes.
            interval (float): Polling interval in seconds.
        """
        self.file_paths = file_paths
        self.callback = callback
        self.interval = interval
        self._mtimes: Dict[Path, float] = {}
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self._update_mtimes()

    def _update_mtimes(self):
        for path in self.file_paths:
            if path.exists():
                self._mtimes[path] = path.stat().st_mtime
            else:
                self._mtimes[path] = 0.0

    def _check_for_changes(self) -> bool:
        changed = False
        for path in self.file_paths:
            if path.exists():
                mtime = path.stat().st_mtime
                if mtime > self._mtimes.get(path, 0.0):
                    self._mtimes[path] = mtime
                    changed = True
            elif path in self._mtimes and self._mtimes[path] != 0.0:
                # File was deleted
                self._mtimes[path] = 0.0
                changed = True
        return changed

    def _run(self):
        while not self._stop_event.is_set():
            if self._check_for_changes():
                self.callback()
            time.sleep(self.interval)

    def start(self):
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        if self._thread is None:
            return
        self._stop_event.set()
        self._thread.join()
        self._thread = None
