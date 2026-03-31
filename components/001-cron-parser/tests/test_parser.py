import pytest
from cronparser.lexer import Lexer
from cronparser.parser import Parser, CronExpression

def test_lexer_success():
    lexer = Lexer("0 9 * * 1-5")
    tokens = lexer.tokenize()
    assert tokens == ["0", "9", "*", "*", "1-5"]

def test_lexer_invalid_fields():
    lexer = Lexer("0 9 * *")
    with pytest.raises(ValueError, match="Expected 5 fields"):
        lexer.tokenize()

def test_lexer_empty():
    lexer = Lexer("")
    with pytest.raises(ValueError, match="cannot be empty"):
        lexer.tokenize()

def test_parser_basic():
    cron = Parser.parse("0 9 * * 1-5")
    assert cron.minute.values == {0}
    assert cron.hour.values == {9}
    assert cron.day_of_month.values == set(range(1, 32))
    assert cron.month.values == set(range(1, 13))
    assert cron.day_of_week.values == {1, 2, 3, 4, 5}

def test_parser_complex():
    cron = Parser.parse("*/15 0-23/2 1,15 * ?")
    assert cron.minute.values == {0, 15, 30, 45}
    assert cron.hour.values == {0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22}
    assert cron.day_of_month.values == {1, 15}
    assert cron.day_of_week.values == set(range(0, 7))

def test_parser_special_chars():
    cron_l = Parser.parse("0 0 L * *")
    assert cron_l.day_of_month.l_flag is True
    assert cron_l.day_of_month.special_char == "L"

    cron_w = Parser.parse("0 0 15W * *")
    assert cron_w.day_of_month.w_flag == 15
    assert cron_w.day_of_month.special_char == "15W"

    cron_hash = Parser.parse("0 0 * * 5#2")
    assert cron_hash.day_of_week.hash_val == (5, 2)
    assert cron_hash.day_of_week.special_char == "5#2"

def test_parser_out_of_range():
    with pytest.raises(ValueError, match="out of range"):
        Parser.parse("60 * * * *")
    with pytest.raises(ValueError, match="out of range"):
        Parser.parse("* 24 * * *")
    with pytest.raises(ValueError, match="out of range"):
        Parser.parse("* * 32 * *")
    with pytest.raises(ValueError, match="out of range"):
        Parser.parse("* * * 13 *")
    with pytest.raises(ValueError, match="out of range"):
        Parser.parse("* * * * 7")

def test_parser_invalid_format():
    with pytest.raises(ValueError, match="invalid for"):
        Parser.parse("* * 10-5 * *")
    with pytest.raises(ValueError, match="invalid literal for int"):
        Parser.parse("a * * * *")
