from typing import Dict, List, Set, Optional, Tuple
from .models import Role, Permission, Policy


class PermissionEngine:
    """
    Core engine for Role-Based Access Control.
    Manages roles, permissions, and policies.
    Provides methods for permission evaluation and caching.
    """

    def __init__(self):
        """
        Initializes the PermissionEngine.
        """
        self.roles: Dict[str, Role] = {}
        # Policies indexed by role name for efficient lookup
        self.policies_by_role: Dict[str, List[Policy]] = {}
        self._cache: Dict[Tuple[str, str, str], bool] = {}

    def add_role(self, role: Role) -> None:
        """
        Adds a new role to the engine.

        Args:
            role (Role): The role to add.
        """
        if role.name in self.roles:
            # Update the existing role's parents if necessary
            existing_role = self.roles[role.name]
            for parent in role.parents:
                existing_role.add_parent(parent)
        else:
            self.roles[role.name] = role
        self._clear_cache()

    def get_role(self, name: str) -> Optional[Role]:
        """
        Retrieves a role by its name.

        Args:
            name (str): The name of the role.

        Returns:
            Optional[Role]: The role if found, None otherwise.
        """
        return self.roles.get(name)

    def add_policy(self, policy: Policy) -> None:
        """
        Adds a new policy to the engine.

        Args:
            policy (Policy): The policy to add.
        """
        # Ensure role is registered
        if policy.role.name not in self.roles:
            self.add_role(policy.role)

        role_name = policy.role.name
        if role_name not in self.policies_by_role:
            self.policies_by_role[role_name] = []

        self.policies_by_role[role_name].append(policy)
        self._clear_cache()

    def _clear_cache(self) -> None:
        """
        Clears the permission evaluation cache.
        """
        self._cache = {}

    def check_permission(self, role_name: str, resource: str, action: str) -> bool:
        """
        Evaluates if a role has permission for a specific resource and action.

        Args:
            role_name (str): The name of the role.
            resource (str): The resource being accessed.
            action (str): The action being performed.

        Returns:
            bool: True if permission is granted, False otherwise.
        """
        # Check cache first
        cache_key = (role_name, resource, action)
        if cache_key in self._cache:
            return self._cache[cache_key]

        role = self.get_role(role_name)
        if not role:
            return False

        # Evaluate permission
        result = self._evaluate_role_permission(role, resource, action, set())

        # Store in cache
        self._cache[cache_key] = result
        return result

    def _evaluate_role_permission(self, role: Role, resource: str, action: str, visited: Set[str]) -> bool:
        """
        Recursively evaluates permission through role inheritance.

        Args:
            role (Role): The role to evaluate.
            resource (str): The resource.
            action (str): The action.
            visited (Set[str]): A set of already visited roles to prevent infinite recursion.

        Returns:
            bool: True if permission is granted, False otherwise.
        """
        if role.name in visited:
            return False
        visited.add(role.name)

        # Check policies directly assigned to this role
        policies = self.policies_by_role.get(role.name, [])
        for policy in policies:
            if (policy.permission.resource == resource or policy.permission.resource == "*") and \
                (policy.permission.action == action or policy.permission.action == "*"):
                return True

        # Check inherited permissions from parents
        for parent in role.parents:
            if self._evaluate_role_permission(parent, resource, action, visited):
                return True

        return False
