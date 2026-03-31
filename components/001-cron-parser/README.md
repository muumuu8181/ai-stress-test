# Cron Expression Parser & Validator

A pure Python cron expression parser and validator with no external dependencies.

## Features

- Parse cron expressions (5 fields: Minute, Hour, Day of Month, Month, Day of Week).
- Calculate the next execution time.
- Validate cron expressions (out-of-range detection, invalid formats).
- Support for special characters: `*`, `?`, `-`, `/`, `,`, `L`, `W`, `#`.
- Human-readable Japanese format conversion.

## Installation

No external libraries are required. Simply include the `cronparser` directory in your project.

## Usage

### Parsing and Validation

```python
from cronparser.parser import Parser

try:
    cron = Parser.parse("0 9 * * 1-5")
    print(cron)
except ValueError as e:
    print(f"Invalid cron expression: {e}")
```

### Calculating Next Execution Time

```python
from datetime import datetime
from cronparser.calculator import Calculator

base_time = datetime.now()
next_run = Calculator.get_next_run_time("0 9 * * 1-5", base_time)
print(f"Next run time: {next_run}")
```

### Human-Readable Format

```python
from cronparser.formatter import Formatter

readable = Formatter.to_human_readable("0 9 * * 1-5")
print(readable) # Output: 平日の9:00
```

## Special Characters Supported

- `*`: All values.
- `?`: No specific value (treated as `*`).
- `-`: Range (e.g., `1-5`).
- `/`: Increments (e.g., `*/15`).
- `,`: Multiple values (e.g., `1,15`).
- `L`: Last (e.g., `L` in DOM for last day of month, `5L` in DOW for last Friday).
- `W`: Weekday (e.g., `15W` for nearest weekday to the 15th).
- `#`: N-th day of week (e.g., `5#2` for the second Friday).

## Testing

Run tests using pytest:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest
```
