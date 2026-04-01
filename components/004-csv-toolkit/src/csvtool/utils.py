import csv
import sys
import os
from typing import Optional, List, Any, Dict, Iterator, TextIO, Union

def detect_delimiter(filepath: Optional[str], sample_size: int = 4096) -> str:
    """
    Detect the delimiter (e.g., CSV, TSV) using csv.Sniffer.

    :param filepath: Path to the CSV file or '-' for stdin.
    :param sample_size: The number of bytes to read for sniffing.
    :return: The detected delimiter character (defaults to ',').
    """
    if not filepath or filepath == '-' or not os.path.exists(filepath):
        return ','
    with open(filepath, 'r', encoding='utf-8') as f:
        sample = f.read(sample_size)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[',', '\t', ';', '|'])
            return dialect.delimiter
        except csv.Error:
            return ','

class StreamHandler:
    """A context manager to handle both files and standard streams."""

    def __init__(self, filepath: Optional[Union[str, TextIO]] = None, mode: str = 'r'):
        """
        Initialize the stream handler.

        :param filepath: Path to a file, '-' for stdin/stdout, or an existing stream.
        :param mode: The mode to open the file (e.g., 'r', 'w').
        """
        self.filepath = filepath
        self.mode = mode
        self.stream: Optional[TextIO] = None
        self.is_std = False

    def __enter__(self) -> TextIO:
        if not self.filepath or self.filepath == '-':
            self.stream = sys.stdin if 'r' in self.mode else sys.stdout
            self.is_std = True
        elif hasattr(self.filepath, 'read') or hasattr(self.filepath, 'write'):
            self.stream = self.filepath # type: ignore
            self.is_std = True
        else:
            self.stream = open(self.filepath, self.mode, encoding='utf-8', newline='' if 'w' in self.mode else None) # type: ignore
        return self.stream # type: ignore

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stream and not self.is_std:
            self.stream.close()

def get_input_stream(filepath: Optional[Union[str, TextIO]] = None) -> TextIO:
    """
    Return the input file object or sys.stdin if no filepath is provided.

    :param filepath: Path to a file, '-' for stdin, or an existing stream.
    :return: An open file object or sys.stdin.
    """
    if filepath and filepath != '-':
        if hasattr(filepath, 'read'): return filepath # type: ignore
        return open(filepath, 'r', encoding='utf-8') # type: ignore
    return sys.stdin

def get_output_stream(filepath: Optional[Union[str, TextIO]] = None) -> TextIO:
    """
    Return the output file object or sys.stdout if no filepath is provided.

    :param filepath: Path to a file, '-' for stdout, or an existing stream.
    :return: An open file object or sys.stdout.
    """
    if filepath and filepath != '-':
        if hasattr(filepath, 'write'): return filepath # type: ignore
        return open(filepath, 'w', encoding='utf-8', newline='') # type: ignore
    return sys.stdout

def write_rows(rows: Iterator[Dict[str, Any]], filepath: Optional[Union[str, TextIO]] = None,
               delimiter: str = ',', fieldnames: Optional[List[str]] = None):
    """
    Stream rows to the specified output filepath or sys.stdout.

    :param rows: An iterator yielding dictionaries representing rows.
    :param filepath: Path to the output file or '-' for stdout.
    :param delimiter: The CSV delimiter to use.
    :param fieldnames: List of column names in the output. If not provided, it's inferred from the first row.
    """
    with StreamHandler(filepath, 'w') as f:
        first_row = None
        if not fieldnames:
            try:
                first_row = next(rows)
                fieldnames = list(first_row.keys())
            except StopIteration:
                return

        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        if first_row:
            writer.writerow(first_row)
        for row in rows:
            writer.writerow(row)
