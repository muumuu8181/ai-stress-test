from typing import Any, Dict, List, Union, Literal

# Type aliases for JSON-like structures
JsonValue = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
Schema = Dict[str, Any]

# Supported JSON Schema types
JsonType = Literal["string", "number", "integer", "boolean", "array", "object", "null"]

def get_type(instance: Any) -> JsonType:
    """Returns the JSON type of the instance."""
    if instance is None:
        return "null"
    if isinstance(instance, bool):
        return "boolean"
    if isinstance(instance, str):
        return "string"
    if isinstance(instance, (int, float)):
        if isinstance(instance, int) or instance.is_integer():
            return "integer"
        return "number"
    if isinstance(instance, list):
        return "array"
    if isinstance(instance, dict):
        return "object"

    # Fallback/Unknown type (not standard for JSON)
    raise TypeError(f"Unknown type for instance: {type(instance)}")

def is_type(instance: Any, type_name: JsonType) -> bool:
    """Checks if the instance matches the specified JSON type."""
    actual_type = get_type(instance)

    if type_name == "number":
        # 'number' includes both integers and floats
        return actual_type in ("number", "integer")

    return actual_type == type_name
