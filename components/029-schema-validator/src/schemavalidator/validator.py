from typing import Any, Dict, List, Union
from .errors import ValidationError
from .keywords import (
    validate_type,
    validate_string,
    validate_number,
    validate_array,
    validate_object,
    validate_combinators
)

class Validator:
    """JSON Schema Validator supporting standard keywords and internal $ref."""

    def __init__(self, schema: Dict[str, Any]):
        self.root_schema = schema
        self._ref_cache: Dict[str, Any] = {}

    def validate(self, instance: Any) -> None:
        """Validates the instance against the root schema.

        Raises ValidationError if validation fails.
        """
        self._validate(instance, self.root_schema, [])

    def _resolve_ref(self, ref: str) -> Any:
        """Resolves internal JSON pointers (e.g., #/definitions/address)."""
        if ref in self._ref_cache:
            return self._ref_cache[ref]

        if not ref.startswith("#"):
            raise NotImplementedError(f"External $ref not supported: {ref}")

        parts = ref.lstrip("#").split("/")
        current = self.root_schema
        for part in parts:
            if not part:
                continue
            # Decode JSON pointer escaping (~1 -> /, ~0 -> ~)
            part = part.replace("~1", "/").replace("~0", "~")
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                current = current[int(part)]
            else:
                raise ValueError(f"Could not resolve $ref: {ref} at part: {part}")

        self._ref_cache[ref] = current
        return current

    def _validate(self, instance: Any, schema: Union[Dict[str, Any], bool], path: List[Any]) -> None:
        """Internal recursive validation function."""
        # Boolean schema support
        if isinstance(schema, bool):
            if schema is True:
                return
            else:
                raise ValidationError("Boolean schema is false", path)

        if not isinstance(schema, dict):
            return

        # Handle $ref
        if "$ref" in schema:
            ref_schema = self._resolve_ref(schema["$ref"])
            # According to some specs, other keywords are ignored when $ref is present.
            # In newer drafts, $ref can be adjacent to other keywords.
            # We'll follow the older convention for simplicity unless needed.
            return self._validate(instance, ref_schema, path)

        # Basic types
        validate_type(instance, schema, path)

        # String keywords
        validate_string(instance, schema, path)

        # Number/Integer keywords
        validate_number(instance, schema, path)

        # Array keywords
        validate_array(instance, schema, path, self._validate)

        # Object keywords
        validate_object(instance, schema, path, self._validate)

        # Combinators
        validate_combinators(instance, schema, path, self._validate)

def validate(instance: Any, schema: Dict[str, Any]) -> None:
    """Convenience function to validate an instance against a schema."""
    Validator(schema).validate(instance)
