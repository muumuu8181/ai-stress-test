from __future__ import annotations
import hashlib
import json
import bisect
import base64
import math
from typing import List, Optional, Dict, Any, Union, Tuple, Iterable

class MerkleTree:
    """
    A Merkle Tree implementation using SHA-256 with domain separation.

    Domain separation uses 0x00 for leaf nodes and 0x01 for internal nodes
    to prevent second-preimage attacks.
    """

    def __init__(self, data_blocks: Optional[Iterable[bytes]] = None, sort_leaves: bool = False):
        """
        Initializes the Merkle Tree.

        Args:
            data_blocks: An optional iterable of bytes to be added as leaves.
            sort_leaves: If True, leaves will be kept sorted by their content
                        (required for exclusion proofs).
        """
        self.sort_leaves = sort_leaves
        self._raw_leaves: List[bytes] = []
        if data_blocks:
            self._raw_leaves = list(data_blocks)
            if self.sort_leaves:
                self._raw_leaves.sort()

        self._leaf_hashes: List[bytes] = [self._hash_leaf(d) for d in self._raw_leaves]
        self._tree: List[List[bytes]] = []
        self._rebuild()

    @staticmethod
    def _hash_leaf(data: bytes) -> bytes:
        """Computes the hash of a leaf node with domain separation (0x00)."""
        h = hashlib.sha256()
        h.update(b'\x00')
        h.update(data)
        return h.digest()

    @staticmethod
    def _hash_internal(left: bytes, right: bytes) -> bytes:
        """Computes the hash of an internal node with domain separation (0x01)."""
        h = hashlib.sha256()
        h.update(b'\x01')
        h.update(left)
        h.update(right)
        return h.digest()

    def _rebuild(self) -> None:
        """Rebuilds the entire tree structure from current leaf hashes."""
        if not self._leaf_hashes:
            self._tree = []
            return

        tree = [self._leaf_hashes]
        current_level = self._leaf_hashes
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                next_level.append(self._hash_internal(left, right))
            tree.append(next_level)
            current_level = next_level
        self._tree = tree

    def _update_path(self, index: int) -> None:
        """Recalculates the hash path from a specific leaf index to the root."""
        if not self._tree:
            return

        current_idx = index
        for level_idx in range(len(self._tree) - 1):
            level = self._tree[level_idx]
            next_level = self._tree[level_idx + 1]

            if current_idx % 2 == 0:
                left = level[current_idx]
                right = level[current_idx + 1] if current_idx + 1 < len(level) else left
            else:
                left = level[current_idx - 1]
                right = level[current_idx]

            new_hash = self._hash_internal(left, right)
            parent_idx = current_idx // 2
            next_level[parent_idx] = new_hash
            current_idx = parent_idx

    def add_leaf(self, data: bytes) -> None:
        """Adds a new leaf to the tree and rebuilds."""
        if self.sort_leaves:
            bisect.insort(self._raw_leaves, data)
            self._leaf_hashes = [self._hash_leaf(d) for d in self._raw_leaves]
            self._rebuild()
        else:
            self._raw_leaves.append(data)
            self._leaf_hashes.append(self._hash_leaf(data))
            self._rebuild()

    def update_leaf(self, index: int, new_data: bytes) -> None:
        """Updates an existing leaf at a specific index."""
        if index < 0 or index >= len(self._raw_leaves):
            raise IndexError("Leaf index out of range")

        if self.sort_leaves:
            self._raw_leaves.pop(index)
            bisect.insort(self._raw_leaves, new_data)
            self._leaf_hashes = [self._hash_leaf(d) for d in self._raw_leaves]
            self._rebuild()
        else:
            self._raw_leaves[index] = new_data
            self._leaf_hashes[index] = self._hash_leaf(new_data)
            self._update_path(index)

    def batch_update(self, updates: Dict[int, bytes]) -> None:
        """Applies multiple leaf updates simultaneously and rebuilds."""
        if self.sort_leaves:
            # Batch update on sorted tree requires finding and removing then re-inserting
            # This is complex to do efficiently without rebuilding.
            for idx, data in sorted(updates.items(), reverse=True):
                if idx < 0 or idx >= len(self._raw_leaves):
                    raise IndexError(f"Leaf index {idx} out of range")
                self._raw_leaves.pop(idx)
                bisect.insort(self._raw_leaves, data)
            self._leaf_hashes = [self._hash_leaf(d) for d in self._raw_leaves]
            self._rebuild()
        else:
            for idx, data in updates.items():
                if idx < 0 or idx >= len(self._raw_leaves):
                    raise IndexError(f"Leaf index {idx} out of range")
                self._raw_leaves[idx] = data
                self._leaf_hashes[idx] = self._hash_leaf(data)
            self._rebuild()

    def delete_leaf(self, index: int) -> None:
        """Deletes a leaf at a specific index."""
        if index < 0 or index >= len(self._raw_leaves):
            raise IndexError("Leaf index out of range")
        self._raw_leaves.pop(index)
        self._leaf_hashes.pop(index)
        self._rebuild()

    @property
    def root(self) -> Optional[bytes]:
        """Returns the root hash of the Merkle Tree."""
        return self._tree[-1][0] if self._tree and self._tree[-1] else None

    @property
    def root_hex(self) -> Optional[str]:
        """Returns the root hash as a hex string."""
        r = self.root
        return r.hex() if r else None

    @property
    def leaves(self) -> List[bytes]:
        """Returns the list of raw leaves."""
        return self._raw_leaves

    def get_proof(self, index: int) -> List[Dict[str, bytes]]:
        """
        Generates a proof of inclusion for a leaf at a given index.

        Args:
            index: The index of the leaf to prove inclusion for.
        Returns:
            A list of proof steps, each containing either a 'left' or 'right' sibling hash.
        """
        if index < 0 or index >= len(self._leaf_hashes):
            raise IndexError("Leaf index out of range")

        proof = []
        current_idx = index
        for level in self._tree[:-1]:
            if current_idx % 2 == 0:
                sibling_hash = level[current_idx + 1] if current_idx + 1 < len(level) else level[current_idx]
                proof.append({'right': sibling_hash})
            else:
                proof.append({'left': level[current_idx - 1]})
            current_idx //= 2
        return proof

    @staticmethod
    def verify_proof(leaf_data: bytes, proof: List[Dict[str, bytes]], root_hash: bytes) -> bool:
        """
        Verifies a proof of inclusion.
        """
        current_hash = MerkleTree._hash_leaf(leaf_data)
        for step in proof:
            if 'left' in step:
                current_hash = MerkleTree._hash_internal(step['left'], current_hash)
            elif 'right' in step:
                current_hash = MerkleTree._hash_internal(current_hash, step['right'])
            else:
                raise ValueError("Invalid proof step")
        return current_hash == root_hash

    def find_differences(self, other: MerkleTree) -> List[int]:
        """Identifies indices of leaves that differ between two trees."""
        if self.root == other.root:
            return []

        differences = []
        def find_diff(level_idx: int, node_idx: int):
            if level_idx == 0:
                differences.append(node_idx)
                return

            if node_idx >= len(self._tree[level_idx]) or node_idx >= len(other._tree[level_idx]):
                return

            left_child = node_idx * 2
            right_child = node_idx * 2 + 1

            if left_child < len(self._tree[level_idx-1]):
                self_h = self._tree[level_idx-1][left_child]
                other_h = other._tree[level_idx-1][left_child] if left_child < len(other._tree[level_idx-1]) else None
                if self_h != other_h:
                    find_diff(level_idx - 1, left_child)

            if right_child < len(self._tree[level_idx-1]):
                self_h = self._tree[level_idx-1][right_child]
                other_h = other._tree[level_idx-1][right_child] if right_child < len(other._tree[level_idx-1]) else None
                if self_h != other_h:
                    find_diff(level_idx - 1, right_child)

        if self._tree and other._tree:
            max_level = min(len(self._tree), len(other._tree)) - 1
            find_diff(max_level, 0)
            if len(self._raw_leaves) != len(other._raw_leaves):
                min_len = min(len(self._raw_leaves), len(other._raw_leaves))
                max_len = max(len(self._raw_leaves), len(other._raw_leaves))
                differences.extend(range(min_len, max_len))

        return sorted(list(set(differences)))

    def to_json(self) -> str:
        """Serializes the tree's raw leaves and settings to JSON."""
        return json.dumps({
            "leaves": [base64.b64encode(l).decode('ascii') for l in self._raw_leaves],
            "sort_leaves": self.sort_leaves
        })

    @classmethod
    def from_json(cls, json_str: str) -> MerkleTree:
        """Deserializes a Merkle Tree from JSON."""
        data = json.loads(json_str)
        leaves = [base64.b64decode(l) for l in data["leaves"]]
        return cls(leaves, sort_leaves=data["sort_leaves"])

    def get_exclusion_proof(self, data: bytes) -> Dict[str, Any]:
        """Generates a proof of exclusion for a data block in a sorted tree."""
        if not self.sort_leaves:
            raise ValueError("Exclusion proof requires a sorted Merkle tree.")
        idx = bisect.bisect_left(self._raw_leaves, data)
        if idx < len(self._raw_leaves) and self._raw_leaves[idx] == data:
            raise ValueError("Data exists in the tree; cannot generate exclusion proof.")
        proof = {}
        if idx > 0:
            proof['lower'] = {'data': self._raw_leaves[idx-1], 'proof': self.get_proof(idx-1)}
        if idx < len(self._raw_leaves):
            proof['upper'] = {'data': self._raw_leaves[idx], 'proof': self.get_proof(idx)}
        return proof

    @staticmethod
    def verify_exclusion_proof(data: bytes, proof: Dict[str, Any], root_hash: bytes) -> bool:
        """Verifies a proof of exclusion."""
        lower, upper = proof.get('lower'), proof.get('upper')
        if not lower and not upper:
            return root_hash is None
        if lower:
            if lower['data'] >= data or not MerkleTree.verify_proof(lower['data'], lower['proof'], root_hash):
                return False
        if upper:
            if upper['data'] <= data or not MerkleTree.verify_proof(upper['data'], upper['proof'], root_hash):
                return False
        return True

    def get_stats(self) -> Dict[str, int]:
        """Returns statistics about the tree: node count, depth, leaf count."""
        leaf_count = len(self._leaf_hashes)
        node_count = sum(len(level) for level in self._tree)
        depth = len(self._tree) if leaf_count > 0 else 0
        return {"leaf_count": leaf_count, "node_count": node_count, "depth": depth}


