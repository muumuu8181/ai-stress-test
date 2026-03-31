import sys
from .engine import PermissionEngine
from .models import Role, Permission, Policy


def run_repl():
    """
    Runs an interactive REPL for the permission engine.
    """
    engine = PermissionEngine()
    print("RBAC Permission Engine REPL")
    print("Commands: role <name> [parent_name], policy <role_name> <resource> <action>, check <role_name> <resource> <action>, exit")

    while True:
        try:
            line = input("> ").strip()
            if not line:
                continue

            parts = line.split()
            cmd = parts[0].lower()

            if cmd == "exit":
                break
            elif cmd == "role":
                if len(parts) < 2:
                    print("Usage: role <name> [parent_name]")
                    continue
                name = parts[1]
                role = Role(name)
                if len(parts) > 2:
                    parent_name = parts[2]
                    parent = engine.get_role(parent_name)
                    if parent:
                        role.add_parent(parent)
                    else:
                        print(f"Parent role '{parent_name}' not found.")
                engine.add_role(role)
                print(f"Role '{name}' added.")
            elif cmd == "policy":
                if len(parts) < 4:
                    print("Usage: policy <role_name> <resource> <action>")
                    continue
                role_name, resource, action = parts[1], parts[2], parts[3]
                role = engine.get_role(role_name)
                if not role:
                    role = Role(role_name)
                    engine.add_role(role)

                permission = Permission(resource, action)
                policy = Policy(role, permission)
                engine.add_policy(policy)
                print(f"Policy added for role '{role_name}'.")
            elif cmd == "check":
                if len(parts) < 4:
                    print("Usage: check <role_name> <resource> <action>")
                    continue
                role_name, resource, action = parts[1], parts[2], parts[3]
                allowed = engine.check_permission(role_name, resource, action)
                print("ALLOWED" if allowed else "DENIED")
            else:
                print(f"Unknown command: {cmd}")
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    run_repl()
