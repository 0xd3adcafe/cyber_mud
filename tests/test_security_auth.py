from __future__ import annotations

import hashlib
import json
import os
import stat

from commands.auth_helpers import handle_login, handle_register, parse_auth_credentials, parse_register_credentials
from commands.registry import CommandContext, dispatch
from persistence.passwords import hash_password, needs_rehash, verify_password
from persistence.save import _save_path, load_player, player_exists, save_player
from server.rate_limit import AuthRateLimiter
from shared.security import validate_character_name, validate_password
from tests.conftest import make_player, make_state


def test_pbkdf2_hash_and_verify():
    stored = hash_password("nightcity42")
    assert stored.startswith("$pbkdf2$")
    assert verify_password("nightcity42", stored)
    assert not verify_password("wrong", stored)
    assert not needs_rehash(stored)


def test_legacy_sha256_verify_and_rehash():
    legacy = hashlib.sha256("legacypass".encode("utf-8")).hexdigest()
    assert verify_password("legacypass", legacy)
    assert needs_rehash(legacy)


def test_parse_auth_credentials_supports_spaces():
    assert parse_auth_credentials("V my secret pass") == ("V", "my secret pass")
    assert parse_register_credentials("V my secret pass mature") == ("V", "my secret pass", True)


def test_validate_name_and_password_policy():
    assert validate_character_name("a") == "auth.name_short"
    assert validate_character_name("../../x") == "auth.name_invalid"
    assert validate_character_name("Runner") is None
    assert validate_password("short") == "auth.password_short"
    assert validate_password("longenough") is None


def test_login_unified_invalid_credentials(save_dir):
    p1 = make_player(named=False)
    state = make_state()
    dispatch("register Runner secret123", p1, state, [], [])

    p2 = make_player(named=False)
    missing = dispatch("login Nobody secret123", p2, state, [], [])
    wrong = dispatch("login Runner wrongpass1", p2, state, [], [])

    assert missing.lines == wrong.lines
    assert "Invalid" in missing.lines[0] or "帳號" in missing.lines[0]


def test_login_rehashes_legacy_password(save_dir):
    player = make_player(name="Legacy", named=True)
    legacy = hashlib.sha256("legacypass".encode("utf-8")).hexdigest()
    player.password_hash = legacy
    save_player(player)

    session = make_player(named=False)
    state = make_state()
    result = handle_login(CommandContext(session, state, "Legacy legacypass", [], []))
    assert result.auth_event
    loaded = load_player("Legacy")
    assert loaded is not None
    assert loaded.password_hash.startswith("$pbkdf2$")


def test_save_path_rejects_traversal():
    try:
        _save_path("../escape")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for traversal name")


def test_save_file_mode_600(save_dir):
    player = make_player(name="Secure", named=True)
    player.password_hash = hash_password("secret1234")
    path = save_player(player)
    assert oct(path.stat().st_mode & 0o777) == oct(stat.S_IRUSR | stat.S_IWUSR)


def test_register_password_with_spaces(save_dir):
    player = make_player(named=False)
    state = make_state()
    result = dispatch("register Spaced2 short", player, state, [], [])
    assert not result.auth_event
    assert any("8" in line for line in result.lines)

    player2 = make_player(named=False)
    result = dispatch("register Spaced my long pass", player2, state, [], [])
    assert result.auth_event
    assert player_exists("Spaced")


def test_auth_rate_limiter_blocks_after_failures():
    limiter = AuthRateLimiter(max_failures=3, window_seconds=60, block_seconds=120)
    now = 1000.0
    for _ in range(3):
        limiter.record_failure(now=now)
    assert limiter.is_blocked(now=now + 1)
    limiter.reset()
    assert not limiter.is_blocked(now=now + 2)