# Merkle Tree Library

A pure Python implementation of a Merkle Tree with SHA-256 and domain separation.

## Features

- **SHA-256 Based:** Uses domain separation (0x00 for leaves, 0x01 for internals) to prevent second-preimage attacks.
- **Dynamic Operations:** Support for adding, updating (O(log N)), and deleting leaves.
- **Proof of Inclusion:** Generate and verify proofs that a data block is part of the tree.
- **Proof of Exclusion:** Generate and verify proofs that a data block is *not* in the tree (requires a sorted tree).
- **Difference Detection:** Efficiently identify which leaves differ between two trees.
- **Batch Updates:** Simultaneously update multiple leaves.
- **Serialization:** Serialize the tree to JSON and reconstruct it later.
- **Streaming Construction:** Build the tree with O(log N) memory while matching the standard "duplicate-on-odd" root calculation.
- **Tree Statistics:** Access node count, depth, and leaf count.

## Usage

### Basic Tree Construction

```python
from merkletree.merkle_tree import MerkleTree

leaves = [b"data1", b"data2", b"data3"]
tree = MerkleTree(leaves)

print(f"Root: {tree.root_hex}")
print(f"Stats: {tree.get_stats()}")
```

### Partial Updates

```python
# O(log N) update
tree.update_leaf(index=1, new_data=b"new_data2")
```

### Proof of Inclusion

```python
# Generate proof for index 0
proof = tree.get_proof(0)

# Verify proof
is_valid = MerkleTree.verify_proof(b"data1", proof, tree.root)
print(f"Is valid: {is_valid}")
```

### Proof of Exclusion (Sorted Merkle Tree)

```python
# Create a sorted tree
stree = MerkleTree([b"a", b"c", b"e"], sort_leaves=True)

# Prove that 'b' is not in the tree
eproof = stree.get_exclusion_proof(b"b")

# Verify exclusion
is_excluded = MerkleTree.verify_exclusion_proof(b"b", eproof, stree.root)
print(f"Is excluded: {is_excluded}")
```

### Difference Detection

```python
tree1 = MerkleTree([b"a", b"b", b"c", b"d"])
tree2 = MerkleTree([b"a", b"X", b"c", b"Y"])

diffs = tree1.find_differences(tree2)
print(f"Differing indices: {diffs}") # Output: [1, 3]
```

### Streaming Construction

```python
from merkletree.merkle_tree import StreamingMerkleTree

stree = StreamingMerkleTree()
for chunk in [b"data1", b"data2", b"data3"]:
    stree.add_leaf(chunk)

# Matches standard MerkleTree root exactly
print(f"Streaming Root: {stree.root.hex()}")
```

## Running Tests

```bash
PYTHONPATH=src pytest tests/
```
