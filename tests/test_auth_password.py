"""Tests for password hashing: bcrypt hash and verify_password."""

import pytest

from app.core.security import hash_password, verify_password


def test_hash_password_returns_bcrypt_string():
    """Hash is not plain password and has bcrypt prefix."""
    plain = "password123"
    hashed = hash_password(plain)
    assert hashed != plain
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")


def test_hash_password_different_each_time():
    """Each hash uses a new salt, so hashes differ."""
    plain = "samepassword"
    h1 = hash_password(plain)
    h2 = hash_password(plain)
    assert h1 != h2
    assert verify_password(plain, h1)
    assert verify_password(plain, h2)


def test_verify_password_correct_plain():
    """verify_password returns True for correct plain vs stored hash."""
    plain = "secret456"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_password_wrong_plain():
    """verify_password returns False for wrong plain."""
    plain = "correct"
    wrong = "wrong"
    hashed = hash_password(plain)
    assert verify_password(wrong, hashed) is False


def test_verify_password_wrong_hash():
    """verify_password returns False for wrong/corrupt hash."""
    plain = "password"
    wrong_hash = "$2b$12$invalidbase64hash"
    assert verify_password(plain, wrong_hash) is False
