from typing import Any, Dict, Optional
from .types import Value

class Environment:
    """Class to manage variable scopes and their values."""
    def __init__(self, enclosing: Optional['Environment'] = None):
        self.values: Dict[str, Value] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: Value):
        """Defines a new variable in the current scope."""
        self.values[name] = value

    def get(self, name: str) -> Value:
        """Retrieves a variable's value, searching in enclosing scopes if necessary."""
        if name in self.values:
            return self.values[name]

        if self.enclosing:
            return self.enclosing.get(name)

        raise NameError(f"Undefined variable '{name}'.")

    def assign(self, name: str, value: Value):
        """Assigns a new value to an existing variable."""
        if name in self.values:
            self.values[name] = value
            return

        if self.enclosing:
            self.enclosing.assign(name, value)
            return

        raise NameError(f"Undefined variable '{name}'.")
