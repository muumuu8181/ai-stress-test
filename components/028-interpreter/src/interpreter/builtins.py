from typing import List, Any
from .types import (
    Value, BuiltinFunctionValue, IntegerValue, FloatValue,
    StringValue, BooleanValue, ArrayValue
)

def builtin_print(args: List[Value]) -> Value:
    """Prints the given values to standard output."""
    print(*(a.value for a in args))
    return BooleanValue(True)

def builtin_len(args: List[Value]) -> Value:
    """Returns the length of a string or array."""
    if len(args) != 1:
        raise ValueError("len() expects exactly 1 argument.")

    val = args[0].value
    if isinstance(val, (str, list)):
        return IntegerValue(len(val))

    raise TypeError(f"len() not supported for type {type(val)}")

def builtin_type(args: List[Value]) -> Value:
    """Returns the type name of the given value."""
    if len(args) != 1:
        raise ValueError("type() expects exactly 1 argument.")

    val = args[0]
    if isinstance(val, IntegerValue): return StringValue("integer")
    if isinstance(val, FloatValue): return StringValue("float")
    if isinstance(val, StringValue): return StringValue("string")
    if isinstance(val, BooleanValue): return StringValue("boolean")
    if isinstance(val, ArrayValue): return StringValue("array")
    return StringValue("function")

def builtin_push(args: List[Value]) -> Value:
    """Appends an element to an array."""
    if len(args) != 2:
        raise ValueError("push() expects exactly 2 arguments (array, element).")

    arr_val = args[0]
    if not isinstance(arr_val, ArrayValue):
        raise TypeError("push() first argument must be an array.")

    arr_val.value.append(args[1])
    return arr_val

def builtin_pop(args: List[Value]) -> Value:
    """Removes and returns the last element of an array."""
    if len(args) != 1:
        raise ValueError("pop() expects exactly 1 argument.")

    arr_val = args[0]
    if not isinstance(arr_val, ArrayValue):
        raise TypeError("pop() argument must be an array.")

    if not arr_val.value:
        raise ValueError("pop() from empty array.")

    return arr_val.value.pop()

def get_builtins() -> List[BuiltinFunctionValue]:
    """Returns a list of all built-in function values."""
    return [
        BuiltinFunctionValue("print", builtin_print),
        BuiltinFunctionValue("len", builtin_len),
        BuiltinFunctionValue("type", builtin_type),
        BuiltinFunctionValue("push", builtin_push),
        BuiltinFunctionValue("pop", builtin_pop),
    ]
