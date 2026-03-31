from typing import Optional, Tuple, TypeVar, Generic

T = TypeVar("T")


class AVLNode(Generic[T]):
    """
    A node in the AVL Tree.

    Attributes:
        key: The value stored in the node.
        height: The height of the node in the tree.
        left: Left child of the node.
        right: Right child of the node.
    """

    def __init__(self, key: T):
        self.key: T = key
        self.height: int = 1
        self.left: Optional[AVLNode[T]] = None
        self.right: Optional[AVLNode[T]] = None

    def __repr__(self) -> str:
        return f"AVLNode({self.key}, h={self.height})"


class AVLTree(Generic[T]):
    """
    AVL Tree implementation (Self-balancing Binary Search Tree).
    Supports insertion, deletion, search, merge, and split.
    """

    def __init__(self):
        self.root: Optional[AVLNode[T]] = None

    def get_height(self, node: Optional[AVLNode[T]]) -> int:
        """Returns the height of a node."""
        return node.height if node else 0

    def _update_height(self, node: AVLNode[T]) -> None:
        """Updates the height of a node based on its children."""
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

    def _get_balance(self, node: Optional[AVLNode[T]]) -> int:
        """Returns the balance factor of a node."""
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def _rotate_right(self, y: AVLNode[T]) -> AVLNode[T]:
        r"""
        Performs a right rotation.
             y              x
            / \            / \
           x   T3   ->    T1  y
          / \                / \
         T1  T2             T2  T3
        """
        x = y.left
        T2 = x.right

        x.right = y
        y.left = T2

        self._update_height(y)
        self._update_height(x)

        return x

    def _rotate_left(self, x: AVLNode[T]) -> AVLNode[T]:
        r"""
        Performs a left rotation.
             x              y
            / \            / \
           T1  y    ->    x   T3
              / \        / \
             T2  T3     T1  T2
        """
        y = x.right
        T2 = y.left

        y.left = x
        x.right = T2

        self._update_height(x)
        self._update_height(y)

        return y

    def _rebalance(self, node: AVLNode[T]) -> AVLNode[T]:
        """Rebalances the node and returns the new root of the subtree."""
        self._update_height(node)
        balance = self._get_balance(node)

        # Left Heavy
        if balance > 1:
            if self._get_balance(node.left) < 0:
                # LR Case
                node.left = self._rotate_left(node.left)
            # LL Case
            return self._rotate_right(node)

        # Right Heavy
        if balance < -1:
            if self._get_balance(node.right) > 0:
                # RL Case
                node.right = self._rotate_right(node.right)
            # RR Case
            return self._rotate_left(node)

        return node

    def insert(self, key: T) -> None:
        """Inserts a key into the AVL tree."""
        self.root = self._insert_recursive(self.root, key)

    def _insert_recursive(self, node: Optional[AVLNode[T]], key: T) -> AVLNode[T]:
        if not node:
            return AVLNode(key)

        if key < node.key:
            node.left = self._insert_recursive(node.left, key)
        elif key > node.key:
            node.right = self._insert_recursive(node.right, key)
        else:
            # Duplicate keys are not allowed in this implementation
            return node

        return self._rebalance(node)

    def delete(self, key: T) -> None:
        """Deletes a key from the AVL tree."""
        self.root = self._delete_recursive(self.root, key)

    def _delete_recursive(
        self, node: Optional[AVLNode[T]], key: T
    ) -> Optional[AVLNode[T]]:
        if not node:
            return None

        if key < node.key:
            node.left = self._delete_recursive(node.left, key)
        elif key > node.key:
            node.right = self._delete_recursive(node.right, key)
        else:
            # Node to be deleted found
            if not node.left:
                return node.right
            elif not node.right:
                return node.left

            # Node with two children: Get the inorder successor
            temp = self._get_min_value_node(node.right)
            node.key = temp.key
            node.right = self._delete_recursive(node.right, temp.key)

        return self._rebalance(node)

    def _get_min_value_node(self, node: AVLNode[T]) -> AVLNode[T]:
        current = node
        while current.left:
            current = current.left
        return current

    def search(self, key: T) -> Optional[AVLNode[T]]:
        """Searches for a key in the AVL tree."""
        return self._search_recursive(self.root, key)

    def _search_recursive(
        self, node: Optional[AVLNode[T]], key: T
    ) -> Optional[AVLNode[T]]:
        if not node or node.key == key:
            return node

        if key < node.key:
            return self._search_recursive(node.left, key)
        return self._search_recursive(node.right, key)

    def inorder_traversal(self) -> list[T]:
        """Returns the keys in inorder."""
        keys = []
        self._inorder_recursive(self.root, keys)
        return keys

    def _inorder_recursive(self, node: Optional[AVLNode[T]], keys: list[T]) -> None:
        if node:
            self._inorder_recursive(node.left, keys)
            keys.append(node.key)
            self._inorder_recursive(node.right, keys)

    # --- Merge and Split Implementation ---

    def merge(self, other: "AVLTree[T]") -> None:
        """
        Merges another AVL tree into this one.
        Inserts all elements of the other tree into this one.
        """
        for key in other.inorder_traversal():
            self.insert(key)

    def split(self, key: T) -> Tuple["AVLTree[T]", "AVLTree[T]"]:
        """
        Splits the tree into two AVL trees: one with keys < key and one with keys > key.
        Returns (left_tree, right_tree).
        """
        left_tree = AVLTree[T]()
        right_tree = AVLTree[T]()

        for k in self.inorder_traversal():
            if k < key:
                left_tree.insert(k)
            elif k > key:
                right_tree.insert(k)

        return left_tree, right_tree

    def is_balanced(self) -> bool:
        """Checks if the tree is balanced."""
        return self._is_balanced_recursive(self.root)

    def _is_balanced_recursive(self, node: Optional[AVLNode[T]]) -> bool:
        if not node:
            return True
        balance = self._get_balance(node)
        if abs(balance) > 1:
            return False
        return self._is_balanced_recursive(node.left) and self._is_balanced_recursive(
            node.right
        )
