import hashlib
import bisect
import json
from typing import List, Dict, Any, Optional, Callable, Set


class ConsistentHasher:
    """
    Consistent Hashing implementation for distributed systems.

    Supports virtual nodes, weighted nodes, multiple replicas, and load statistics.
    Uses only the Python standard library.

    Attributes:
        hash_algorithm (str): The name of the hash algorithm to use (md5, sha1, sha256).
        vnodes_base (int): Base number of virtual nodes per node.
        nodes (Dict[str, int]): Dictionary of node names and their weights.
        ring (List[int]): Sorted list of hash values (the ring).
        vnode_to_node (Dict[int, str]): Map from hash value to node name.
    """

    SUPPORTED_ALGORITHMS = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
    }

    def __init__(self, hash_algorithm: str = "sha256", vnodes: int = 100):
        """
        Initializes the ConsistentHasher.

        Args:
            hash_algorithm (str): Hash algorithm to use ('md5', 'sha1', 'sha256').
            vnodes (int): Base number of virtual nodes per node.

        Raises:
            ValueError: If hash_algorithm is not supported.
        """
        if hash_algorithm.lower() not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}. "
                             f"Supported: {list(self.SUPPORTED_ALGORITHMS.keys())}")

        self.hash_algorithm = hash_algorithm.lower()
        self.vnodes_base = vnodes
        self.nodes: Dict[str, int] = {}  # node_name -> weight
        self.ring: List[int] = []
        self.vnode_to_node: Dict[int, str] = {}
        self._hash_func = self.SUPPORTED_ALGORITHMS[self.hash_algorithm]

    def _hash(self, key: str) -> int:
        """
        Generates a hash value for a given key.

        Args:
            key (str): The key to hash.

        Returns:
            int: The hash value as an integer.
        """
        return int(self._hash_func(key.encode("utf-8")).hexdigest(), 16)

    def add_node(self, node_name: str, weight: int = 1) -> None:
        """
        Adds a node to the consistent hash ring.

        Args:
            node_name (str): The name of the node to add.
            weight (int): The weight of the node, proportional to its capacity.

        Raises:
            ValueError: If node_name already exists or weight is invalid.
        """
        if node_name in self.nodes:
            raise ValueError(f"Node already exists: {node_name}")
        if weight <= 0:
            raise ValueError("Weight must be greater than zero.")

        self.nodes[node_name] = weight
        vnode_count = self.vnodes_base * weight
        for i in range(vnode_count):
            # Generate a unique key for each virtual node
            vnode_key = f"{node_name}:vnode:{i}"
            vnode_hash = self._hash(vnode_key)
            # Insert the hash into the ring and maintain sorting
            bisect.insort(self.ring, vnode_hash)
            self.vnode_to_node[vnode_hash] = node_name

    def remove_node(self, node_name: str) -> None:
        """
        Removes a node from the consistent hash ring.

        Args:
            node_name (str): The name of the node to remove.

        Raises:
            ValueError: If node_name does not exist.
        """
        if node_name not in self.nodes:
            raise ValueError(f"Node does not exist: {node_name}")

        weight = self.nodes.pop(node_name)
        vnode_count = self.vnodes_base * weight
        for i in range(vnode_count):
            vnode_key = f"{node_name}:vnode:{i}"
            vnode_hash = self._hash(vnode_key)
            # Find and remove the hash from the ring
            idx = bisect.bisect_left(self.ring, vnode_hash)
            if idx < len(self.ring) and self.ring[idx] == vnode_hash:
                self.ring.pop(idx)
                self.vnode_to_node.pop(vnode_hash, None)

    def get_nodes(self, key: str, replicas: int = 1) -> List[str]:
        """
        Retrieves the nodes assigned to a given key.

        Args:
            key (str): The key to allocate.
            replicas (int): The number of nodes to return (for data redundancy).

        Returns:
            List[str]: A list of node names assigned to the key.

        Raises:
            ValueError: If the ring is empty or replicas is greater than the number of nodes.
        """
        if not self.ring:
            raise ValueError("No nodes in the ring.")
        if replicas > len(self.nodes):
            raise ValueError(f"Replica count {replicas} exceeds number of nodes "
                             f"{len(self.nodes)}.")

        key_hash = self._hash(key)
        # Binary search for the index of the first hash >= key_hash
        idx = bisect.bisect_left(self.ring, key_hash)

        result_nodes: List[str] = []
        # Traverse the ring until we find enough distinct nodes
        for i in range(len(self.ring)):
            # Handle wrapping by using modulo
            current_idx = (idx + i) % len(self.ring)
            node_name = self.vnode_to_node[self.ring[current_idx]]
            if node_name not in result_nodes:
                result_nodes.append(node_name)
                if len(result_nodes) == replicas:
                    break

        return result_nodes

    def get_stats(self) -> Dict[str, Any]:
        """
        Returns load distribution statistics for the current ring.

        Returns:
            Dict[str, Any]: A dictionary containing the number of vnodes per node,
                            and the approximate percentage of the ring covered by each node.
        """
        total_vnodes = len(self.ring)
        if total_vnodes == 0:
            return {"total_nodes": 0, "total_vnodes": 0, "distribution": {}}

        vnode_counts: Dict[str, int] = {}
        # Calculate coverage by looking at the distance between vnodes
        coverage: Dict[str, float] = {node: 0.0 for node in self.nodes}

        # Calculate ring segments.
        # Max value of the ring is the max possible hash value + 1.
        # We'll use a 2^256 scale for simplicity for SHA-256 (roughly).
        # Actually, for statistics, we can just look at the fraction of hashes.
        for i in range(total_vnodes):
            current_hash = self.ring[i]
            prev_hash = self.ring[i - 1] if i > 0 else self.ring[-1]
            node_name = self.vnode_to_node[current_hash]
            vnode_counts[node_name] = vnode_counts.get(node_name, 0) + 1

            # Segment size calculation handles wrapping correctly
            if current_hash >= prev_hash:
                segment_size = current_hash - prev_hash
            else:
                # Wrap around the full hash space.
                # Assuming the hash space is defined by the hexdigest size.
                hash_bits = self._hash_func().digest_size * 8
                max_hash = 2 ** hash_bits
                segment_size = (max_hash - prev_hash) + current_hash

            coverage[node_name] += segment_size

        # Normalize coverage to percentages
        hash_bits = self._hash_func().digest_size * 8
        max_hash = 2 ** hash_bits
        normalized_coverage = {node: (cov / max_hash) * 100 for node, cov in coverage.items()}

        return {
            "total_nodes": len(self.nodes),
            "total_vnodes": total_vnodes,
            "vnode_counts": vnode_counts,
            "coverage_percentage": normalized_coverage,
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the hasher state to a dictionary.

        Returns:
            Dict[str, Any]: Serialized hasher state.
        """
        return {
            "hash_algorithm": self.hash_algorithm,
            "vnodes_base": self.vnodes_base,
            "nodes": self.nodes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConsistentHasher":
        """
        Deserializes a hasher from a dictionary.

        Args:
            data (Dict[str, Any]): Serialized hasher state.

        Returns:
            ConsistentHasher: A new instance of ConsistentHasher.
        """
        hasher = cls(
            hash_algorithm=data["hash_algorithm"],
            vnodes=data["vnodes_base"]
        )
        for node_name, weight in data["nodes"].items():
            hasher.add_node(node_name, weight)
        return hasher