class StreamingMerkleTree:
    """
    A streaming implementation of Merkle Tree calculation.
    Uses O(log N) memory to compute the root hash.
    Compatible with MerkleTree's duplicate-on-odd rule.
    """

    def __init__(self):
        self._peaks: List[Optional[bytes]] = [] # Level -> hash
        self._count = 0

    def add_leaf(self, data: bytes) -> None:
        """Adds a leaf hash to the streaming structure."""
        h = MerkleTree._hash_leaf(data)
        level = 0
        while level < len(self._peaks) and self._peaks[level] is not None:
            h = MerkleTree._hash_internal(self._peaks[level], h)
            self._peaks[level] = None
            level += 1

        if level == len(self._peaks):
            self._peaks.append(h)
        else:
            self._peaks[level] = h
        self._count += 1

    @property
    def root(self) -> Optional[bytes]:
        """Computes the current root hash matching MerkleTree's rule."""
        if self._count == 0:
            return None

        height = math.ceil(math.log2(self._count)) if self._count > 1 else 0
        res = None
        temp_count = self._count
        for i in range(height + 1):
            if i < len(self._peaks) and self._peaks[i] is not None:
                p = self._peaks[i]
                if res is None:
                    res = p
                else:
                    res = MerkleTree._hash_internal(p, res)

            if temp_count % 2 == 1:
                if res is not None:
                    if i < height:
                        res = MerkleTree._hash_internal(res, res)

            temp_count = (temp_count + 1) // 2

        return res
