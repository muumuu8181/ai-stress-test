import csv
import operator
import statistics
import sys
from collections import defaultdict
from typing import Any, Callable, Dict, Iterator, List, Optional, Union, Tuple, Iterable, Set

from .utils import detect_delimiter, get_input_stream, StreamHandler
from .schema import TypeInferrer, Schema

class CSVProcessor:
    """Core CSV processing class providing streaming-friendly methods."""

    def __init__(self, filepath: Optional[str] = None, delimiter: Optional[str] = None):
        """
        Initialize the CSV processor.

        :param filepath: Path to the CSV file or '-' for stdin.
        :param delimiter: The CSV delimiter (e.g., ',', '\t'). If not provided, it's detected automatically.
        """
        self.filepath = filepath
        self.delimiter = delimiter or (detect_delimiter(filepath) if filepath and filepath != '-' else ',')

    def _get_reader(self) -> Iterator[Dict[str, str]]:
        """Internal generator to yield rows from the input stream."""
        with StreamHandler(self.filepath, 'r') as in_stream:
            reader = csv.DictReader(in_stream, delimiter=self.delimiter)
            for row in reader:
                yield row

    def stream_rows(self) -> Iterator[Dict[str, str]]:
        """
        Yield each row of the CSV as a dictionary of strings.

        :return: An iterator yielding rows as dictionaries.
        """
        return self._get_reader()

    def select(self, columns: List[str]) -> Iterator[Dict[str, str]]:
        """
        Select a subset of columns from each row.

        :param columns: List of column names to include in the output.
        :return: An iterator yielding filtered dictionaries.
        """
        for row in self.stream_rows():
            yield {col: row[col] for col in columns if col in row}

    def filter(self, predicate: Callable[[Dict[str, str]], bool]) -> Iterator[Dict[str, str]]:
        """
        Filter rows based on a given predicate function.

        :param predicate: A function that takes a row (dict) and returns True to include it.
        :return: An iterator yielding rows that satisfy the predicate.
        """
        for row in self.stream_rows():
            if predicate(row):
                yield row

    def sort(self, key_col: str, reverse: bool = False) -> Iterator[Dict[str, str]]:
        """
        Sort the CSV data by a key column. Note: this is an in-memory operation.

        :param key_col: The column name to use as a sort key.
        :param reverse: Whether to sort in descending order.
        :return: An iterator yielding sorted rows.
        """
        # Sorting requires all rows to be loaded in memory
        rows = list(self.stream_rows())
        return iter(sorted(rows, key=lambda r: (TypeInferrer.infer(r.get(key_col, ''))), reverse=reverse))

    def validate(self, schema: Schema) -> Iterator[Dict[str, Any]]:
        """
        Validate and cast rows according to the provided schema.

        :param schema: A Schema object defining fields and their expected types.
        :return: An iterator yielding validated and cast rows.
        """
        for row in self.stream_rows():
            yield schema.validate(row)

    def groupby(self, key_col: str, aggregations: Dict[str, str]) -> Iterator[Dict[str, Any]]:
        """
        Group rows by a key column and apply aggregations using running aggregates.

        :param key_col: The column name to group by.
        :param aggregations: A dictionary mapping column names to aggregation functions ('sum', 'avg', 'min', 'max', 'count').
        :return: An iterator yielding one dictionary per group with aggregated results.
        """
        # Dictionary to store running aggregates for each group
        # Structure: group_key -> column -> {sum, count, min, max}
        stats = defaultdict(lambda: defaultdict(lambda: {'sum': 0.0, 'count': 0, 'min': float('inf'), 'max': float('-inf')}))

        for row in self.stream_rows():
            group_key = row[key_col]
            for col, agg in aggregations.items():
                if col not in row: continue
                val = TypeInferrer.infer(row[col])
                if isinstance(val, (int, float)):
                    s = stats[group_key][col]
                    s['sum'] += val
                    s['count'] += 1
                    if val < s['min']: s['min'] = val
                    if val > s['max']: s['max'] = val
                elif agg == 'count':
                    stats[group_key][col]['count'] += 1

        for group_key, columns in stats.items():
            result = {key_col: group_key}
            for col, agg in aggregations.items():
                s = columns[col]
                if agg == 'sum':
                    result[f"sum_{col}"] = s['sum']
                elif agg == 'avg':
                    result[f"avg_{col}"] = s['sum'] / s['count'] if s['count'] > 0 else 0
                elif agg == 'min':
                    result[f"min_{col}"] = s['min'] if s['count'] > 0 else None
                elif agg == 'max':
                    result[f"max_{col}"] = s['max'] if s['count'] > 0 else None
                elif agg == 'count':
                    result[f"count_{col}"] = s['count']
            yield result

    def join(self, other: 'CSVProcessor', on_col: str, how: str = 'inner') -> Iterator[Dict[str, Any]]:
        """
        Join two CSV files based on a common key column using a hash join.

        :param other: Another CSVProcessor instance for the right side of the join.
        :param on_col: The common column name to join on.
        :param how: The join type, either 'inner' or 'left'.
        :return: An iterator yielding combined rows from both CSVs.
        """
        # Load the right-side CSV into memory for joining
        right_rows = list(other.stream_rows())
        right_lookup = defaultdict(list)
        right_cols: Set[str] = set()
        for row in right_rows:
            right_lookup[row[on_col]].append(row)
            right_cols.update(row.keys())

        # Pre-identify columns only in the right side to avoid re-scanning
        right_only_cols = [c for c in right_cols if c != on_col]

        for left_row in self.stream_rows():
            key = left_row[on_col]
            if key in right_lookup:
                for right_row in right_lookup[key]:
                    combined = left_row.copy()
                    for k, v in right_row.items():
                        if k != on_col:
                            # Handle duplicate column names
                            new_k = k
                            suffix = 2
                            while new_k in combined:
                                new_k = f"{k}_{suffix}"
                                suffix += 1
                            combined[new_k] = v
                    yield combined
            elif how == 'left':
                combined = left_row.copy()
                for col in right_only_cols:
                    if col not in combined:
                        combined[col] = None
                yield combined

    def stats(self) -> Dict[str, Any]:
        """
        Calculate summary statistics for each numeric column using running aggregates.

        :return: A dictionary containing summary statistics (count, sum, avg, min, max) for each column.
        """
        # running aggregates per column
        column_stats = defaultdict(lambda: {'sum': 0.0, 'count': 0, 'min': float('inf'), 'max': float('-inf')})
        row_count = 0

        for row in self.stream_rows():
            row_count += 1
            for col, val in row.items():
                typed_val = TypeInferrer.infer(val)
                if isinstance(typed_val, (int, float)):
                    s = column_stats[col]
                    s['sum'] += typed_val
                    s['count'] += 1
                    if typed_val < s['min']: s['min'] = typed_val
                    if typed_val > s['max']: s['max'] = typed_val

        results = {'row_count': row_count, 'columns': {}}
        for col, s in column_stats.items():
            if s['count'] > 0:
                results['columns'][col] = {
                    'count': s['count'],
                    'sum': s['sum'],
                    'avg': s['sum'] / s['count'],
                    'min': s['min'],
                    'max': s['max']
                }
        return results
