from typing import Any, Dict, List, Optional, Union, Type, Tuple

class ValidationError(Exception):
    """Exception raised for errors in configuration validation."""
    pass

class SchemaField:
    def __init__(
        self,
        expected_type: Union[Type, Tuple[Type, ...]],
        required: bool = False,
        default: Any = None,
        min_val: Optional[Union[int, float]] = None,
        max_val: Optional[Union[int, float]] = None,
        choices: Optional[List[Any]] = None
    ):
        self.expected_type = expected_type
        self.required = required
        self.default = default
        self.min_val = min_val
        self.max_val = max_val
        self.choices = choices

    def validate(self, name: str, value: Any) -> Any:
        if value is None:
            if self.required:
                raise ValidationError(f"Field '{name}' is required")
            return self.default

        # Try to cast if it's the wrong type (especially for ENV variables which are all strings)
        if not isinstance(value, self.expected_type):
            try:
                if isinstance(self.expected_type, tuple):
                    # For simplicity, pick the first one if multiple are expected
                    target_type = self.expected_type[0]
                else:
                    target_type = self.expected_type

                if target_type == bool and isinstance(value, str):
                    if value.lower() in ('true', '1', 'yes'):
                        value = True
                    elif value.lower() in ('false', '0', 'no'):
                        value = False
                    else:
                        raise ValueError()
                else:
                    value = target_type(value)
            except (ValueError, TypeError):
                raise ValidationError(
                    f"Field '{name}' must be of type {self.expected_type}, "
                    f"got {type(value)} with value {value}"
                )

        if self.min_val is not None and value < self.min_val:
            raise ValidationError(f"Field '{name}' value {value} is less than minimum {self.min_val}")

        if self.max_val is not None and value > self.max_val:
            raise ValidationError(f"Field '{name}' value {value} is greater than maximum {self.max_val}")

        if self.choices is not None and value not in self.choices:
            raise ValidationError(f"Field '{name}' value {value} is not one of {self.choices}")

        return value

class Validator:
    def __init__(self, schema: Dict[str, Union[SchemaField, 'Validator']]):
        self.schema = schema

    def validate(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        validated_data = {}
        for key, rule in self.schema.items():
            full_key = f"{prefix}.{key}" if prefix else key
            value = data.get(key)

            if isinstance(rule, Validator):
                if value is None:
                    # Check if any nested field is required
                    try:
                        validated_data[key] = rule.validate({}, full_key)
                    except ValidationError as e:
                        raise ValidationError(f"Missing required fields in nested configuration '{full_key}': {str(e)}")
                elif isinstance(value, dict):
                    validated_data[key] = rule.validate(value, full_key)
                else:
                    raise ValidationError(f"Field '{full_key}' must be a dictionary")
            else:
                validated_data[key] = rule.validate(full_key, value)

        # Keep keys that are not in schema
        for key in data:
            if key not in self.schema:
                validated_data[key] = data[key]

        return validated_data
