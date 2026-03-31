# Spreadsheet Formula Evaluator

A lightweight spreadsheet formula evaluation engine built using only the Python standard library.

## Features

- **Cell References**: Support for `A1`, `B2`, and cross-sheet references like `Sheet2!A1`.
- **Range References**: Support for `A1:B5` and column-wide ranges like `A:A`.
- **Arithmetic Operators**: `+`, `-`, `*`, `/`.
- **Built-in Functions**: `SUM`, `AVG`, `MIN`, `MAX`, `COUNT`, `IF`, `VLOOKUP`.
- **Automatic Recalculation**: Cell updates automatically trigger recalculations of dependent cells.
- **Topological Sorting**: Efficiently resolves cell dependencies.
- **Circular Reference Detection**: Detects and reports `#CIRC!` errors.
- **Error Handling**: Supports common spreadsheet errors: `#REF!`, `#VALUE!`, `#DIV/0!`, `#NAME?`, `#CIRC!`.
- **Cell Formatting**: Basic numeric formatting for display purposes.

## Usage

```python
from formula.sheet import SpreadsheetManager

# Initialize workbook
manager = SpreadsheetManager()
sheet1 = manager.get_sheet("Sheet1")
sheet2 = manager.add_sheet("Sheet2")

# Set values
sheet2.set_cell_value("A1", "100")
sheet1.set_cell_value("A1", "10")
sheet1.set_cell_value("A2", "20")

# Set formulas
sheet1.set_cell_value("B1", "=A1+A2")
sheet1.set_cell_value("B2", "=SUM(A1:A2, Sheet2!A1)")

# Get results
print(sheet1.get_cell("B1").value) # 30.0
print(sheet1.get_cell("B2").value) # 130.0

# Automatic recalculation
sheet1.set_cell_value("A1", "50")
print(sheet1.get_cell("B1").value) # 70.0
print(sheet1.get_cell("B2").value) # 170.0

# Cell formatting
cell = sheet1.get_cell("B1")
print(cell.get_display_value()) # "70"
cell.format_str = ".2f"
print(cell.get_display_value()) # "70.00"
```

## Running Tests

```bash
pytest
```

## Directory Structure

```
src/formula/
  lexer.py     - Formula tokenization
  parser.py    - Formula parsing to AST
  evaluator.py - Formula evaluation logic
  cell.py      - Cell data structure
  sheet.py     - Sheet and Workbook management
  functions.py - Built-in functions implementation
```
