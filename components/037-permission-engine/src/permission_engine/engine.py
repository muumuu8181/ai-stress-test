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

    def add_role(self, role: Role) -> Role:
        """
        Adds a new role to the engine, resolving parent references to canonical instances.

        Args:
            role (Role): The role to add.

        Returns:
            Role: The canonical role instance in the engine.
        """
        return self._add_role_recursive(role, set())

    def _add_role_recursive(self, role: Role, visited: Set[str]) -> Role:
        """
        Recursively adds roles and their parents to the engine.

        Args:
            role (Role): The role to add.
            visited (Set[str]): Set of role names currently being processed to detect cycles.

        Returns:
            Role: The canonical role instance.
        """
        if role.name in self.roles:
            canonical_role = self.roles[role.name]
        else:
            canonical_role = Role(role.name)
            canonical_role.set_on_change_callback(self._clear_cache)
            self.roles[role.name] = canonical_role

        if role.name in visited:
            return canonical_role
        visited.add(role.name)

        # Build a list of canonical parents from the *provided* role object
        for parent in role.parents:
            canonical_parent = self._add_role_recursive(parent, visited)
            canonical_role.add_parent(canonical_parent)

        visited.remove(role.name)
        self._clear_cache()
        return canonical_role

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
        Adds a new policy to the engine, ensuring the role and its hierarchy are merged.

        Args:
            policy (Policy): The policy to add.
        """
        # Ensure role is registered and merged canonically
        canonical_role = self.add_role(policy.role)

        # Create a new policy with the canonical role
        canonical_policy = Policy(canonical_role, policy.permission)

        role_name = canonical_role.name
        if role_name not in self.policies_by_role:
            self.policies_by_role[role_name] = []

        self.policies_by_role[role_name].append(canonical_policy)
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
