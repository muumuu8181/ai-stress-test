import pytest
from permission_engine.models import Role, Permission, Policy


def test_role_creation():
    role = Role("admin")
    assert role.name == "admin"
    assert len(role.parents) == 0


def test_role_inheritance():
    admin = Role("admin")
    user = Role("user")
    admin.add_parent(user)
    assert user in admin.parents


def test_role_self_inheritance():
    role = Role("admin")
    with pytest.raises(ValueError, match="A role cannot be its own parent."):
        role.add_parent(role)


def test_role_equality():
    r1 = Role("admin")
    r2 = Role("admin")
    r3 = Role("user")
    assert r1 == r2
    assert r1 != r3
    assert hash(r1) == hash(r2)


def test_permission_creation():
    perm = Permission("file", "read")
    assert perm.resource == "file"
    assert perm.action == "read"


def test_permission_equality():
    p1 = Permission("file", "read")
    p2 = Permission("file", "read")
    p3 = Permission("file", "write")
    assert p1 == p2
    assert p1 != p3
    assert hash(p1) == hash(p2)


def test_policy_creation():
    role = Role("user")
    perm = Permission("file", "read")
    policy = Policy(role, perm)
    assert policy.role == role
    assert policy.permission == perm
