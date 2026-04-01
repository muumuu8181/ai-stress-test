import pytest
from consistent_hash.hasher import ConsistentHasher

def test_minimal_redistribution_addition():
    hasher = ConsistentHasher(vnodes=100)
    hasher.add_node("node1")
    hasher.add_node("node2")
    hasher.add_node("node3")

    # Sample 1000 keys
    keys = [f"key_{i}" for i in range(1000)]
    initial_mapping = {key: hasher.get_nodes(key)[0] for key in keys}

    # Add a new node
    hasher.add_node("node4")
    new_mapping = {key: hasher.get_nodes(key)[0] for key in keys}

    # Keys should only move to node4, and not between node1, node2, node3
    moved_keys = 0
    incorrect_moves = 0
    for key in keys:
        if initial_mapping[key] != new_mapping[key]:
            moved_keys += 1
            if new_mapping[key] != "node4":
                incorrect_moves += 1

    # Ideally, 1/4 of keys move to node4
    assert 200 <= moved_keys <= 300
    assert incorrect_moves == 0

def test_minimal_redistribution_removal():
    hasher = ConsistentHasher(vnodes=100)
    hasher.add_node("node1")
    hasher.add_node("node2")
    hasher.add_node("node3")
    hasher.add_node("node4")

    keys = [f"key_{i}" for i in range(1000)]
    initial_mapping = {key: hasher.get_nodes(key)[0] for key in keys}

    # Remove node4
    hasher.remove_node("node4")
    new_mapping = {key: hasher.get_nodes(key)[0] for key in keys}

    moved_keys = 0
    incorrect_moves = 0
    for key in keys:
        if initial_mapping[key] != new_mapping[key]:
            moved_keys += 1
            if initial_mapping[key] != "node4":
                incorrect_moves += 1

    # Only keys that were on node4 should move
    # Expected on node4 initially: ~250
    assert 200 <= moved_keys <= 300
    assert incorrect_moves == 0

def test_weight_based_distribution():
    hasher = ConsistentHasher(vnodes=100)
    hasher.add_node("light", weight=1)
    hasher.add_node("heavy", weight=9)

    keys = [f"key_{i}" for i in range(10000)]
    counts = {"light": 0, "heavy": 0}
    for key in keys:
        node = hasher.get_nodes(key)[0]
        counts[node] += 1

    # Ideally light=1000, heavy=9000
    assert 800 <= counts["light"] <= 1200
    assert 8800 <= counts["heavy"] <= 9200
