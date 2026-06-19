from __future__ import annotations

import json
import sys

from persistence.save import delete_save, list_saves, save_player
from tests.conftest import make_player


def test_delete_save_removes_file(save_dir):
    player = make_player(name="Ghost")
    save_player(player)
    assert "ghost" in list_saves()
    assert delete_save("Ghost") is True
    assert list_saves() == []
    assert delete_save("Ghost") is False


def test_admin_delete_save_cli(save_dir, monkeypatch, capsys):
    path = save_dir / "rogue.json"
    path.write_text(json.dumps({"name": "Rogue"}), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["admin", "delete-save", "rogue"])
    from admin.__main__ import delete_save_cmd

    assert delete_save_cmd() == 0
    out = capsys.readouterr().out
    assert "OK: deleted save rogue" in out
    assert not path.exists()


def test_admin_delete_save_missing(save_dir, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["admin", "delete-save", "missing"])
    from admin.__main__ import delete_save_cmd

    assert delete_save_cmd() == 1
    out = capsys.readouterr().out
    assert "ERR: save not found" in out