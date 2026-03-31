import pytest
from permission_engine.models import Role, Permission, Policy
from permission_engine.engine import PermissionEngine


@pytest.fixture
def engine():
    return PermissionEngine()


def test_add_role(engine):
    role = Role("admin")
    engine.add_role(role)
    assert engine.get_role("admin") == role


def test_add_duplicate_role(engine):
    role1 = Role("admin")
    engine.add_role(role1)

    parent = Role("superuser")
    role2 = Role("admin")
    role2.add_parent(parent)

    engine.add_role(role2)

    retrieved_role = engine.get_role("admin")
    assert retrieved_role.name == "admin"
    assert parent in retrieved_role.parents


def test_check_permission_direct(engine):
    role = Role("user")
    perm = Permission("file", "read")
    policy = Policy(role, perm)
    engine.add_policy(policy)

    assert engine.check_permission("user", "file", "read") is True
    assert engine.check_permission("user", "file", "write") is False


def test_check_permission_inheritance(engine):
    admin = Role("admin")
    user = Role("user")
    admin.add_parent(user)

    user_perm = Permission("file", "read")
    admin_perm = Permission("file", "write")

    engine.add_policy(Policy(user, user_perm))
    engine.add_policy(Policy(admin, admin_perm))

    assert engine.check_permission("admin", "file", "read") is True
    assert engine.check_permission("admin", "file", "write") is True
    assert engine.check_permission("user", "file", "read") is True
    assert engine.check_permission("user", "file", "write") is False


def test_check_permission_wildcard(engine):
    admin = Role("admin")
    all_perm = Permission("*", "*")
    engine.add_policy(Policy(admin, all_perm))

    assert engine.check_permission("admin", "any", "thing") is True
    assert engine.check_permission("admin", "other", "action") is True


def test_check_permission_cache(engine):
    role = Role("user")
    perm = Permission("file", "read")
    engine.add_policy(Policy(role, perm))

    # First call - should evaluate and cache
    assert engine.check_permission("user", "file", "read") is True
    assert ("user", "file", "read") in engine._cache

    # Second call - should use cache
    assert engine.check_permission("user", "file", "read") is True


def test_cache_clearing(engine):
    role = Role("user")
    perm = Permission("file", "read")
    engine.add_policy(Policy(role, perm))

    engine.check_permission("user", "file", "read")
    assert len(engine._cache) > 0

    # Adding a new policy should clear cache
    engine.add_policy(Policy(role, Permission("file", "write")))
    assert len(engine._cache) == 0


def test_circular_inheritance(engine):
    role1 = Role("role1")
    role2 = Role("role2")
    role1.add_parent(role2)
    role2.add_parent(role1)

    engine.add_role(role1)
    engine.add_role(role2)

    # Should not infinite loop
    assert engine.check_permission("role1", "resource", "action") is False


def test_missing_role(engine):
    assert engine.check_permission("nonexistent", "resource", "action") is False
