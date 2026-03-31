# Permission Engine

A Role-Based Access Control (RBAC) permission engine with role inheritance, resource-action combinations, and policy caching.

## Features

- **Role Inheritance**: Roles can inherit permissions from other roles.
- **Resource-Action Permissions**: Granular control over resources and actions.
- **Policy Caching**: Efficient permission evaluation with caching.
- **CLI/REPL**: Interactive tool to test permissions.

## Installation

```bash
pip install -e .
```

## Usage

```python
from permission_engine.engine import PermissionEngine
from permission_engine.models import Role, Permission, Policy

# Initialize engine
engine = PermissionEngine()

# Define roles
admin_role = Role(name="admin")
user_role = Role(name="user")
admin_role.add_parent(user_role)

# Define permissions
read_permission = Permission(resource="document", action="read")
write_permission = Permission(resource="document", action="write")

# Assign policies
engine.add_policy(Policy(role=user_role, permission=read_permission))
engine.add_policy(Policy(role=admin_role, permission=write_permission))

# Check permissions
engine.check_permission("admin", "document", "write")  # True
engine.check_permission("admin", "document", "read")   # True (inherited)
engine.check_permission("user", "document", "write")   # False
```

## CLI

```bash
python -m permission_engine.cli
```
