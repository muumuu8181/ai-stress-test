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

def test_merge_3way_modify_delete_conflict():
    # As requested in the review feedback
    ancestor = "line1\nline2\nline3\n"
    current = "line1\nmodified2\nline3\n"
    other = "line1\nline3\n"

    # Side A modifies line 2, Side B deletes line 2.
    merged, conflict = merge_3way(ancestor, current, other)
    # Ideally, this should be a conflict.
    # In my current implementation, it's a conflict because state_b[1] has ins and kept_b=False,
    # and state_o[1] has no ins and kept_o=False.
    # Actually, the insertions logic: ins_b != ins_o (one is ['modified2\n'], other is []).
    # So it flags a conflict in insertions.
    assert conflict
    assert "<<<<<<< CURRENT" in merged
    assert "modified2" in merged
