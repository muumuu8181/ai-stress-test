import re
from typing import Any, Dict, List, Union, Tuple, Optional

def parse_yaml(content: str) -> Dict[str, Any]:
    """
    Parses a YAML string (subset) into a dictionary.
    Supports key-value, indentation-based nesting, and simple lists.
    """
    lines = content.splitlines()

    def _get_indent(line: str) -> int:
        return len(line) - len(line.lstrip())

    def _parse_value(value: str) -> Any:
        value = value.strip()
        if not value:
            return None
        if len(value) >= 2 and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")):
            return value[1:-1]
        val_lower = value.lower()
        if val_lower == 'true': return True
        if val_lower == 'false': return False
        if val_lower in ('null', '~'): return None
        try:
            if '.' in value: return float(value)
            return int(value)
        except ValueError:
            return value

    def _parse_block(start_idx: int, min_indent: int) -> Tuple[Union[Dict[str, Any], List[Any]], int]:
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
            if indent < min_indent:
                break

            if stripped.startswith('-'):
                is_list = True
                val_str = stripped[1:].strip()
                if ':' in val_str:
                    # Case: - key: value
                    # The dict starts with this line (minus the dash)
                    dict_lines = [line.replace('-', ' ', 1)]
                    i += 1
                    while i < len(lines):
                        if not lines[i].strip() or lines[i].lstrip().startswith('#'):
                            dict_lines.append(lines[i])
                            i += 1
                            continue
                        if _get_indent(lines[i]) > indent:
                            dict_lines.append(lines[i])
                            i += 1
                        else:
                            break
                    items.append(parse_yaml("\n".join(dict_lines)))
                elif val_str:
                    items.append(_parse_value(val_str))
                    i += 1
                else:
                    # Case: -
                    #        key: val
                    i += 1
                    if i < len(lines):
                        next_indent = _get_indent(lines[i])
                        if next_indent > indent:
                            val, next_i = _parse_block(i, next_indent)
                            items.append(val)
                            i = next_i
                        else:
                            items.append(None)
                    else:
                        items.append(None)
                continue

            if ':' in stripped:
                key, value = stripped.split(':', 1)
                key = key.strip()
                value = value.strip()
                if value:
                    result[key] = _parse_value(value)
                    i += 1
                else:
                    i += 1
                    if i < len(lines):
                        next_indent = _get_indent(lines[i])
                        if next_indent > indent:
                            val, next_i = _parse_block(i, next_indent)
                            result[key] = val
                            i = next_i
                        else:
                            result[key] = None
                    else:
                        result[key] = None
                continue
            i += 1

        return (items if is_list else result), i

    res, _ = _parse_block(0, 0)
    return res if isinstance(res, dict) else {}
