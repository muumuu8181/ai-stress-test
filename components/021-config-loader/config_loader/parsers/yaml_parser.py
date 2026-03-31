import re
from typing import Any, Dict, List, Union, Tuple

def parse_yaml_subset(content: str) -> Dict[str, Any]:
    """
    Parses a YAML string (subset) into a dictionary.
    Supports key-value, indentation-based nesting, and simple lists.

    Args:
        content (str): The YAML string to parse.

    Returns:
        Dict[str, Any]: The parsed dictionary.
    """
    lines = content.splitlines()

    def _parse_value(value: str) -> Any:
        value = value.strip()
        if not value:
            return None
        # Remove quotes if present
        if len(value) >= 2 and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")):
            return value[1:-1]

        # Try boolean/null
        val_lower = value.lower()
        if val_lower == 'true': return True
        if val_lower == 'false': return False
        if val_lower == 'null': return None

        # Try numeric types
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def _get_indent(line: str) -> int:
        return len(line) - len(line.lstrip())

    def _parse_recursive(start_idx: int, current_indent: int) -> Tuple[Union[Dict[str, Any], List[Any]], int]:
        result: Dict[str, Any] = {}
        items: List[Any] = []
        is_list = False

        i = start_idx
        while i < len(lines):
            line = lines[i]
            stripped = line.lstrip()

            if not stripped or stripped.startswith('#'):
                i += 1
                continue

            indent = _get_indent(line)

            if indent < current_indent:
                break

            if stripped.startswith('-'):
                is_list = True
                val_str = stripped[1:].strip()
                if val_str:
                    items.append(_parse_value(val_str))
                    i += 1
                else:
                    # Nested block in list
                    nested_val, next_i = _parse_recursive(i + 1, indent + 2)
                    items.append(nested_val)
                    i = next_i
                continue

            if ':' in stripped:
                key, value = stripped.split(':', 1)
                key = key.strip()
                value = value.strip()

                if value:
                    result[key] = _parse_value(value)
                    i += 1
                else:
                    # Check next line for nesting
                    next_i = i + 1
                    found_nested = False
                    while next_i < len(lines):
                        next_line = lines[next_i]
                        if not next_line.strip() or next_line.lstrip().startswith('#'):
                            next_i += 1
                            continue
                        if _get_indent(next_line) > indent:
                            nested_val, new_i = _parse_recursive(next_i, _get_indent(next_line))
                            result[key] = nested_val
                            i = new_i
                            found_nested = True
                        break

                    if not found_nested:
                        result[key] = None
                        i += 1
                continue

            i += 1

        return (items if is_list else result), i

    res, _ = _parse_recursive(0, 0)
    return res if isinstance(res, dict) else {}
