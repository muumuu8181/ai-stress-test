from typing import Any, List, Dict, Optional, Callable

class Value:
    """Base class for all runtime values."""
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Value):
            return self.value == other.value
        return False

class IntegerValue(Value):
    """Integer runtime value."""
    def __init__(self, value: int):
        super().__init__(value)

class FloatValue(Value):
    """Floating point runtime value."""
    def __init__(self, value: float):
        super().__init__(value)

class StringValue(Value):
    """String runtime value."""
    def __init__(self, value: str):
        super().__init__(value)

class BooleanValue(Value):
    """Boolean runtime value."""
    def __init__(self, value: bool):
        super().__init__(value)

class ArrayValue(Value):
    """Array runtime value."""
    def __init__(self, value: List[Value]):
        super().__init__(value)

    def __repr__(self) -> str:
        return f"ArrayValue([{', '.join(repr(v) for v in self.value)}])"

class FunctionValue(Value):
    """Function runtime value."""
    def __init__(self, name: str, params: List[str], body: Any, env: Any):
        super().__init__(None)
        self.name = name
        self.params = params
        self.body = body
        self.env = env # Closure environment

    def __repr__(self) -> str:
        return f"FunctionValue(name={self.name}, params={self.params})"

class BuiltinFunctionValue(Value):
    """Built-in function runtime value."""
    def __init__(self, name: str, func: Callable[..., Value]):
        super().__init__(None)
        self.name = name
        self.func = func

    def __repr__(self) -> str:
        return f"BuiltinFunctionValue(name={self.name})"
