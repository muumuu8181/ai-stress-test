import pytest
from src.formula.sheet import SpreadsheetManager
from src.formula.cell import ERROR_REF, ERROR_VALUE, ERROR_DIV0, ERROR_NAME, ERROR_CIRC

def test_sheet_eval_simple():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "10")
    sheet.set_cell_value("A2", "20")
    sheet.set_cell_value("B1", "=A1+A2")
    assert sheet.get_cell("B1").value == 30.0

def test_sheet_eval_update():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "10")
    sheet.set_cell_value("B1", "=A1*2")
    assert sheet.get_cell("B1").value == 20.0

    sheet.set_cell_value("A1", "30")
    assert sheet.get_cell("B1").value == 60.0

def test_sheet_multi_sheet():
    mgr = SpreadsheetManager()
    sheet1 = mgr.get_sheet("Sheet1")
    sheet2 = mgr.add_sheet("Sheet2")

    sheet2.set_cell_value("A1", "100")
    sheet1.set_cell_value("A1", "=Sheet2!A1+5")
    assert sheet1.get_cell("A1").value == 105.0

    sheet2.set_cell_value("A1", "200")
    assert sheet1.get_cell("A1").value == 205.0

def test_sheet_range_eval():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")
    sheet.set_cell_value("A1", "1")
    sheet.set_cell_value("A2", "2")
    sheet.set_cell_value("A3", "3")
    sheet.set_cell_value("B1", "=SUM(A1:A3)")
    assert sheet.get_cell("B1").value == 6.0

    sheet.set_cell_value("A2", "10")
    assert sheet.get_cell("B1").value == 14.0

def test_sheet_eval_errors():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")

    sheet.set_cell_value("A1", "=1/0")
    assert sheet.get_cell("A1").value == ERROR_DIV0

    sheet.set_cell_value("A2", "=UNKNOWN(1)")
    assert sheet.get_cell("A2").value == ERROR_NAME

    sheet.set_cell_value("A3", "=A1+A2")
    # ERROR_DIV0 + ERROR_NAME -> propagate first one usually
    assert sheet.get_cell("A3").value == ERROR_DIV0
