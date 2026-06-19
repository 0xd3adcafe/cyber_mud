from __future__ import annotations

import json

from client.history import CommandHistory, load_command_history, save_command_history


def test_add_dedupes_consecutive():
    history = CommandHistory()
    history.add("look")
    history.add("look")
    assert history.entries == ["look"]


def test_browse_older_and_newer():
    history = CommandHistory(entries=["look", "go north"])
    history.begin_browse("draft")
    assert history.older() == "go north"
    assert history.older() == "look"
    assert history.newer() == "go north"
    assert history.newer() == "draft"
    assert not history.is_browsing


def test_cancel_browse_restores_draft():
    history = CommandHistory(entries=["look"])
    history.begin_browse("my draft")
    history.older()
    assert history.cancel_browse() == "my draft"
    assert not history.is_browsing


def test_mark_edited_exits_browse():
    history = CommandHistory(entries=["look"])
    history.begin_browse("")
    history.older()
    history.mark_edited()
    assert not history.is_browsing
    assert history.newer() is None


def test_persist_roundtrip(tmp_path, monkeypatch):
    path = tmp_path / "command_history.json"
    monkeypatch.setattr("client.history.history_path", lambda: path)
    history = CommandHistory()
    history.add("scan")
    history.add("map")
    loaded = load_command_history()
    assert loaded == ["scan", "map"]
    save_command_history(["quit"])
    assert json.loads(path.read_text(encoding="utf-8")) == ["quit"]