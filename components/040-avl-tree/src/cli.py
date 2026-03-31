import sys
from avl_tree import AVLTree


def print_tree(node, indent="", last=True):
    """Prints the tree structure visually."""
    if node:
        sys.stdout.write(indent)
        if last:
            sys.stdout.write("R---- ")
            indent += "     "
        else:
            sys.stdout.write("L---- ")
            indent += "|    "
        print(f"{node.key} (h={node.height})")
        print_tree(node.left, indent, False)
        print_tree(node.right, indent, True)


def main():
    tree = AVLTree[int]()
    print("AVL Tree CLI")
    print("Commands: insert <val>, delete <val>, search <val>, print, exit")

    while True:
        try:
            line = input("avl> ").strip()
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].lower()

            if cmd == "insert" and len(parts) > 1:
                val = int(parts[1])
                tree.insert(val)
                print(f"Inserted {val}")
            elif cmd == "delete" and len(parts) > 1:
                val = int(parts[1])
                tree.delete(val)
                print(f"Deleted {val}")
            elif cmd == "search" and len(parts) > 1:
                val = int(parts[1])
                result = tree.search(val)
                if result:
                    print(f"Found {val}")
                else:
                    print(f"{val} not found")
            elif cmd == "print":
                if tree.root:
                    print_tree(tree.root)
                else:
                    print("Tree is empty")
            elif cmd == "exit":
                break
            else:
                print("Unknown command or missing argument")
        except ValueError:
            print("Invalid input: value must be an integer")
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    main()
