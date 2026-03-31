from typing import List, Any, Callable, Dict
from .cell import ERROR_DIV0, ERROR_NA, ERROR_REF, is_error

def sum_func(args: List[Any]) -> Any:
    """
    Calculates the sum of all numeric values in the arguments.
    Supports nested lists (from ranges).
    Propagates spreadsheet errors.
    """
    total = 0.0
    for arg in args:
        if isinstance(arg, list):
            res = sum_func(arg)
            if is_error(res): return res
            total += res
        elif is_error(arg):
            return arg
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
    Propagates spreadsheet errors.
    """
    flat_args = []
    def flatten(items):
        for item in items:
            if isinstance(item, list):
                res = flatten(item)
                if is_error(res): return res
            elif is_error(item):
                return item
            elif isinstance(item, (int, float)):
                flat_args.append(float(item))
            elif isinstance(item, str):
                try:
                    flat_args.append(float(item))
                except ValueError:
                    pass
        return None

    err = flatten(args)
    if err: return err

    if not flat_args:
        return ERROR_DIV0
    return sum(flat_args) / len(flat_args)

def min_func(args: List[Any]) -> Any:
    """
    Returns the minimum numeric value in the arguments.
    Propagates spreadsheet errors.
    """
    flat_args = []
    def flatten(items):
        for item in items:
            if isinstance(item, list):
                res = flatten(item)
                if is_error(res): return res
            elif is_error(item):
                return item
            elif isinstance(item, (int, float)):
                flat_args.append(float(item))
            elif isinstance(item, str):
                try:
                    flat_args.append(float(item))
                except ValueError:
                    pass
        return None

    err = flatten(args)
    if err: return err

    if not flat_args:
        return 0.0
    return min(flat_args)

def max_func(args: List[Any]) -> Any:
    """
    Returns the maximum numeric value in the arguments.
    Propagates spreadsheet errors.
    """
    flat_args = []
    def flatten(items):
        for item in items:
            if isinstance(item, list):
                res = flatten(item)
                if is_error(res): return res
            elif is_error(item):
                return item
            elif isinstance(item, (int, float)):
                flat_args.append(float(item))
            elif isinstance(item, str):
                try:
                    flat_args.append(float(item))
                except ValueError:
                    pass
        return None

    err = flatten(args)
    if err: return err

    if not flat_args:
        return 0.0
    return max(flat_args)

def count_func(args: List[Any]) -> Any:
    """
    Counts the number of numeric values in the arguments.
    Propagates spreadsheet errors.
    """
    count = 0
    def do_count(items):
        nonlocal count
        for item in items:
            if isinstance(item, list):
                res = do_count(item)
                if is_error(res): return res
            elif is_error(item):
                return item
            elif isinstance(item, (int, float)):
                count += 1
            elif isinstance(item, str):
                try:
                    float(item)
                    count += 1
                except ValueError:
                    pass
        return None

    err = do_count(args)
    if err: return err

    return float(count)

def if_func(args: List[Any]) -> Any:
    """
    Evaluates a condition and returns different values based on the result.
    Usage: IF(condition, true_value, false_value)
    Propagates spreadsheet errors in condition.
    """
    if len(args) < 2:
        return "#VALUE!"
    condition = args[0]

    if is_error(condition):
        return condition

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
    Propagates spreadsheet errors. Case-insensitive lookup.
    """
    if len(args) < 3:
        return "#VALUE!"

    lookup_value = args[0]
    if is_error(lookup_value): return lookup_value

    table_array = args[1] # Expected to be a list of lists (rows)
    if is_error(table_array): return table_array

    try:
        col_index = int(args[2]) - 1 # 1-indexed to 0-indexed
    except (ValueError, TypeError):
        return "#VALUE!"

    range_lookup = args[3] if len(args) > 3 else True
    if is_error(range_lookup): return range_lookup

    if not isinstance(table_array, list):
        return "#VALUE!"

    # Standard VLOOKUP validation: col_index must be within table width
    # Check width of first row as proxy or max width?
    # Usually we check against the actual table provided.
    max_width = 0
    if table_array:
        for row in table_array:
            if isinstance(row, list):
                max_width = max(max_width, len(row))

    if col_index < 0 or col_index >= max_width:
        return ERROR_REF

    # Standard VLOOKUP behavior
    for row in table_array:
        if not isinstance(row, list):
            continue

        if not row: continue

        target = row[0]
        match = False
        if isinstance(target, str) and isinstance(lookup_value, str):
            match = (target.lower() == lookup_value.lower())
        else:
            match = (target == lookup_value)

        if match:
            if col_index < len(row):
                return row[col_index]
            else:
                return ERROR_REF # Should not happen with max_width check but good for safety

    return ERROR_NA

FUNCTIONS: Dict[str, Callable] = {
    "SUM": sum_func,
    "AVG": avg_func,
    "MIN": min_func,
    "MAX": max_func,
    "COUNT": count_func,
    "IF": if_func,
    "VLOOKUP": vlookup_func
}
