import re
from decimal import Decimal
from typing import Any, Dict, List, Callable, Union
from .errors import ValidationError
from .types import is_type, get_type
from .format import FORMAT_VALIDATORS

def validate_type(instance: Any, schema: Any, path: List[Any]) -> None:
    """Validates the type of the instance."""
    expected_type = schema.get("type")
    if not expected_type:
        return

    if isinstance(expected_type, list):
        if not any(is_type(instance, t) for t in expected_type):
            raise ValidationError(f"Expected one of types {expected_type}, but got {get_type(instance)}", path)
    else:
        if not is_type(instance, expected_type):
            raise ValidationError(f"Expected type {expected_type}, but got {get_type(instance)}", path)

def validate_string(instance: str, schema: Dict[str, Any], path: List[Any]) -> None:
    """Validates string-specific keywords."""
    if not isinstance(instance, str):
        return

    # minLength
    if "minLength" in schema and len(instance) < schema["minLength"]:
        raise ValidationError(f"String too short (min {schema['minLength']})", path)

    # maxLength
    if "maxLength" in schema and len(instance) > schema["maxLength"]:
        raise ValidationError(f"String too long (max {schema['maxLength']})", path)

    # pattern
    if "pattern" in schema:
        if not re.search(schema["pattern"], instance):
            raise ValidationError(f"String does not match pattern {schema['pattern']}", path)

    # format
    if "format" in schema:
        format_name = schema["format"]
        if format_name in FORMAT_VALIDATORS:
            if not FORMAT_VALIDATORS[format_name](instance):
                raise ValidationError(f"String does not match format {format_name}", path)

def validate_number(instance: Union[int, float], schema: Dict[str, Any], path: List[Any]) -> None:
    """Validates number/integer-specific keywords."""
    if not isinstance(instance, (int, float)) or isinstance(instance, bool):
        return

    # minimum
    if "minimum" in schema and instance < schema["minimum"]:
        raise ValidationError(f"Value {instance} is less than minimum {schema['minimum']}", path)

    # maximum
    if "maximum" in schema and instance > schema["maximum"]:
        raise ValidationError(f"Value {instance} is greater than maximum {schema['maximum']}", path)

    # exclusiveMinimum
    if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
        raise ValidationError(f"Value {instance} is less than or equal to exclusiveMinimum {schema['exclusiveMinimum']}", path)

    # exclusiveMaximum
    if "exclusiveMaximum" in schema and instance >= schema["exclusiveMaximum"]:
        raise ValidationError(f"Value {instance} is greater than or equal to exclusiveMaximum {schema['exclusiveMaximum']}", path)

    # multipleOf
    if "multipleOf" in schema:
        inst_dec = Decimal(str(instance))
        mult_dec = Decimal(str(schema["multipleOf"]))
        if (inst_dec % mult_dec) != 0:
             raise ValidationError(f"Value {instance} is not a multiple of {schema['multipleOf']}", path)

def validate_array(instance: List[Any], schema: Dict[str, Any], path: List[Any], validate_func: Callable) -> None:
    """Validates array-specific keywords."""
    if not isinstance(instance, list):
        return

    # minItems
    if "minItems" in schema and len(instance) < schema["minItems"]:
        raise ValidationError(f"Array too short (min {schema['minItems']})", path)

    # maxItems
    if "maxItems" in schema and len(instance) > schema["maxItems"]:
        raise ValidationError(f"Array too long (max {schema['maxItems']})", path)

    # uniqueItems
    if "uniqueItems" in schema and schema["uniqueItems"]:
        seen = []
        for item in instance:
            # Distinguish between True/1 and False/0 by checking both value and type
            # Using a custom equality check that considers type for booleans
            is_duplicate = False
            for seen_item in seen:
                if item == seen_item and type(item) is type(seen_item):
                    is_duplicate = True
                    break
            if is_duplicate:
                raise ValidationError("Array items are not unique", path)
            seen.append(item)

    # items
    if "items" in schema:
        items_schema = schema["items"]
        if isinstance(items_schema, dict):
            for i, item in enumerate(instance):
                validate_func(item, items_schema, path + [i])
        elif isinstance(items_schema, list):
            for i, (item, sub_schema) in enumerate(zip(instance, items_schema)):
                validate_func(item, sub_schema, path + [i])

    # contains
    if "contains" in schema:
        contains_schema = schema["contains"]
        found = False
        for item in instance:
            try:
                validate_func(item, contains_schema, path)
                found = True
                break
            except ValidationError:
                continue
        if not found:
             raise ValidationError("Array does not contain any item matching the schema", path)

def validate_object(instance: Dict[str, Any], schema: Dict[str, Any], path: List[Any], validate_func: Callable) -> None:
    """Validates object-specific keywords."""
    if not isinstance(instance, dict):
        return

    # required
    if "required" in schema:
        for prop in schema["required"]:
            if prop not in instance:
                raise ValidationError(f"Required property '{prop}' is missing", path)

    # minProperties
    if "minProperties" in schema and len(instance) < schema["minProperties"]:
        raise ValidationError(f"Object has too few properties (min {schema['minProperties']})", path)

    # maxProperties
    if "maxProperties" in schema and len(instance) > schema["maxProperties"]:
        raise ValidationError(f"Object has too many properties (max {schema['maxProperties']})", path)

    # properties & additionalProperties
    properties = schema.get("properties", {})
    additional_properties = schema.get("additionalProperties", True)

    for key, value in instance.items():
        if key in properties:
            validate_func(value, properties[key], path + [key])
        elif additional_properties is False:
            raise ValidationError(f"Additional property '{key}' is not allowed", path)
        elif isinstance(additional_properties, dict):
            validate_func(value, additional_properties, path + [key])

def validate_combinators(instance: Any, schema: Dict[str, Any], path: List[Any], validate_func: Callable) -> None:
    """Validates allOf, anyOf, oneOf, and not keywords."""

    # allOf
    if "allOf" in schema:
        for i, sub_schema in enumerate(schema["allOf"]):
            validate_func(instance, sub_schema, path)

    # anyOf
    if "anyOf" in schema:
        success = False
        for sub_schema in schema["anyOf"]:
            try:
                validate_func(instance, sub_schema, path)
                success = True
                break
            except ValidationError:
                continue
        if not success:
            raise ValidationError("Does not match any of the schemas in anyOf", path)

    # oneOf
    if "oneOf" in schema:
        matches = 0
        for sub_schema in schema["oneOf"]:
            try:
                validate_func(instance, sub_schema, path)
                matches += 1
            except ValidationError:
                continue
        if matches != 1:
            raise ValidationError(f"Matches {matches} schemas in oneOf, expected exactly 1", path)

    # not
    if "not" in schema:
        is_valid = True
        try:
            validate_func(instance, schema["not"], path)
        except ValidationError:
            is_valid = False

        if is_valid:
            raise ValidationError("Matches the schema in 'not'", path)
