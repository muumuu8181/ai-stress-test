import pytest
from cronparser.parser import Parser
from cronparser.calculator import Calculator
from datetime import datetime

def test_edge_case_empty():
    with pytest.raises(ValueError):
        Parser.parse("")

def test_edge_case_none():
    with pytest.raises(AttributeError):
        Parser.parse(None)

def test_edge_case_excessive_spaces():
    cron = Parser.parse("  0   9   *   *   1-5  ")
    assert cron.minute.values == {0}
    assert cron.hour.values == {9}

def test_edge_case_leap_year():
    # Feb 29th on Leap Year
    base = datetime(2024, 1, 1, 0, 0)
    next_run = Calculator.get_next_run_time("0 0 29 2 *", base)
    assert next_run == datetime(2024, 2, 29, 0, 0)

    # Non-Leap Year (2025)
    base_2025 = datetime(2025, 1, 1, 0, 0)
    next_run_2028 = Calculator.get_next_run_time("0 0 29 2 *", base_2025)
    assert next_run_2028 == datetime(2028, 2, 29, 0, 0)

def test_edge_case_l_dow_variations():
    # 6L is last Saturday
    base = datetime(2024, 1, 1, 0, 0)
    next_run = Calculator.get_next_run_time("0 0 * * 6L", base)
    assert next_run == datetime(2024, 1, 27, 0, 0)

def test_edge_case_w_at_end_of_month():
    # 31W in June (30 days)
    # June 30, 2024 is Sunday.
    # Closest weekday to 31st (which is clamped to 30th)
    # Closest weekday to Sunday 30th is Friday 28th? No, Monday July 1st?
    # Usually it must stay in the same month.
    # My implementation says: if Sun, and target < last_day, target + 1. Else target - 2.
    # For June 30 (Sun): target=30, last_day=30. So 30-2 = 28 (Fri).
    base = datetime(2024, 6, 1, 0, 0)
    next_run = Calculator.get_next_run_time("0 0 31W * *", base)
    assert next_run == datetime(2024, 6, 28, 0, 0)
