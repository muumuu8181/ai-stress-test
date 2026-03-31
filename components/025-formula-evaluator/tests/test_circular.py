import pytest
from src.formula.sheet import SpreadsheetManager
from src.formula.cell import ERROR_CIRC

def test_circular_simple():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")

    # A1 -> A1
    sheet.set_cell_value("A1", "=A1")
    assert sheet.get_cell("A1").value == ERROR_CIRC

def test_circular_indirect():
    mgr = SpreadsheetManager()
    sheet = mgr.get_sheet("Sheet1")

    # A1 -> B1 -> A1
    sheet.set_cell_value("A1", "=B1")
    sheet.set_cell_value("B1", "=A1")

    assert sheet.get_cell("B1").value == ERROR_CIRC
    # Recalculate A1 should also show ERROR_CIRC if properly propagated
    # When B1 was set to =A1, B1 became ERROR_CIRC.
    # What about A1? A1 depends on B1.
    # Recalculation follows order from start_node.
    # If B1 was start_node, B1 is updated to ERROR_CIRC.
    # B1's dependents (A1) should be updated to propagate ERROR_CIRC.

    assert sheet.get_cell("A1").value == ERROR_CIRC

def test_circular_multi_sheet():
    mgr = SpreadsheetManager()
    sheet1 = mgr.get_sheet("Sheet1")
    sheet2 = mgr.add_sheet("Sheet2")

    # Sheet1!A1 -> Sheet2!A1 -> Sheet1!A1
    sheet1.set_cell_value("A1", "=Sheet2!A1")
    sheet2.set_cell_value("A1", "=Sheet1!A1")

    assert sheet2.get_cell("A1").value == ERROR_CIRC
    assert sheet1.get_cell("A1").value == ERROR_CIRC
