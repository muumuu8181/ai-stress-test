import pytest
from permission_engine.models import Role, Permission, Policy
from permission_engine.engine import PermissionEngine


@pytest.fixture
def engine():
    return PermissionEngine()


def test_canonical_role_instances(engine):
    # Callers build roles from separate objects with same name
    parent_instance_1 = Role("employee")
    canonical_parent_instance_1 = engine.add_role(parent_instance_1)

    child = Role("manager")
    parent_instance_2 = Role("employee")
    child.add_parent(parent_instance_2)
    engine.add_role(child)

    # Ensure manager's parent is the canonical 'employee' from the engine, not parent_instance_2
    canonical_manager = engine.get_role("manager")
    canonical_employee = engine.get_role("employee")

    assert list(canonical_manager.parents)[0] is canonical_employee
    assert list(canonical_manager.parents)[0] is canonical_parent_instance_1
    assert list(canonical_manager.parents)[0] is not parent_instance_2


def test_incremental_updates_via_add_policy(engine):
    # Initially child has no parent
    child_role = Role("child")
    engine.add_role(child_role)

    parent_role = Role("parent")
    engine.add_policy(Policy(parent_role, Permission("file", "read")))

    assert engine.check_permission("child", "file", "read") is False

    # Add a policy with child having parent
    new_child_role = Role("child")
    new_child_role.add_parent(Role("parent"))
    engine.add_policy(Policy(new_child_role, Permission("file", "write")))

    # Now child should inherit read from parent
    assert engine.check_permission("child", "file", "read") is True
    assert engine.check_permission("child", "file", "write") is True


def test_cache_invalidation_on_direct_inheritance_change(engine):
    child = Role("child")
    parent = Role("parent")
    engine.add_role(child)
    engine.add_role(parent)
    engine.add_policy(Policy(parent, Permission("file", "read")))

    # First check - should be False and cached
    assert engine.check_permission("child", "file", "read") is False
    assert ("child", "file", "read") in engine._cache

    # Directly modify inheritance on the canonical object
    canonical_child = engine.get_role("child")
    canonical_parent = engine.get_role("parent")
    canonical_child.add_parent(canonical_parent)

    # Cache should have been cleared by on_change callback
    assert len(engine._cache) == 0

    # Now should be allowed
    assert engine.check_permission("child", "file", "read") is True


def test_transitive_inheritance_canonicalization(engine):
    # A -> B -> C
    c = Role("C")
    engine.add_role(c)
    engine.add_policy(Policy(c, Permission("resource", "action")))

    b = Role("B")
    b.add_parent(Role("C"))
    engine.add_role(b)

    a = Role("A")
    a.add_parent(Role("B"))
    engine.add_role(a)

    assert engine.check_permission("A", "resource", "action") is True

    # Verify canonical pointers
    canonical_a = engine.get_role("A")
    canonical_b = engine.get_role("B")
    canonical_c = engine.get_role("C")

    assert list(canonical_a.parents)[0] is canonical_b
    assert list(canonical_b.parents)[0] is canonical_c
