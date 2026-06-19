from __future__ import annotations

import pytest

from commands import register_builtin_commands

register_builtin_commands()


@pytest.fixture
def save_dir(tmp_path, monkeypatch):
    saves = tmp_path / "saves"
    saves.mkdir()
    monkeypatch.setattr("persistence.save.SAVE_DIR", saves)
    return saves