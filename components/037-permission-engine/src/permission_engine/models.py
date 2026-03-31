from typing import List, Optional, Set, Callable


class Role:
    """
    Represents a role in the RBAC system.
    Roles can inherit permissions from other roles.
    """

    def __init__(self, name: str):
        """
        Initializes a new Role.

        Args:
            name (str): The name of the role.
        """
        self.name: str = name
        self.parents: Set["Role"] = set()
        self._on_change: Optional[Callable[[], None]] = None

    def set_on_change_callback(self, callback: Callable[[], None]) -> None:
        """
        Sets a callback to be called when the role's inheritance changes.

        Args:
            callback (Callable[[], None]): The callback function.
        """
        self._on_change = callback

    def add_parent(self, parent: "Role") -> None:
        """
        Adds a parent role to this role for inheritance.

        Args:
            parent (Role): The parent role to inherit from.
        """
        if parent == self:
            raise ValueError("A role cannot be its own parent.")

        if parent not in self.parents:
            self.parents.add(parent)
            if self._on_change:
                self._on_change()

    def __repr__(self) -> str:
        return f"Role(name='{self.name}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


class Permission:
    """
    Represents a permission consisting of a resource and an action.
    """

    def __init__(self, resource: str, action: str):
        """
        Initializes a new Permission.

        Args:
            resource (str): The resource the permission applies to.
            action (str): The action allowed on the resource.
        """
        self.resource: str = resource
        self.action: str = action

    def __repr__(self) -> str:
        return f"Permission(resource='{self.resource}', action='{self.action}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Permission):
            return NotImplemented
        return self.resource == other.resource and self.action == other.action

    def __hash__(self) -> int:
        return hash((self.resource, self.action))


class Policy:
    """
    Represents a policy that assigns a permission to a role.
    """

    def __init__(self, role: Role, permission: Permission):
        """
        Initializes a new Policy.

        Args:
            role (Role): The role assigned the permission.
            permission (Permission): The permission assigned to the role.
        """
        self.role: Role = role
        self.permission: Permission = permission

    def __repr__(self) -> str:
        return f"Policy(role={self.role}, permission={self.permission})"
