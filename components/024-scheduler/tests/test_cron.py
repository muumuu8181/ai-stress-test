import pytest
import datetime
from scheduler.cron import CronParser

def test_cron_parsing_asterisk():
    cp = CronParser("* * * * *")
    assert len(cp.minutes) == 60
    assert len(cp.hours) == 24
    assert len(cp.days) == 31
    assert len(cp.months) == 12
    assert len(cp.weekdays) == 7

def test_cron_parsing_fixed_values():
    cp = CronParser("15 10 1 1 1")
    assert cp.minutes == {15}
    assert cp.hours == {10}
    assert cp.days == {1}
    assert cp.months == {1}
    assert cp.weekdays == {0}  # Monday in Python is 0, 1 in Cron is Monday

def test_cron_parsing_ranges():
    cp = CronParser("0-5 * * * *")
    assert cp.minutes == {0, 1, 2, 3, 4, 5}

def test_cron_parsing_intervals():
    cp = CronParser("*/15 * * * *")
    assert cp.minutes == {0, 15, 30, 45}

def test_cron_parsing_mixed():
    cp = CronParser("0,15,30-35/2 * * * *")
    # 0, 15, 30, 32, 34
    assert cp.minutes == {0, 15, 30, 32, 34}

def test_cron_next_occurrence():
    cp = CronParser("0 10 * * *")  # Every day at 10:00
    start = datetime.datetime(2023, 1, 1, 9, 0)
    next_run = cp.get_next_occurrence(start)
    assert next_run == datetime.datetime(2023, 1, 1, 10, 0)

    start = datetime.datetime(2023, 1, 1, 11, 0)
    next_run = cp.get_next_occurrence(start)
    assert next_run == datetime.datetime(2023, 1, 2, 10, 0)

def test_cron_weekday_sunday():
    # Cron 0 is Sunday, 7 is also Sunday
    cp0 = CronParser("* * * * 0")
    assert cp0.weekdays == {6} # Sunday in Python

    cp7 = CronParser("* * * * 7")
    assert cp7.weekdays == {6}

def test_invalid_cron():
    with pytest.raises(ValueError):
        CronParser("* * * *")  # Too few parts
    with pytest.raises(ValueError):
        CronParser("60 * * * *")  # Minute out of range
