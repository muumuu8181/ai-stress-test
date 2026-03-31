from __future__ import annotations
import json
from typing import Any, List, Optional, Iterator

class BTreeNode:
    """
    A node in the B-Tree.

    Attributes:
        leaf (bool): True if the node is a leaf, False otherwise.
        keys (List[Any]): List of keys stored in the node.
        children (List[BTreeNode]): List of child nodes.
    """
    def __init__(self, leaf: bool = False):
        self.leaf: bool = leaf
        self.keys: List[Any] = []
        self.children: List[BTreeNode] = []

    def __repr__(self) -> str:
        return f"BTreeNode(leaf={self.leaf}, keys={self.keys})"


class BTree:
    """
    B-Tree implementation.

    Attributes:
        t (int): Minimum degree (defines the range for number of keys).
        root (BTreeNode): The root node of the B-Tree.
    """
    def __init__(self, t: int):
        """
        Initialize the B-Tree.

        Args:
            t (int): Minimum degree. Must be at least 2.
        """
        if t < 2:
            raise ValueError("Minimum degree 't' must be at least 2.")
        self.t: int = t
        self.root: BTreeNode = BTreeNode(True)

    def search(self, key: Any, node: Optional[BTreeNode] = None) -> Optional[tuple[BTreeNode, int]]:
        """
        Search for a key in the B-Tree.

        Args:
            key (Any): The key to search for.
            node (Optional[BTreeNode]): The node to start searching from.

        Returns:
            Optional[tuple[BTreeNode, int]]: The node and the index of the key if found, else None.
        """
        if node is None:
            node = self.root

        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            return (node, i)
        elif node.leaf:
            return None
        else:
            return self.search(key, node.children[i])

    def insert(self, key: Any) -> None:
        """
        Insert a key into the B-Tree.

        Args:
            key (Any): The key to insert.
        """
        # Ensure key is comparable to avoid state corruption
        if self.root.keys:
            _ = key < self.root.keys[0] or key > self.root.keys[0]

        root = self.root
        if len(root.keys) == (2 * self.t) - 1:
            new_root = BTreeNode(False)
            self.root = new_root
            new_root.children.insert(0, root)
            self._split_child(new_root, 0)
            self._insert_non_full(new_root, key)
        else:
            self._insert_non_full(root, key)

    def _split_child(self, x: BTreeNode, i: int) -> None:
        """
        Split a child of a node.

        Args:
            x (BTreeNode): The parent node.
            i (int): The index of the child to split.
        """
        t = self.t
        y = x.children[i]
        z = BTreeNode(y.leaf)

        # Split keys
        # y.keys[t-1] is the median
        x.keys.insert(i, y.keys[t - 1])
        z.keys = y.keys[t:]
        y.keys = y.keys[:t - 1]

        # Split children if not leaf
        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]

        x.children.insert(i + 1, z)

    def _insert_non_full(self, x: BTreeNode, k: Any) -> None:
        """
        Insert a key into a node that is not full.

        Args:
            x (BTreeNode): The node to insert into.
            k (Any): The key to insert.
        """
        i = len(x.keys) - 1
        if x.leaf:
            # Find insertion point before mutating
            while i >= 0 and k < x.keys[i]:
                i -= 1
            x.keys.insert(i + 1, k)
        else:
            # Find child to descend
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.children[i].keys) == (2 * self.t) - 1:
                self._split_child(x, i)
                if k > x.keys[i]:
                    i += 1
            self._insert_non_full(x.children[i], k)

    def delete(self, key: Any) -> None:
        """
        Delete a key from the B-Tree.

        Args:
            key (Any): The key to delete.
        """
        self._delete(self.root, key)
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

    def _delete(self, x: BTreeNode, k: Any) -> None:
        """
        Recursive deletion of a key from a node or its subtree.

        Args:
            x (BTreeNode): The current node.
            k (Any): The key to delete.
        """
        t = self.t
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1

        if i < len(x.keys) and x.keys[i] == k:
            # Case 1: Key k is in node x and x is a leaf
            if x.leaf:
                x.keys.pop(i)
                return
            # Case 2: Key k is in node x and x is an internal node
            else:
                y = x.children[i]
                z = x.children[i + 1]
                # Case 2a: Child y has at least t keys
                if len(y.keys) >= t:
                    k_prime = self._get_predecessor(y)
                    x.keys[i] = k_prime
                    self._delete(y, k_prime)
                # Case 2b: Child z has at least t keys
                elif len(z.keys) >= t:
                    k_prime = self._get_successor(z)
                    x.keys[i] = k_prime
                    self._delete(z, k_prime)
                # Case 2c: Both y and z have t-1 keys
                else:
                    self._merge(x, i)
                    self._delete(y, k)
        else:
            # Case 3: Key k is not in node x
            if x.leaf:
                # Key not in tree
                return

            # The key k is in child x.children[i]
            child = x.children[i]
            if len(child.keys) < t:
                # Rebalancing
                # Case 3a: Child has a sibling with at least t keys
                if i > 0 and len(x.children[i - 1].keys) >= t:
                    self._borrow_from_prev(x, i)
                elif i < len(x.children) - 1 and len(x.children[i + 1].keys) >= t:
                    self._borrow_from_next(x, i)
                # Case 3b: Both siblings have t-1 keys
                else:
                    if i < len(x.children) - 1:
                        self._merge(x, i)
                    else:
                        self._merge(x, i - 1)
                        child = x.children[i - 1]

            self._delete(child, k)

    def _get_predecessor(self, x: BTreeNode) -> Any:
        while not x.leaf:
            x = x.children[-1]
        return x.keys[-1]

    def _get_successor(self, x: BTreeNode) -> Any:
        while not x.leaf:
            x = x.children[0]
        return x.keys[0]

    def _borrow_from_prev(self, x: BTreeNode, i: int) -> None:
        child = x.children[i]
        sibling = x.children[i - 1]

        child.keys.insert(0, x.keys[i - 1])
        x.keys[i - 1] = sibling.keys.pop(-1)

        if not child.leaf:
            child.children.insert(0, sibling.children.pop(-1))

    def _borrow_from_next(self, x: BTreeNode, i: int) -> None:
        child = x.children[i]
        sibling = x.children[i + 1]

        child.keys.append(x.keys[i])
        x.keys[i] = sibling.keys.pop(0)

        if not child.leaf:
            child.children.append(sibling.children.pop(0))

    def _merge(self, x: BTreeNode, i: int) -> None:
        y = x.children[i]
        z = x.children[i + 1]

        # Move key from x to y
        y.keys.append(x.keys.pop(i))
        # Move all keys from z to y
        y.keys.extend(z.keys)
        # Move all children from z to y
        if not y.leaf:
            y.children.extend(z.children)

        # Remove z from x
        x.children.pop(i + 1)

    def range_query(self, low: Any, high: Any) -> List[Any]:
        """
        Return all keys in the range [low, high].

        Args:
            low (Any): Lower bound (inclusive).
            high (Any): Upper bound (inclusive).

        Returns:
            List[Any]: List of keys in the range.
        """
        result: List[Any] = []
        self._range_query(self.root, low, high, result)
        return result

    def _range_query(self, x: BTreeNode, low: Any, high: Any, result: List[Any]) -> None:
        i = 0
        while i < len(x.keys) and x.keys[i] < low:
            i += 1

        while i < len(x.keys) and x.keys[i] <= high:
            if not x.leaf:
                self._range_query(x.children[i], low, high, result)
            result.append(x.keys[i])
            i += 1

        if not x.leaf:
            self._range_query(x.children[i], low, high, result)

    def __iter__(self) -> Iterator[Any]:
        """
        In-order traversal iterator.
        """
        return self._in_order_traversal(self.root)

    def _in_order_traversal(self, x: BTreeNode) -> Iterator[Any]:
        for i in range(len(x.keys)):
            if not x.leaf:
                yield from self._in_order_traversal(x.children[i])
            yield x.keys[i]
        if not x.leaf:
            yield from self._in_order_traversal(x.children[-1])

    def dump(self) -> str:
        """
        Return a string representation of the tree structure for debugging.
        """
        lines = self._dump(self.root, 0)
        return "\n".join(lines)

    def _dump(self, x: BTreeNode, level: int) -> List[str]:
        output = [f"{'  ' * level}Level {level}: {x.keys} (leaf={x.leaf})"]
        if not x.leaf:
            for child in x.children:
                output.extend(self._dump(child, level + 1))
        return output

    def to_json(self) -> str:
        """
        Serialize the B-Tree to a JSON string.
        """
        def node_to_dict(node: BTreeNode) -> dict:
            return {
                "leaf": node.leaf,
                "keys": node.keys,
                "children": [node_to_dict(child) for child in node.children]
            }

        data = {
            "t": self.t,
            "root": node_to_dict(self.root)
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> BTree:
        """
        Deserialize a JSON string to a B-Tree.
        """
        data = json.loads(json_str)
        btree = cls(data["t"])

        def dict_to_node(node_data: dict) -> BTreeNode:
            node = BTreeNode(node_data["leaf"])
            node.keys = node_data["keys"]
            node.children = [dict_to_node(child_data) for child_data in node_data["children"]]
            return node

        btree.root = dict_to_node(data["root"])
        return btree
