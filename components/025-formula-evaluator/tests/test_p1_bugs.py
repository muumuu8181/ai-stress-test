import pytest
from src.formula.sheet import SpreadsheetManager
from src.formula.cell import ERROR_REF, ERROR_VALUE, ERROR_DIV0, ERROR_NAME, ERROR_CIRC, ERROR_NA

def test_trailing_tokens():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "=1+2 3")
    assert sheet.get_cell("A1").value == "#ERROR!"

def test_if_error_propagation():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "=IF(1/0, 1, 2)")
    assert sheet.get_cell("A1").value == ERROR_DIV0

def test_aggregate_error_propagation():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "=1/0")
    sheet.set_cell_value("A2", "10")
    sheet.set_cell_value("B1", "=SUM(A1, A2)")
    assert sheet.get_cell("B1").value == ERROR_DIV0

    sheet.set_cell_value("B2", "=AVG(A1:A2)")
    assert sheet.get_cell("B2").value == ERROR_DIV0

def test_vlookup_improved():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "Apple")
    sheet.set_cell_value("B1", "Red")

    # Case-insensitive
    sheet.set_cell_value("C1", "=VLOOKUP(\"apple\", A1:B1, 2)")
    assert sheet.get_cell("C1").value == "Red"

    # Early col_index validation
    sheet.set_cell_value("C2", "=VLOOKUP(\"Banana\", A1:B1, 3)")
    assert sheet.get_cell("C2").value == ERROR_REF

    # Error propagation
    sheet.set_cell_value("A2", "=1/0")
    sheet.set_cell_value("C3", "=VLOOKUP(A2, A1:B1, 2)")
    assert sheet.get_cell("C3").value == ERROR_DIV0

def test_dynamic_column_dependency():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")

    # B1 depends on all of column A
    sheet.set_cell_value("B1", "=SUM(A:A)")
    assert sheet.get_cell("B1").value == 0

    # Add value to A10 (previously didn't exist)
    sheet.set_cell_value("A10", "100")
    # B1 should have recalculated
    assert sheet.get_cell("B1").value == 100.0

    # Add value to A5
    sheet.set_cell_value("A5", "50")
    assert sheet.get_cell("B1").value == 150.0

def test_na_propagation():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "=VLOOKUP(\"Missing\", B1:C1, 1)")
    assert sheet.get_cell("A1").value == ERROR_NA

    sheet.set_cell_value("A2", "=A1+10")
    assert sheet.get_cell("A2").value == ERROR_NA

def test_complex_range_dependency():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "10")
    sheet.set_cell_value("B1", "=SUM(A1:A5)")
    sheet.set_cell_value("C1", "=B1*2")

    assert sheet.get_cell("C1").value == 20.0

    # Update A3 (inside the range A1:A5)
    sheet.set_cell_value("A3", "20")
    assert sheet.get_cell("B1").value == 30.0
    assert sheet.get_cell("C1").value == 60.0
