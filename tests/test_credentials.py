from __future__ import annotations

import json
from pathlib import Path

import pytest

from client import credentials as creds


@pytest.fixture
def cred_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "credentials.json"
    monkeypatch.setattr(creds, "credentials_path", lambda: path)
    return path


def test_validate_pin_rejects_non_digits():
    assert creds.validate_pin("12ab") == "PIN 僅能為數字。"
    assert creds.validate_pin("123") == "PIN 需為 4–6 位數字。"
    assert creds.validate_pin("1234567") == "PIN 需為 4–6 位數字。"
    assert creds.validate_pin("1234") is None


def test_save_and_unlock_roundtrip(cred_path: Path):
    assert creds.save_credentials(
        username="runner",
        password="s3cret!",
        mode="login",
        pin="2468",
    ) is None
    assert cred_path.exists()
    assert oct(cred_path.stat().st_mode & 0o777) == oct(0o600)

    unlocked = creds.unlock_credentials("2468")
    assert unlocked is not None
    assert unlocked.username == "runner"
    assert unlocked.password == "s3cret!"
    assert unlocked.mode == "login"


def test_unlock_wrong_pin_returns_none(cred_path: Path):
    creds.save_credentials(username="a", password="b", mode="login", pin="1111")
    assert creds.unlock_credentials("2222") is None


def test_blob_does_not_contain_plaintext(cred_path: Path):
    creds.save_credentials(username="neo", password="matrix", mode="register", pin="4321")
    raw = json.loads(cred_path.read_text(encoding="utf-8"))
    text = json.dumps(raw)
    assert "neo" not in text
    assert "matrix" not in text


def test_clear_credentials(cred_path: Path):
    creds.save_credentials(username="x", password="y", mode="login", pin="9999")
    assert creds.has_stored_credentials()
    creds.clear_credentials()
    assert not creds.has_stored_credentials()
    assert creds.unlock_credentials("9999") is None


def test_auth_meta_persists_pending_credentials(cred_path: Path, monkeypatch: pytest.MonkeyPatch):
    import asyncio

    from textual.widgets import Input

    from client.app import CyberMudApp

    monkeypatch.setattr("client.app.has_stored_credentials", creds.has_stored_credentials)
    monkeypatch.setattr("client.app.save_credentials", creds.save_credentials)

    async def _run() -> None:
        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(80, 40)) as pilot:
            await pilot.pause()
            app._pending_credential_save = ("runner", "secret", "login", "2468")
            app._apply_meta("auth=1")
            await pilot.pause()
            assert cred_path.exists()
            pin = app.query_one("#login_pin", Input)
            assert "credential-hidden" not in pin.classes

    asyncio.run(_run())