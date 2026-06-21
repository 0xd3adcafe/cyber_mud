from __future__ import annotations

import hashlib
import json
import stat
import time
from pathlib import Path

import pytest

from commands.auth_helpers import handle_login, handle_register, handle_resume, parse_auth_credentials, parse_register_credentials
from commands.registry import CommandContext, dispatch
from persistence.account_lockout import LOCKOUT_MAX_FAILURES, LOCKOUT_SECONDS
from persistence.passwords import hash_password, needs_rehash, verify_password
from persistence.save import SAVE_DIR, _save_path, load_player, player_exists, save_player
from server.audit_log import log_security_event
from server.connection_limits import (
    can_accept_connection,
    count_connections_for_ip,
    is_idle,
    peer_ip,
)
from server.game import ClientSession, Game
from server.rate_limit import AuthRateLimiter
from server.session_tokens import clear_all_session_tokens, issue_session_token, validate_session_token
from shared.protocol import MAX_LINE_BYTES
from shared.security import validate_character_name, validate_password
from tests.conftest import make_player, make_state


@pytest.fixture(autouse=True)
def _reset_session_tokens():
    clear_all_session_tokens()
    yield
    clear_all_session_tokens()


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
    p1 = make_player(named=False, locale="en")
    state = make_state()
    dispatch("register Runner secret123", p1, state, [], [])

    p2 = make_player(named=False, locale="en")
    missing = dispatch("login Nobody secret123", p2, state, [], [])
    wrong = dispatch("login Runner wrongpass1", p2, state, [], [])

    assert missing.lines == wrong.lines
    assert "Invalid" in missing.lines[0]


def test_login_rehashes_legacy_password(save_dir):
    player = make_player(name="Legacy", named=True, locale="en")
    legacy = hashlib.sha256("legacypass".encode("utf-8")).hexdigest()
    player.password_hash = legacy
    save_player(player)

    session = make_player(named=False, locale="en")
    state = make_state()
    result = handle_login(CommandContext(session, state, "Legacy legacypass", [], []))
    assert result.auth_event
    assert result.meta.get("session_token")
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
    player = make_player(name="Secure", named=True, locale="en")
    player.password_hash = hash_password("secret1234")
    path = save_player(player)
    assert oct(path.stat().st_mode & 0o777) == oct(stat.S_IRUSR | stat.S_IWUSR)


def test_save_dir_mode_700(save_dir):
    player = make_player(name="DirSecure", named=True, locale="en")
    save_player(player)
    assert oct(save_dir.stat().st_mode & 0o777) == oct(stat.S_IRWXU)


def test_register_password_with_spaces(save_dir):
    player = make_player(named=False, locale="en")
    state = make_state()
    result = dispatch("register Spaced2 short", player, state, [], [])
    assert not result.auth_event
    assert any("8" in line for line in result.lines)

    player2 = make_player(named=False, locale="en")
    result = dispatch("register Spaced my long pass", player2, state, [], [])
    assert result.auth_event
    assert result.meta.get("session_token")
    assert player_exists("Spaced")


def test_auth_rate_limiter_blocks_after_failures():
    limiter = AuthRateLimiter(max_failures=3, window_seconds=60, block_seconds=120)
    now = 1000.0
    for _ in range(3):
        limiter.record_failure(now=now)
    assert limiter.is_blocked(now=now + 1)
    limiter.reset()
    assert not limiter.is_blocked(now=now + 2)


class _FakeWriter:
    def __init__(self, peer: tuple[str, int] | None = ("127.0.0.1", 4000)):
        self._peer = peer

    def get_extra_info(self, name: str):
        if name == "peername":
            return self._peer
        return None


def test_peer_ip_from_writer():
    assert peer_ip(_FakeWriter()) == "127.0.0.1"
    assert peer_ip(_FakeWriter(None)) == "unknown"


def test_connection_limit_per_ip(monkeypatch):
    monkeypatch.setattr("server.connection_limits.MAX_CONNECTIONS_PER_IP", 2)
    state = make_state()
    game = Game(state=state)
    game.sessions.append(ClientSession(writer=object(), player=make_player(named=False), peer_ip="10.0.0.1"))
    game.sessions.append(ClientSession(writer=object(), player=make_player(named=False), peer_ip="10.0.0.1"))
    assert count_connections_for_ip(game, "10.0.0.1") == 2
    assert not can_accept_connection(game, "10.0.0.1")
    assert can_accept_connection(game, "10.0.0.2")


def test_idle_timeout_guest_vs_auth(monkeypatch):
    monkeypatch.setattr("server.connection_limits.GUEST_IDLE_SECONDS", 100)
    monkeypatch.setattr("server.connection_limits.AUTH_IDLE_SECONDS", 200)
    guest = ClientSession(writer=object(), player=make_player(named=False), last_activity_at=0.0)
    authed = ClientSession(writer=object(), player=make_player(named=True), last_activity_at=0.0)
    assert not is_idle(guest, now=50.0)
    assert is_idle(guest, now=150.0)
    assert not is_idle(authed, now=150.0)
    assert is_idle(authed, now=250.0)


