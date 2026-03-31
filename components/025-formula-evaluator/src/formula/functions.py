from typing import List, Any, Callable, Dict
from .cell import ERROR_DIV0

def sum_func(args: List[Any]) -> float:
    """
    Calculates the sum of all numeric values in the arguments.
    Supports nested lists (from ranges).
    """
    total = 0.0
    for arg in args:
        if isinstance(arg, list):
            total += sum_func(arg)
        elif isinstance(arg, (int, float)):
            total += float(arg)
        elif isinstance(arg, str):
            try:
                total += float(arg)
            except ValueError:
                pass
    return total

def avg_func(args: List[Any]) -> Any:
    """
    Calculates the average of all numeric values in the arguments.
    Returns #DIV/0! if no numeric values are present.
    """
    flat_args = []
    def flatten(items):
        for item in items:
            if isinstance(item, list):
                flatten(item)
            elif isinstance(item, (int, float)):
                flat_args.append(float(item))
            elif isinstance(item, str):
                try:
                    flat_args.append(float(item))
                except ValueError:
                    pass
    flatten(args)
    if not flat_args:
        return ERROR_DIV0
    return sum(flat_args) / len(flat_args)

def min_func(args: List[Any]) -> float:
    """
    Returns the minimum numeric value in the arguments.
    """
    flat_args = []
    def flatten(items):
        for item in items:
            if isinstance(item, list):
                flatten(item)
            elif isinstance(item, (int, float)):
                flat_args.append(float(item))
            elif isinstance(item, str):
                try:
                    flat_args.append(float(item))
                except ValueError:
                    pass
    flatten(args)
    if not flat_args:
        return 0.0
    return min(flat_args)

def max_func(args: List[Any]) -> float:
    """
    Returns the maximum numeric value in the arguments.
    """
    flat_args = []
    def flatten(items):
        for item in items:
            if isinstance(item, list):
                flatten(item)
            elif isinstance(item, (int, float)):
                flat_args.append(float(item))
            elif isinstance(item, str):
                try:
                    flat_args.append(float(item))
                except ValueError:
                    pass
    flatten(args)
    if not flat_args:
        return 0.0
    return max(flat_args)

def count_func(args: List[Any]) -> float:
    """
    Counts the number of numeric values in the arguments.
    """
    count = 0
    def do_count(items):
        nonlocal count
        for item in items:
            if isinstance(item, list):
                do_count(item)
            elif isinstance(item, (int, float)):
                count += 1
            elif isinstance(item, str):
                try:
                    float(item)
                    count += 1
                except ValueError:
                    pass
    do_count(args)
    return float(count)

def if_func(args: List[Any]) -> Any:
    """
    Evaluates a condition and returns different values based on the result.
    Usage: IF(condition, true_value, false_value)
    """
    if len(args) < 2:
        return "#VALUE!"
    condition = args[0]
    true_val = args[1]
    false_val = args[2] if len(args) > 2 else ""

    if condition:
        return true_val
    else:
        return false_val

def vlookup_func(args: List[Any]) -> Any:
    """
    Looks for a value in the leftmost column of a table, and returns a value in the same row from a specified column.
    Usage: VLOOKUP(lookup_value, table_array, col_index_num, [range_lookup])
    """
    if len(args) < 3:
        return "#VALUE!"

    lookup_value = args[0]
    table_array = args[1] # Expected to be a list of lists (rows)
    try:
        col_index = int(args[2]) - 1 # 1-indexed to 0-indexed
    except (ValueError, TypeError):
        return "#VALUE!"

    range_lookup = args[3] if len(args) > 3 else True

    if not isinstance(table_array, list):
        return "#VALUE!"

    # Standard VLOOKUP behavior
    for row in table_array:
        if not isinstance(row, list):
            # Try to handle flat list if range_ref was flat? No, table_array must be 2D
            continue

        if row and row[0] == lookup_value:
            if 0 <= col_index < len(row):
                return row[col_index]
            else:
                return "#REF!"

    return "#N/A"

FUNCTIONS: Dict[str, Callable] = {
    "SUM": sum_func,
    "AVG": avg_func,
    "MIN": min_func,
    "MAX": max_func,
    "COUNT": count_func,
    "IF": if_func,
    "VLOOKUP": vlookup_func
}
