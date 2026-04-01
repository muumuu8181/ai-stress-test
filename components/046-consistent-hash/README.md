# Consistent Hashing

A pure Python implementation of Consistent Hashing for distributed systems.

## Features

- **Hash Algorithms**: Supports MD5, SHA-1, and SHA-256 via `hashlib`.
- **Virtual Nodes (VNodes)**: Balances load by mapping each physical node to multiple points on the ring.
- **Node Weighting**: Allows more powerful nodes to take a larger share of the load.
- **Data Replication**: Supports mapping a single key to $N$ distinct nodes for redundancy.
- **Load Statistics**: Provides information on how the ring is distributed across nodes.
- **Serialization**: Can be exported to and imported from a dictionary.

## Installation

This library uses only the Python standard library. Copy `src/consistent_hash` to your project.

## Usage

### Basic Usage

```python
from consistent_hash.hasher import ConsistentHasher

# Initialize with SHA-256 and 100 virtual nodes per unit of weight
hasher = ConsistentHasher(hash_algorithm="sha256", vnodes=100)

# Add nodes
hasher.add_node("node1")
hasher.add_node("node2")
hasher.add_node("node3")

# Assign keys to nodes
node = hasher.get_nodes("my_key")[0]
print(f"Key is assigned to: {node}")

# Get multiple replicas for a key
nodes = hasher.get_nodes("my_key", replicas=2)
print(f"Key is replicated to: {nodes}")
```

### Weighting Nodes

```python
# 'heavy_node' will have 300 vnodes, while 'light_node' will have 100
hasher.add_node("heavy_node", weight=3)
hasher.add_node("light_node", weight=1)
```

### Get Load Statistics

```python
stats = hasher.get_stats()
for node, coverage in stats["coverage_percentage"].items():
    print(f"Node: {node}, Ring Coverage: {coverage:.2f}%")
```

### Serialization

```python
# Serialize to a dictionary (can be converted to JSON)
data = hasher.to_dict()

# Deserialize
new_hasher = ConsistentHasher.from_dict(data)
```

## API Reference

### `ConsistentHasher(hash_algorithm="sha256", vnodes=100)`
Initializes the hasher.
- `hash_algorithm`: 'md5', 'sha1', or 'sha256'.
- `vnodes`: Base number of virtual nodes per node.

### `add_node(node_name, weight=1)`
Adds a node to the ring.
- `node_name`: Unique name for the node.
- `weight`: Relative capacity of the node.

### `remove_node(node_name)`
Removes a node from the ring.

### `get_nodes(key, replicas=1)`
Finds the nodes assigned to a key.
- `key`: The string key to look up.
- `replicas`: Number of distinct nodes to return.

### `get_stats()`
Returns a dictionary containing node distribution and coverage statistics.

### `to_dict()` / `from_dict(data)`
Methods for serializing and deserializing the hasher state.
