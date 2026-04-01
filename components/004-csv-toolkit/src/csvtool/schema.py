import datetime
from typing import Any, Dict, List, Optional, Type, Union

class TypeInferrer:
    """Helper class for inferring types from values in CSV rows."""

    @staticmethod
    def infer(value: str) -> Any:
        """
        Infer type (int, float, date, bool) from string and return typed value.

        :param value: A string value to infer from.
        :return: The value cast to its inferred type (bool, int, float, date, or str).
        """
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None

        # Boolean
        if isinstance(value, str):
            v_low = value.lower()
            if v_low in ('true', 'yes', 'on', '1'):
                return True
            if v_low in ('false', 'no', 'off', '0'):
                return False

        # Integer
        try:
            return int(value)
        except (ValueError, TypeError):
            pass

        # Float
        try:
            return float(value)
        except (ValueError, TypeError):
            pass

        # Date (YYYY-MM-DD)
        if isinstance(value, str):
            try:
                return datetime.datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Return as string if no type match
        return value

class Schema:
    """A simple schema definition for CSV data validation."""

    def __init__(self, fields: Dict[str, Type]):
        """
        Initialize the schema.

        :param fields: A dictionary mapping field names to their expected Python types.
        """
        self.fields = fields

    def validate(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate and cast the row to its defined types.

        :param row: A dictionary representing a single CSV row.
        :return: A dictionary with the row's values cast to the schema's types.
        :raises ValueError: If a field is missing or a value cannot be cast.
        """
        validated_row = {}
        for field, expected_type in self.fields.items():
            if field not in row:
                raise ValueError(f"Missing field: {field}")

            value = row[field]
            try:
                # Basic casting for schema validation
                if expected_type == bool:
                    validated_row[field] = value.lower() in ('true', 'yes', 'on', '1')
                elif expected_type == int:
                    validated_row[field] = int(value)
                elif expected_type == float:
                    validated_row[field] = float(value)
                elif expected_type == datetime.date:
                    validated_row[field] = datetime.datetime.strptime(value, '%Y-%m-%d').date()
                else:
                    validated_row[field] = str(value)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid value for field '{field}': {value} (expected {expected_type.__name__})") from e
        return validated_row