def test_changepass_success_and_rehash(save_dir):
    player = make_player(named=False, locale="en")
    state = make_state()
    dispatch("register Runner secret123", player, state, [], [])

    result = dispatch("changepass secret123 newerpass1", player, state, [], [])
    assert "changed" in result.lines[0].lower()
    assert result.meta.get("session_token")
    loaded = load_player("Runner")
    assert loaded is not None
    assert verify_password("newerpass1", loaded.password_hash)


def test_changepass_rejects_bad_current(save_dir):
    player = make_player(named=False, locale="en")
    state = make_state()
    dispatch("register Runner secret123", player, state, [], [])

    result = dispatch("changepass wrongpass newerpass1", player, state, [], [])
    assert "incorrect" in result.lines[0].lower()


def test_changepass_requires_auth(save_dir):
    guest = make_player(named=False, locale="en")
    state = make_state()
    result = dispatch("changepass old newpass12", guest, state, [], [])
    assert "log in" in result.lines[0].lower()


def test_login_issues_session_token(save_dir):
    player = make_player(named=False, locale="en")
    state = make_state()
    dispatch("register TokenUser secret123", player, state, [], [])

    guest = make_player(named=False, locale="en")
    result = dispatch("login TokenUser secret123", guest, state, [], [])
    token = result.meta.get("session_token", "")
    assert token
    assert validate_session_token(token) == "tokenuser"


def test_resume_restores_session(save_dir):
    player = make_player(named=False, locale="en")
    state = make_state()
    dispatch("register ResumeUser secret123", player, state, [], [])
    token = issue_session_token("ResumeUser")

    guest = make_player(named=False, locale="en")
    result = handle_resume(CommandContext(guest, state, token, [], []))
    assert result.auth_event
    assert guest.named
    assert guest.name == "ResumeUser"
    assert result.meta.get("session_token")
    assert validate_session_token(token) is None
    assert validate_session_token(result.meta["session_token"]) == "resumeuser"


def test_resume_invalid_token(save_dir):
    guest = make_player(named=False, locale="en")
    state = make_state()
    result = handle_resume(CommandContext(guest, state, "not-a-real-token", [], []))
    assert result.auth_failure
    assert "invalid" in result.lines[0].lower()


def test_account_lockout_after_repeated_failures(save_dir, monkeypatch):
    monkeypatch.setattr("persistence.account_lockout.LOCKOUT_MAX_FAILURES", 3)
    player = make_player(named=False, locale="en")
    state = make_state()
    dispatch("register LockUser secret123", player, state, [], [])

    guest = make_player(named=False, locale="en")
    for _ in range(3):
        dispatch("login LockUser wrongpass1", guest, state, [], [])

    locked = dispatch("login LockUser secret123", guest, state, [], [])
    assert "locked" in locked.lines[0].lower()
    loaded = load_player("LockUser")
    assert loaded is not None
    assert loaded.auth_locked_until > time.time()


def test_account_lockout_clears_on_success(save_dir, monkeypatch):
    monkeypatch.setattr("persistence.account_lockout.LOCKOUT_MAX_FAILURES", 2)
    reg = make_player(named=False, locale="en")
    state = make_state()
    dispatch("register ClearLock secret123", reg, state, [], [])

    guest = make_player(named=False, locale="en")
    dispatch("login ClearLock wrongpass1", guest, state, [], [])
    dispatch("login ClearLock secret123", guest, state, [], [])
    loaded = load_player("ClearLock")
    assert loaded is not None
    assert loaded.auth_failed_attempts == 0
    assert loaded.auth_locked_until == 0.0


def test_audit_log_emits_json(capsys):
    log_security_event("auth_login_failure", player="ghost", reason="unknown_account")
    captured = capsys.readouterr()
    assert "[audit]" in captured.err
    payload = json.loads(captured.err.strip().split("[audit] ", 1)[1])
    assert payload["event"] == "auth_login_failure"
    assert payload["player"] == "ghost"


def test_game_blocks_rate_limited_resume(monkeypatch):
    async def _run() -> None:
        state = make_state()
        game = Game(state=state)

        class _Writer:
            def __init__(self):
                self.lines: list[str] = []

            def write(self, data: bytes) -> None:
                self.lines.append(data.decode("utf-8"))

            async def drain(self) -> None:
                return None

        writer = _Writer()
        session = ClientSession(writer=writer, player=make_player(named=False, locale="en"))
        session.auth_rate_limit = AuthRateLimiter(max_failures=1, window_seconds=60, block_seconds=300)
        session.auth_rate_limit.record_failure()

        keep_open = await game.handle_command(session, "resume faketoken")
        assert keep_open is True
        assert any("Too many failed" in line for line in writer.lines)

    import asyncio

    asyncio.run(_run())


def test_protocol_max_line_bytes_constant():
    assert MAX_LINE_BYTES == 4096


def test_register_rejects_oversized_password(save_dir):
    player = make_player(named=False, locale="en")
    state = make_state()
    huge = "a" * 129
    result = dispatch(f"register BigUser {huge}", player, state, [], [])
    assert not result.auth_event
    assert any("128" in line for line in result.lines)


def test_lockout_constants_sane():
    assert LOCKOUT_MAX_FAILURES >= 5
    assert LOCKOUT_SECONDS >= 300