import pytest
import os
import shutil
from diffengine.diff import get_diff, get_line_diff, get_inline_diff, get_directory_diff, DiffOp
from diffengine.format import format_unified, format_side_by_side, get_diff_stats

def test_get_diff():
    a = "abc"
    b = "ac"
    diff = get_diff(list(a), list(b))
    # Expect: 'a' EQUAL, 'b' DELETE, 'c' EQUAL
    assert diff == [
        DiffOp(DiffOp.EQUAL, 'a'),
        DiffOp(DiffOp.DELETE, 'b'),
        DiffOp(DiffOp.EQUAL, 'c')
    ]

def test_get_line_diff():
    a = "line1\nline2\n"
    b = "line1\nline3\n"
    diff = get_line_diff(a, b)
    assert len(diff) == 3
    assert diff[0] == DiffOp(DiffOp.EQUAL, "line1\n")
    assert diff[1] == DiffOp(DiffOp.DELETE, "line2\n")
    assert diff[2] == DiffOp(DiffOp.INSERT, "line3\n")

def test_get_inline_diff():
    a = "hello"
    b = "hallo"
    diff = get_inline_diff(a, b)
    # Expected: h, e->a, l, l, o
    assert diff[0] == DiffOp(DiffOp.EQUAL, 'h')
    assert diff[1] == DiffOp(DiffOp.DELETE, 'e')
    assert diff[2] == DiffOp(DiffOp.INSERT, 'a')

def test_get_directory_diff(tmp_path):
    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"
    dir_a.mkdir()
    dir_b.mkdir()

    (dir_a / "same.txt").write_text("same", encoding="utf-8")
    (dir_b / "same.txt").write_text("same", encoding="utf-8")

    (dir_a / "diff.txt").write_text("a", encoding="utf-8")
    (dir_b / "diff.txt").write_text("b", encoding="utf-8")

    (dir_a / "only_a.txt").write_text("only a", encoding="utf-8")
    (dir_b / "only_b.txt").write_text("only b", encoding="utf-8")

    diffs = get_directory_diff(str(dir_a), str(dir_b))

    assert diffs["diff.txt"] == "modified"
    assert diffs["only_a.txt"] == "only in source"
    assert diffs["only_b.txt"] == "only in target"
    assert "same.txt" not in diffs

def test_format_unified():
    a = "line1\n"
    b = "line2\n"
    diff = get_line_diff(a, b)
    unified = format_unified(diff)
    assert "--- source" in unified
    assert "+++ target" in unified
    assert "-line1\n" in unified
    assert "+line2\n" in unified

def test_format_side_by_side():
    a = "line1\n"
    b = "line2\n"
    diff = get_line_diff(a, b)
    sbs = format_side_by_side(diff, width=10)
    # Expected: "line1" | "line2" (approximately)
    assert "line1" in sbs
    assert "line2" in sbs
    assert "|" in sbs

def test_get_diff_stats():
    a = "line1\nline2\n"
    b = "line1\nline3\n"
    diff = get_line_diff(a, b)
    stats = get_diff_stats(diff)
    assert stats["changed"] == 1
    assert stats["added"] == 0
    assert stats["deleted"] == 0

def test_format_unified_no_changes():
    a = "line1\n"
    diff = get_line_diff(a, a)
    unified = format_unified(diff)
    assert "--- source" in unified
    assert "+++ target" in unified
    assert "@@" not in unified

def test_format_side_by_side_ops():
    # Only INSERT
    diff = [DiffOp(DiffOp.INSERT, "new\n")]
    sbs = format_side_by_side(diff)
    assert ">" in sbs

    # Only DELETE
    diff = [DiffOp(DiffOp.DELETE, "old\n")]
    sbs = format_side_by_side(diff)
    assert "<" in sbs

def test_get_diff_stats_ops():
    # Only INSERT
    diff = [DiffOp(DiffOp.INSERT, "new\n")]
    stats = get_diff_stats(diff)
    assert stats["added"] == 1

    # Only DELETE
    diff = [DiffOp(DiffOp.DELETE, "old\n")]
    stats = get_diff_stats(diff)
    assert stats["deleted"] == 1
