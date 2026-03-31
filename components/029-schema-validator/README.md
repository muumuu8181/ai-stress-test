# JSON Schema Validator

A lightweight JSON Schema validator implemented in pure Python.

## Features

- Core types support: `string`, `number`, `integer`, `boolean`, `array`, `object`, `null`
- String validation: `minLength`, `maxLength`, `pattern`, `format` (email, uri, date)
- Number validation: `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`
- Array validation: `minItems`, `maxItems`, `uniqueItems`, `items`, `contains`
- Object validation: `required`, `properties`, `additionalProperties`, `minProperties`
- Combinators: `allOf`, `anyOf`, `oneOf`, `not`
- Internal $ref resolution and recursive schema support
- Descriptive error messages with JSON path

## Usage

```python
from schemavalidator import validate, ValidationError

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 2},
        "age": {"type": "integer", "minimum": 0}
    },
    "required": ["name"]
}

instance = {"name": "Alice", "age": 30}

try:
    validate(instance, schema)
    print("Validation successful!")
except ValidationError as e:
    print(f"Validation error: {e}")
    print(f"JSON Path: {e.json_path}")
```

## Internal References ($ref)

```python
schema = {
    "definitions": {
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"}
            },
            "required": ["street", "city"]
        }
    },
    "type": "object",
    "properties": {
        "home": {"$ref": "#/definitions/address"},
        "office": {"$ref": "#/definitions/address"}
    }
}
```

## Testing

Run tests using pytest:

```bash
pytest
```
