import pytest
from consistent_hash.hasher import ConsistentHasher

def test_empty_input_key():
    hasher = ConsistentHasher()
    hasher.add_node("node1")
    # Empty string is a valid key in Python and hasher
    assert len(hasher.get_nodes("")) == 1

def test_null_input_key():
    hasher = ConsistentHasher()
    hasher.add_node("node1")
    # Python's None can't be hashed by our _hash method (key.encode("utf-8"))
    with pytest.raises(AttributeError):
        hasher.get_nodes(None)

def test_invalid_vnodes_count():
    # vnodes=0 is not very useful but doesn't raise error on init.
    # However, adding a node with weight 1 will still result in 0 vnodes in the ring.
    hasher = ConsistentHasher(vnodes=0)
    hasher.add_node("node1")
    assert len(hasher.ring) == 0
    with pytest.raises(ValueError, match="No nodes in the ring"):
        hasher.get_nodes("key")

def test_large_number_of_nodes():
    hasher = ConsistentHasher(vnodes=10)
    for i in range(100):
        hasher.add_node(f"node_{i}")
    assert len(hasher.ring) == 1000
    assert len(hasher.get_nodes("key", replicas=5)) == 5

def test_single_vnode_ring():
    hasher = ConsistentHasher(vnodes=1)
    hasher.add_node("node1")
    assert len(hasher.ring) == 1
    assert hasher.get_nodes("key1") == ["node1"]
    assert hasher.get_nodes("key2") == ["node1"]

def test_complex_node_names():
    hasher = ConsistentHasher()
    hasher.add_node("127.0.0.1:8080")
    hasher.add_node("server-A")
    hasher.add_node("🚀")

    nodes = hasher.get_nodes("key", replicas=3)
    assert len(nodes) == 3
    assert "🚀" in nodes
