from typing import List, Optional, Any

class ValidationError(Exception):
    """Exception raised for errors during JSON Schema validation.

    Attributes:
        message: The error message.
        path: The JSON path where the error occurred, as a list of keys/indices.
        schema_path: The JSON path within the schema where the error occurred.
        instance: The instance value that failed validation.
        schema: The schema keyword that failed validation.
    """
    def __init__(
        self,
        message: str,
        path: Optional[List[Any]] = None,
        schema_path: Optional[List[Any]] = None,
        instance: Any = None,
        schema: Any = None
    ):
        super().__init__(message)
        self.message = message
        self.path = path or []
        self.schema_path = schema_path or []
        self.instance = instance
        self.schema = schema

    def __str__(self) -> str:
        path_str = "root" + "".join(f"[{repr(p)}]" for p in self.path)
        return f"{self.message} at {path_str}"

    @property
    def json_path(self) -> str:
        """Returns the JSON path as a string (e.g., '$.properties.name')."""
        if not self.path:
            return "$"
        parts = []
        for p in self.path:
            if isinstance(p, int):
                parts.append(f"[{p}]")
            else:
                parts.append(f".{p}")
        return "$" + "".join(parts)
