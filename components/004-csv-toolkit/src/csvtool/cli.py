import argparse
import sys
import json
import re
from typing import Any, Callable, Dict, Iterator, List, Optional, Union, Tuple, Iterable, TextIO

from .core import CSVProcessor
from .utils import write_rows

def parse_where_clause(where: str) -> Tuple[str, str, Any]:
    """
    Parse a WHERE clause string into (column, operator, value) components.

    :param where: A string like "age > 20" or 'city == "New York"'.
    :return: A tuple of (column, operator, value).
    """
    pattern = r'^\s*([^\s<>!=]+)\s*(>|<|==|!=|>=|<=)\s*(.*)$'
    match = re.match(pattern, where)
    if not match:
        raise ValueError(f"Invalid where clause: {where}. Example: 'age > 20'")

    col, op, val = match.groups()
    val = val.strip()

    # Simple unquoting
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1]
    else:
        try:
            val = float(val)
        except ValueError:
            pass
    return col, op, val

def main(args_list: Optional[List[str]] = None, stdout: Optional[TextIO] = None):
    """
    The main CLI entry point for the CSV toolkit.

    :param args_list: List of command-line arguments (default: sys.argv[1:]).
    :param stdout: Output stream for printing results (default: sys.stdout).
    """
    parser = argparse.ArgumentParser(prog='csvtool', description='CSV Toolkit CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # select subcommand
    select_parser = subparsers.add_parser('select', help='Select columns from CSV')
    select_parser.add_argument('--columns', required=True, help='Comma-separated list of columns to select')
    select_parser.add_argument('input', nargs='?', default='-', help='Input CSV file (default: stdin)')

    # filter subcommand
    filter_parser = subparsers.add_parser('filter', help='Filter rows based on condition')
    filter_parser.add_argument('--where', required=True, help='Filter condition (e.g., "age > 20" or "city == \'New York\'")')
    filter_parser.add_argument('input', nargs='?', default='-', help='Input CSV file (default: stdin)')

    # join subcommand
    join_parser = subparsers.add_parser('join', help='Join two CSV files')
    join_parser.add_argument('--on', required=True, help='Column name to join on')
    join_parser.add_argument('--how', choices=['inner', 'left'], default='inner', help='Join type (inner, left)')
    join_parser.add_argument('left_csv', help='Left CSV file')
    join_parser.add_argument('right_csv', help='Right CSV file')

    # stats subcommand
    stats_parser = subparsers.add_parser('stats', help='Get summary statistics')
    stats_parser.add_argument('input', nargs='?', default='-', help='Input CSV file (default: stdin)')

    args = parser.parse_args(args_list)

    out = stdout or sys.stdout

    if args.command == 'select':
        columns = args.columns.split(',')
        processor = CSVProcessor(args.input)
        write_rows(processor.select(columns), filepath=out)

    elif args.command == 'filter':
        try:
            col, op, val = parse_where_clause(args.where)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)

        def predicate(row: Dict[str, str]) -> bool:
            if col not in row:
                return False
            row_val = row[col]
            try:
                row_val_typed = float(row_val)
            except ValueError:
                row_val_typed = row_val

            if op == '>': return row_val_typed > val
            if op == '<': return row_val_typed < val
            if op == '==': return row_val_typed == val
            if op == '!=': return row_val_typed != val
            if op == '>=': return row_val_typed >= val
            if op == '<=': return row_val_typed <= val
            return False

        processor = CSVProcessor(args.input)
        write_rows(processor.filter(predicate), filepath=out)

    elif args.command == 'join':
        left_processor = CSVProcessor(args.left_csv)
        right_processor = CSVProcessor(args.right_csv)
        write_rows(left_processor.join(right_processor, args.on, args.how), filepath=out)

    elif args.command == 'stats':
        processor = CSVProcessor(args.input)
        print(json.dumps(processor.stats(), indent=2, default=str), file=out)

    else:
        parser.print_help(file=out)

if __name__ == '__main__':
    main()
