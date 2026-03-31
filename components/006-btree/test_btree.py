import pytest
from btree import BTree

def test_btree_init():
    bt = BTree(t=3)
    assert bt.t == 3
    assert bt.root.leaf is True
    assert len(bt.root.keys) == 0

def test_btree_init_error():
    with pytest.raises(ValueError):
        BTree(t=1)

def test_btree_insert_and_search():
    bt = BTree(t=2)
    keys = [10, 20, 5, 6, 12, 30, 7, 17]
    for key in keys:
        bt.insert(key)

    for key in keys:
        res = bt.search(key)
        assert res is not None
        node, idx = res
        assert node.keys[idx] == key

    assert bt.search(100) is None
    assert bt.search(0) is None

def test_btree_duplicates():
    bt = BTree(t=2)
    bt.insert(10)
    bt.insert(10)

    # Search should find at least one 10
    res = bt.search(10)
    assert res is not None
    node, idx = res
    assert node.keys[idx] == 10

    # Iterator should contain both 10s
    assert list(bt) == [10, 10]

def test_btree_delete_leaf():
    bt = BTree(t=3)
    keys = [1, 2, 3, 4, 5]
    for k in keys:
        bt.insert(k)

    bt.delete(3)
    assert bt.search(3) is None
    assert list(bt) == [1, 2, 4, 5]

def test_btree_delete_internal_predecessor():
    bt = BTree(t=2)
    keys = [10, 20, 5, 15, 30]
    for k in keys:
        bt.insert(k)

    # 10 is the root (likely)
    # Let's ensure 10 is internal
    bt.delete(10)
    assert bt.search(10) is None
    assert list(bt) == [5, 15, 20, 30]

def test_btree_delete_internal_successor():
    bt = BTree(t=2)
    keys = [10, 20, 5, 15, 30]
    for k in keys:
        bt.insert(k)

    # Let's manipulate to ensure successor branch is used
    # But for t=2, it's easier to just test if it works.
    bt.delete(20)
    assert bt.search(20) is None
    assert list(bt) == [5, 10, 15, 30]

def test_btree_delete_merge():
    bt = BTree(t=2)
    # Force merge by deleting from nodes with t-1 keys
    keys = [10, 20, 30]
    for k in keys:
        bt.insert(k)

    # root [20], kids [10], [30]
    bt.delete(20)
    assert bt.search(20) is None
    assert list(bt) == [10, 30]

def test_btree_range_query():
    bt = BTree(t=3)
    keys = list(range(100))
    for k in keys:
        bt.insert(k)

    assert bt.range_query(20, 30) == list(range(20, 31))
    assert bt.range_query(-10, 5) == list(range(6))
    assert bt.range_query(95, 110) == list(range(95, 100))
    assert bt.range_query(50, 50) == [50]
    assert bt.range_query(101, 110) == []

def test_btree_iterator():
    bt = BTree(t=2)
    keys = [5, 3, 7, 2, 4, 6, 8]
    for k in keys:
        bt.insert(k)

    assert list(bt) == sorted(keys)

def test_btree_serialization():
    bt = BTree(t=3)
    keys = [10, 20, 5, 30, 15]
    for k in keys:
        bt.insert(k)

    json_str = bt.to_json()
    new_bt = BTree.from_json(json_str)

    assert new_bt.t == 3
    assert list(new_bt) == sorted(keys)
    assert new_bt.search(20) is not None

def test_btree_dump():
    bt = BTree(t=2)
    bt.insert(10)
    bt.insert(20)
    dump_str = bt.dump()
    assert "Level 0" in dump_str
    assert "10" in dump_str
    assert "20" in dump_str

def test_btree_large_data():
    import random
    bt = BTree(t=10)
    data = list(range(10000))
    random.shuffle(data)

    # Insertion
    for k in data:
        bt.insert(k)

    # Search all
    random.shuffle(data)
    for k in data:
        assert bt.search(k) is not None

    # Deletion (part of it)
    to_delete = data[:1000]
    for k in to_delete:
        bt.delete(k)
        assert bt.search(k) is None

    remaining = sorted(data[1000:])
    assert list(bt) == remaining

def test_btree_edge_cases():
    bt = BTree(t=2)
    # Search/Delete from empty tree
    assert bt.search(10) is None
    bt.delete(10) # Should not raise error
    assert list(bt) == []

    # Range query empty tree
    assert bt.range_query(0, 100) == []

    # Single element
    bt.insert(5)
    assert bt.search(5) is not None
    bt.delete(5)
    assert bt.search(5) is None
    assert list(bt) == []

def test_btree_non_comparable_keys():
    bt = BTree(t=2)
    bt.insert(10)
    with pytest.raises(TypeError):
        bt.insert("string")
