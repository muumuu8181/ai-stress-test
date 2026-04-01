import pytest
import base64
import json
from merkletree.merkle_tree import MerkleTree, StreamingMerkleTree

def test_empty_tree():
    tree = MerkleTree()
    assert tree.root is None
    assert tree.get_stats()["leaf_count"] == 0
    assert tree.get_stats()["depth"] == 0

def test_single_leaf():
    tree = MerkleTree([b"hello"])
    assert tree.root is not None
    assert tree.get_stats()["leaf_count"] == 1
    assert tree.get_stats()["depth"] == 1

    proof = tree.get_proof(0)
    assert MerkleTree.verify_proof(b"hello", proof, tree.root)

def test_two_leaves():
    tree = MerkleTree([b"a", b"b"])
    assert tree.get_stats()["leaf_count"] == 2
    assert tree.get_stats()["depth"] == 2

    assert MerkleTree.verify_proof(b"a", tree.get_proof(0), tree.root)
    assert MerkleTree.verify_proof(b"b", tree.get_proof(1), tree.root)

def test_update_leaf():
    tree = MerkleTree([b"a", b"b", b"c"])
    root_before = tree.root
    tree.update_leaf(1, b"updated")
    assert tree.leaves[1] == b"updated"
    assert tree.root != root_before
    assert MerkleTree.verify_proof(b"updated", tree.get_proof(1), tree.root)

def test_delete_leaf():
    tree = MerkleTree([b"a", b"b", b"c"])
    tree.delete_leaf(1)
    assert tree.leaves == [b"a", b"c"]
    assert tree.get_stats()["leaf_count"] == 2

def test_batch_update():
    tree = MerkleTree([b"a", b"b", b"c", b"d"])
    tree.batch_update({0: b"x", 2: b"z"})
    assert tree.leaves[0] == b"x"
    assert tree.leaves[2] == b"z"
    assert MerkleTree.verify_proof(b"x", tree.get_proof(0), tree.root)
    assert MerkleTree.verify_proof(b"z", tree.get_proof(2), tree.root)

def test_find_differences():
    tree1 = MerkleTree([b"a", b"b", b"c", b"d"])
    tree2 = MerkleTree([b"a", b"X", b"c", b"Y"])
    diffs = tree1.find_differences(tree2)
    assert diffs == [1, 3]

def test_serialization():
    tree = MerkleTree([b"a", b"b"], sort_leaves=True)
    json_str = tree.to_json()
    new_tree = MerkleTree.from_json(json_str)
    assert tree.root == new_tree.root
    assert new_tree.sort_leaves is True

def test_exclusion_proof():
    # Sorted tree: [b"a", b"c", b"e"]
    tree = MerkleTree([b"e", b"a", b"c"], sort_leaves=True)
    root = tree.root

    # Prove b is not in [a, c, e]
    proof = tree.get_exclusion_proof(b"b")
    assert MerkleTree.verify_exclusion_proof(b"b", proof, root)

    # Outside range (lower)
    proof_low = tree.get_exclusion_proof(b"0")
    assert MerkleTree.verify_exclusion_proof(b"0", proof_low, root)

    # Outside range (upper)
    proof_high = tree.get_exclusion_proof(b"z")
    assert MerkleTree.verify_exclusion_proof(b"z", proof_high, root)

def test_streaming_root():
    data = [b"a", b"b", b"c", b"d", b"e", b"f", b"g"]
    stree = StreamingMerkleTree()
    for i in range(len(data)):
        stree.add_leaf(data[i])
        tree = MerkleTree(data[:i+1])
        assert stree.root == tree.root

def test_error_cases():
    tree = MerkleTree([b"a"])
    with pytest.raises(IndexError):
        tree.update_leaf(1, b"fail")
    with pytest.raises(IndexError):
        tree.get_proof(5)

    stree = MerkleTree([b"a"], sort_leaves=False)
    with pytest.raises(ValueError):
        stree.get_exclusion_proof(b"b")

def test_large_tree_stats():
    tree = MerkleTree([bytes([i]) for i in range(100)])
    stats = tree.get_stats()
    assert stats["leaf_count"] == 100
    assert stats["depth"] == 8 # 2^6 < 100 < 2^7 ? No, log2(100) = 6.64 -> 7 levels above leaf?
    # Let's see: 100 -> 50 -> 25 -> 13 -> 7 -> 4 -> 2 -> 1. That's 8 levels total.
    assert stats["depth"] == 8
