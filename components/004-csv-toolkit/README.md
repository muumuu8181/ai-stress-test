# CSV Toolkit

A high-performance CSV processing toolkit built with only the Python standard library.

## Features

- **CSV/TSV reading/writing** with automatic delimiter detection.
- **Column selection, filtering, and sorting**.
- **Aggregations**: `groupby` with `sum`, `avg`, `min`, `max`, and `count`.
- **Joins**: INNER and LEFT JOIN between two CSV files.
- **Type Inference**: Automatic detection of numbers, dates, and booleans.
- **Schema Validation**: Define and validate schemas for CSV data.
- **Streaming Support**: Efficiently process large files.

## Installation

This toolkit is part of the components library. No external dependencies are required.

## CLI Usage

### Column Selection
```bash
python -m csvtool select --columns name,age data.csv
```

### Filtering
```bash
python -m csvtool filter --where "age > 20" data.csv
```

### Join
```bash
python -m csvtool join --on id left.csv right.csv
```

### Statistics
```bash
python -m csvtool stats data.csv
```

## Programmatic Usage

```python
from csvtool.core import CSVProcessor

processor = CSVProcessor("data.csv")
for row in processor.filter(lambda r: int(r['age']) > 20).select(['name', 'age']):
    print(row)
```
