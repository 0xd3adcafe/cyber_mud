from __future__ import annotations

import hashlib
import secrets

PBKDF2_PREFIX = "$pbkdf2$"
PBKDF2_ITERATIONS = 600_000
LEGACY_SHA256_HEX_LEN = 64


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"{PBKDF2_PREFIX}{PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def _verify_pbkdf2(password: str, stored: str) -> bool:
    if not stored.startswith(PBKDF2_PREFIX):
        return False
    try:
        iterations_text, salt_hex, digest_hex = stored[len(PBKDF2_PREFIX) :].split("$", 2)
        iterations = int(iterations_text)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, TypeError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return secrets.compare_digest(actual, expected)


def _verify_legacy_sha256(password: str, stored: str) -> bool:
    if len(stored) != LEGACY_SHA256_HEX_LEN:
        return False
    try:
        int(stored, 16)
    except ValueError:
        return False
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return secrets.compare_digest(digest, stored)


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    if password_hash.startswith(PBKDF2_PREFIX):
        return _verify_pbkdf2(password, password_hash)
    return _verify_legacy_sha256(password, password_hash)


def needs_rehash(password_hash: str) -> bool:
    return not password_hash.startswith(PBKDF2_PREFIX)