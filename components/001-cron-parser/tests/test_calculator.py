import pytest
from datetime import datetime
from cronparser.calculator import Calculator

def test_calculator_basic():
    base = datetime(2024, 1, 1, 0, 0)
    # 0 9 * * 1-5 (Mon-Fri 9:00)
    # 2024-01-01 is Monday
    next_run = Calculator.get_next_run_time("0 9 * * 1-5", base)
    assert next_run == datetime(2024, 1, 1, 9, 0)

    base2 = datetime(2024, 1, 1, 9, 0)
    next_run2 = Calculator.get_next_run_time("0 9 * * 1-5", base2)
    assert next_run2 == datetime(2024, 1, 2, 9, 0)

def test_calculator_every_minute():
    base = datetime(2024, 1, 1, 0, 0)
    next_run = Calculator.get_next_run_time("* * * * *", base)
    assert next_run == datetime(2024, 1, 1, 0, 1)

def test_calculator_month_skip():
    base = datetime(2024, 1, 1, 0, 0)
    # Next Jan 1st at 1:00
    next_run = Calculator.get_next_run_time("0 1 1 1 *", base)
    assert next_run == datetime(2024, 1, 1, 1, 0)

    # Next Feb 1st
    next_run_feb = Calculator.get_next_run_time("0 1 1 2 *", base)
    assert next_run_feb == datetime(2024, 2, 1, 1, 0)

def test_calculator_l_character():
    # Last day of month
    base = datetime(2024, 2, 1, 0, 0)
    # 2024 is leap year, Feb has 29 days
    next_run = Calculator.get_next_run_time("0 0 L * *", base)
    assert next_run == datetime(2024, 2, 29, 0, 0)

def test_calculator_w_character():
    # Nearest weekday to 15th
    # 2024-06-15 is Saturday
    base = datetime(2024, 6, 1, 0, 0)
    next_run = Calculator.get_next_run_time("0 0 15W * *", base)
    # Should be Friday June 14th
    assert next_run == datetime(2024, 6, 14, 0, 0)

def test_calculator_hash_character():
    # Second Friday of the month (Friday=5, nth=2)
    # 2024-01-01 is Monday
    # Fridays: 5th, 12th, 19th, 26th
    base = datetime(2024, 1, 1, 0, 0)
    next_run = Calculator.get_next_run_time("0 0 * * 5#2", base)
    assert next_run == datetime(2024, 1, 12, 0, 0)

def test_calculator_dow_l_character():
    # Last Friday of Jan 2024
    # 2024-01-26 is the last Friday
    base = datetime(2024, 1, 1, 0, 0)
    next_run = Calculator.get_next_run_time("0 0 * * 5L", base)
    assert next_run == datetime(2024, 1, 26, 0, 0)

    # Bare "L" in DOW field
    next_run_l = Calculator.get_next_run_time("0 0 * * L", base)
    # Bare L in DOW means last Saturday of month.
    # Jan 27 is the last Saturday.
    assert next_run_l == datetime(2024, 1, 27, 0, 0)

def test_calculator_no_match():
    base = datetime(2024, 1, 1, 0, 0)
    # Impossible date Feb 30th
    with pytest.raises(ValueError, match="Could not find next execution time"):
        Calculator.get_next_run_time("0 0 30 2 *", base)
