import pytest
from cronparser.formatter import Formatter

def test_formatter_basic():
    assert Formatter.to_human_readable("0 9 * * 1-5") == "平日の9:00"
    assert Formatter.to_human_readable("* * * * *") == "毎分"
    assert Formatter.to_human_readable("0 0 * * *") == "毎日 00:00"

def test_formatter_complex():
    assert Formatter.to_human_readable("30 10 1 * *") == "1日 10:30"
    assert Formatter.to_human_readable("0 12 * 1 0") == "1月 日曜日 12:00"
    assert Formatter.to_human_readable("0 9 * * 1,3,5") == "月・水・金曜日 09:00"

def test_formatter_special():
    assert Formatter.to_human_readable("0 0 L * *") == "月末 00:00"
