import pytest
from diffengine.diff import get_diff, DiffOp

def test_lcs_large():
    a = list(range(100))
    b = list(range(50, 150))
    diff = get_diff(a, b)
    # 0..49 DELETED, 50..99 EQUAL, 100..149 INSERTED
    stats = {"added": 0, "deleted": 0, "equal": 0}
    for op in diff:
        if op.op == DiffOp.DELETE: stats["deleted"] += 1
        elif op.op == DiffOp.INSERT: stats["added"] += 1
        else: stats["equal"] += 1
    assert stats["deleted"] == 50
    assert stats["equal"] == 50
    assert stats["added"] == 50

def test_diff_repeated_elements():
    a = ["a", "a", "a"]
    b = ["a", "a"]
    diff = get_diff(a, b)
    # Expect 2 EQUAL, 1 DELETE
    assert len([op for op in diff if op.op == DiffOp.EQUAL]) == 2
    assert len([op for op in diff if op.op == DiffOp.DELETE]) == 1

def test_diff_null_values():
    a = [None, 1, 2]
    b = [1, 2, None]
    diff = get_diff(a, b)
    assert diff[0] == DiffOp(DiffOp.DELETE, None)
    assert diff[-1] == DiffOp(DiffOp.INSERT, None)
