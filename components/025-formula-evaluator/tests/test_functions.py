import pytest
from src.formula.functions import sum_func, avg_func, min_func, max_func, count_func, if_func, vlookup_func
from src.formula.cell import ERROR_DIV0

def test_sum():
    assert sum_func([1, 2, 3]) == 6.0
    assert sum_func([[1, 2], 3]) == 6.0
    assert sum_func([1, "2", "abc"]) == 3.0

def test_avg():
    assert avg_func([1, 2, 3]) == 2.0
    assert avg_func([1, 2, 3, 4]) == 2.5
    assert avg_func([]) == ERROR_DIV0

def test_min_max():
    assert min_func([1, 5, -2, 10]) == -2.0
    assert max_func([1, 5, -2, 10]) == 10.0

def test_count():
    assert count_func([1, 2, "a", 3.5]) == 3.0
    assert count_func([[1, 2], "b"]) == 2.0

def test_if():
    assert if_func([True, "Yes", "No"]) == "Yes"
    assert if_func([False, "Yes", "No"]) == "No"
    assert if_func([1, "Yes", "No"]) == "Yes"
    assert if_func([0, "Yes", "No"]) == "No"

def test_vlookup():
    table = [
        ["A", 10],
        ["B", 20],
        ["C", 30]
    ]
    assert vlookup_func(["B", table, 2]) == 20
    assert vlookup_func(["D", table, 2]) == "#N/A"
    assert vlookup_func(["A", table, 3]) == "#REF!"
