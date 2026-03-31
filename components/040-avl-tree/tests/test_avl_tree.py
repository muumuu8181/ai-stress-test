import sys
import os

# Add src to path to import avl_tree
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from avl_tree import AVLTree, AVLNode  # noqa: E402
import cli  # noqa: E402
from unittest.mock import patch
import io


def test_repr():
    node = AVLNode(10)
    assert repr(node) == "AVLNode(10, h=1)"


def test_get_height():
    tree = AVLTree[int]()
    assert tree.get_height(None) == 0
    node = AVLNode(10)
    assert tree.get_height(node) == 1


def test_get_balance_none():
    tree = AVLTree[int]()
    assert tree._get_balance(None) == 0


def test_insert_duplicate():
    tree = AVLTree[int]()
    tree.insert(10)
    tree.insert(10)
    assert tree.inorder_traversal() == [10]


def test_is_balanced_deep():
    tree = AVLTree[int]()
    # Create an unbalanced tree manually to test is_balanced
    n1 = AVLNode(10)
    n2 = AVLNode(20)
    n3 = AVLNode(30)
    n1.right = n2
    n2.right = n3
    n1.height = 3
    n2.height = 2
    tree.root = n1
    assert not tree.is_balanced()


def test_insert_balanced():
    tree = AVLTree[int]()
    keys = [10, 20, 30, 40, 50, 25]
    for key in keys:
        tree.insert(key)
        assert tree.is_balanced()

    assert tree.inorder_traversal() == [10, 20, 25, 30, 40, 50]


def test_delete():
    tree = AVLTree[int]()
    keys = [10, 20, 30, 40, 50, 25]
    for key in keys:
        tree.insert(key)

    tree.delete(30)
    assert tree.is_balanced()
    assert 30 not in tree.inorder_traversal()
    assert tree.inorder_traversal() == [10, 20, 25, 40, 50]

    tree.delete(10)
    assert tree.is_balanced()
    assert tree.inorder_traversal() == [20, 25, 40, 50]

    tree.delete(40)
    tree.delete(50)
    tree.delete(25)
    tree.delete(20)
    assert tree.root is None


def test_search():
    tree = AVLTree[int]()
    tree.insert(10)
    tree.insert(20)
    tree.insert(5)

    assert tree.search(10) is not None
    assert tree.search(10).key == 10
    assert tree.search(20) is not None
    assert tree.search(5) is not None
    assert tree.search(100) is None


def test_merge():
    tree1 = AVLTree[int]()
    tree1.insert(10)
    tree1.insert(20)

    tree2 = AVLTree[int]()
    tree2.insert(5)
    tree2.insert(15)
    tree2.insert(25)

    tree1.merge(tree2)
    assert tree1.is_balanced()
    assert tree1.inorder_traversal() == [5, 10, 15, 20, 25]


def test_split():
    tree = AVLTree[int]()
    for i in [10, 20, 30, 40, 50]:
        tree.insert(i)

    left, right = tree.split(25)
    assert left.inorder_traversal() == [10, 20]
    assert right.inorder_traversal() == [30, 40, 50]
    assert left.is_balanced()
    assert right.is_balanced()


def test_rotations():
    # LL case
    tree = AVLTree[int]()
    tree.insert(30)
    tree.insert(20)
    tree.insert(10)
    assert tree.root.key == 20
    assert tree.root.left.key == 10
    assert tree.root.right.key == 30

    # RR case
    tree = AVLTree[int]()
    tree.insert(10)
    tree.insert(20)
    tree.insert(30)
    assert tree.root.key == 20
    assert tree.root.left.key == 10
    assert tree.root.right.key == 30

    # LR case
    tree = AVLTree[int]()
    tree.insert(30)
    tree.insert(10)
    tree.insert(20)
    assert tree.root.key == 20
    assert tree.root.left.key == 10
    assert tree.root.right.key == 30

    # RL case
    tree = AVLTree[int]()
    tree.insert(10)
    tree.insert(30)
    tree.insert(20)
    assert tree.root.key == 20
    assert tree.root.left.key == 10
    assert tree.root.right.key == 30


def test_empty_tree():
    tree = AVLTree[int]()
    assert tree.inorder_traversal() == []
    assert tree.search(10) is None
    tree.delete(10)  # Should not raise error
    assert tree.root is None
    assert tree.is_balanced()


def test_delete_nonexistent():
    tree = AVLTree[int]()
    tree.insert(10)
    tree.delete(20)
    assert tree.inorder_traversal() == [10]


def test_string_keys():
    tree = AVLTree[str]()
    tree.insert("banana")
    tree.insert("apple")
    tree.insert("cherry")
    assert tree.inorder_traversal() == ["apple", "banana", "cherry"]
    assert tree.is_balanced()


def test_integration():
    import random

    tree = AVLTree[int]()
    nums = list(range(100))
    random.shuffle(nums)

    for n in nums:
        tree.insert(n)
        assert tree.is_balanced()

    random.shuffle(nums)
    for n in nums[:50]:
        tree.delete(n)
        assert tree.is_balanced()

    remaining = sorted(nums[50:])
    assert tree.inorder_traversal() == remaining


def test_cli_basic():
    inputs = [
        "insert 10",
        "insert 20",
        "search 10",
        "search 30",
        "print",
        "delete 10",
        "print",
        "exit",
    ]
    with patch("builtins.input", side_effect=inputs):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.main()
            output = fake_out.getvalue()
            assert "Inserted 10" in output
            assert "Inserted 20" in output
            assert "Found 10" in output
            assert "30 not found" in output
            assert "10 (h=2)" in output or "10 (h=1)" in output
            assert "Deleted 10" in output


def test_cli_errors():
    inputs = ["insert abc", "unknown", "", "exit"]
    with patch("builtins.input", side_effect=inputs):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.main()
            output = fake_out.getvalue()
            assert "Invalid input" in output
            assert "Unknown command" in output


def test_cli_empty_print():
    inputs = ["print", "exit"]
    with patch("builtins.input", side_effect=inputs):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.main()
            output = fake_out.getvalue()
            assert "Tree is empty" in output
