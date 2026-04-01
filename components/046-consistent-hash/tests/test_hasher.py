import pytest
from consistent_hash.hasher import ConsistentHasher

def test_init_success():
    hasher = ConsistentHasher(hash_algorithm="md5", vnodes=50)
    assert hasher.hash_algorithm == "md5"
    assert hasher.vnodes_base == 50
    assert len(hasher.nodes) == 0
    assert len(hasher.ring) == 0

def test_init_unsupported_algorithm():
    with pytest.raises(ValueError, match="Unsupported hash algorithm"):
        ConsistentHasher(hash_algorithm="sha512")

def test_add_node_success():
    hasher = ConsistentHasher(vnodes=10)
    hasher.add_node("node1", weight=1)
    assert "node1" in hasher.nodes
    assert hasher.nodes["node1"] == 1
    assert len(hasher.ring) == 10
    assert len(hasher.vnode_to_node) == 10

def test_add_duplicate_node():
    hasher = ConsistentHasher()
    hasher.add_node("node1")
    with pytest.raises(ValueError, match="Node already exists"):
        hasher.add_node("node1")

def test_add_node_invalid_weight():
    hasher = ConsistentHasher()
    with pytest.raises(ValueError, match="Weight must be greater than zero"):
        hasher.add_node("node1", weight=0)
    with pytest.raises(ValueError, match="Weight must be greater than zero"):
        hasher.add_node("node1", weight=-1)

def test_remove_node_success():
    hasher = ConsistentHasher(vnodes=10)
    hasher.add_node("node1", weight=2)
    assert len(hasher.ring) == 20
    hasher.remove_node("node1")
    assert "node1" not in hasher.nodes
    assert len(hasher.ring) == 0
    assert len(hasher.vnode_to_node) == 0

def test_remove_nonexistent_node():
    hasher = ConsistentHasher()
    with pytest.raises(ValueError, match="Node does not exist"):
        hasher.remove_node("node1")

def test_get_nodes_success():
    hasher = ConsistentHasher(vnodes=10)
    hasher.add_node("node1")
    hasher.add_node("node2")

    nodes = hasher.get_nodes("some_key")
    assert len(nodes) == 1
    assert nodes[0] in ["node1", "node2"]

def test_get_nodes_replicas():
    hasher = ConsistentHasher(vnodes=10)
    hasher.add_node("node1")
    hasher.add_node("node2")
    hasher.add_node("node3")

    nodes = hasher.get_nodes("some_key", replicas=2)
    assert len(nodes) == 2
    assert len(set(nodes)) == 2
    for node in nodes:
        assert node in ["node1", "node2", "node3"]

def test_get_nodes_empty_ring():
    hasher = ConsistentHasher()
    with pytest.raises(ValueError, match="No nodes in the ring"):
        hasher.get_nodes("key")

def test_get_nodes_too_many_replicas():
    hasher = ConsistentHasher()
    hasher.add_node("node1")
    with pytest.raises(ValueError, match="Replica count 2 exceeds number of nodes 1"):
        hasher.get_nodes("key", replicas=2)

def test_serialization():
    hasher = ConsistentHasher(hash_algorithm="sha1", vnodes=20)
    hasher.add_node("node1", weight=1)
    hasher.add_node("node2", weight=2)

    data = hasher.to_dict()
    assert data["hash_algorithm"] == "sha1"
    assert data["vnodes_base"] == 20
    assert data["nodes"] == {"node1": 1, "node2": 2}

    hasher2 = ConsistentHasher.from_dict(data)
    assert hasher2.hash_algorithm == "sha1"
    assert hasher2.vnodes_base == 20
    assert hasher2.nodes == {"node1": 1, "node2": 2}
    assert len(hasher2.ring) == 60

def test_get_stats():
    hasher = ConsistentHasher(vnodes=10)
    hasher.add_node("node1", weight=1)
    hasher.add_node("node2", weight=2)

    stats = hasher.get_stats()
    assert stats["total_nodes"] == 2
    assert stats["total_vnodes"] == 30
    assert stats["vnode_counts"] == {"node1": 10, "node2": 20}
    assert "coverage_percentage" in stats
    assert sum(stats["coverage_percentage"].values()) == pytest.approx(100.0)

def test_get_stats_empty():
    hasher = ConsistentHasher()
    stats = hasher.get_stats()
    assert stats["total_nodes"] == 0
    assert stats["total_vnodes"] == 0
    assert stats["distribution"] == {}
