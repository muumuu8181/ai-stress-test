import pytest
from diffengine.merge import merge_3way

def test_merge_3way_no_conflict():
    ancestor = "line1\nline2\n"
    current = "line1\nline2\nline3\n"
    other = "line1\nline2\n"

    merged, conflict = merge_3way(ancestor, current, other)
    assert not conflict
    assert merged == current

def test_merge_3way_conflict():
    ancestor = "line1\nline2\n"
    current = "line1\nmodified1\n"
    other = "line1\nmodified2\n"

    # In my current implementation, "modified1" is a DELETE of "line2" and an INSERT of "modified1".
    # Same for "modified2".
    # So it should detect a conflict in insertions before index 1 (or 2).

    merged, conflict = merge_3way(ancestor, current, other)
    assert conflict
    assert "<<<<<<< CURRENT" in merged
    assert "modified1" in merged
    assert "modified2" in merged

def test_merge_3way_non_overlapping():
    ancestor = "line1\nline2\nline3\nline4\n"
    current = "line1_mod\nline2\nline3\nline4\n"
    other = "line1\nline2\nline3\nline4_mod\n"

    merged, conflict = merge_3way(ancestor, current, other)
    assert not conflict
    assert "line1_mod" in merged
    assert "line4_mod" in merged
    assert "line2" in merged
    assert "line3" in merged

def test_merge_3way_same_change():
    ancestor = "line1\nline2\n"
    current = "line1\nmodified\n"
    other = "line1\nmodified\n"

    merged, conflict = merge_3way(ancestor, current, other)
    assert not conflict
    assert merged == current
