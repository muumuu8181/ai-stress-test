import pytest
from src.formula.sheet import SpreadsheetManager
from src.formula.cell import ERROR_REF, ERROR_VALUE, ERROR_DIV0, ERROR_NAME, ERROR_CIRC

def test_empty_formula():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "=")
    assert sheet.get_cell("A1").value == "#ERROR!"

def test_invalid_formula():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "=1+(2*")
    assert sheet.get_cell("A1").value == "#ERROR!"

def test_non_existent_sheet():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "=Other!A1")
    assert sheet.get_cell("A1").value == ERROR_REF

def test_formatting():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")

    cell = sheet.get_cell("A1")
    cell.set_value("10.5")
    assert cell.get_display_value() == "10.50"

    cell.set_value("10")
    assert cell.get_display_value() == "10"

    cell.format_str = ".3f"
    cell.set_value("10.5")
    assert cell.get_display_value() == "10.500"

def test_vlookup_flat_range():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "Apple")
    sheet.set_cell_value("B1", "Red")
    sheet.set_cell_value("A2", "Banana")
    sheet.set_cell_value("B2", "Yellow")
    sheet.set_cell_value("C1", "=VLOOKUP(\"Banana\", A1:B2, 2)")
    assert sheet.get_cell("C1").value == "Yellow"

def test_quoted_sheet_name():
    mgr = SpreadsheetManager()
    sheet = mgr.add_sheet("My Sheet")
    sheet.set_cell_value("A1", "42")
    sheet1 = mgr.get_sheet("Sheet1")
    sheet1.set_cell_value("A1", "='My Sheet'!A1")
    assert sheet1.get_cell("A1").value == 42.0

def test_escaped_quotes():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "=\"He said \"\"Hello\"\"\"")
    assert sheet.get_cell("A1").value == "He said \"Hello\""

def test_avg_div0():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "=AVG()")
    assert sheet.get_cell("A1").value == ERROR_DIV0
