import pytest
from backend.routers.access.password import get_password_hash, verify_password


def test_hash_is_not_plaintext():
    h = get_password_hash("secret123")
    assert h != "secret123"
    assert len(h) > 20


def test_verify_correct_password():
    h = get_password_hash("mypassword")
    assert verify_password("mypassword", h) is True


def test_verify_wrong_password():
    h = get_password_hash("correct")
    assert verify_password("wrong", h) is False


def test_different_hashes_for_same_password():
    # argon2 is salted — same input → different hashes
    h1 = get_password_hash("same")
    h2 = get_password_hash("same")
    assert h1 != h2


def test_empty_password_hashes_and_verifies():
    h = get_password_hash("")
    assert verify_password("", h) is True
    assert verify_password("notempty", h) is False
