from __future__ import annotations

import json
from pathlib import Path

from client.animated_log import AnimatedLogBuffer
from client.log_settings import (
    LogDisplaySettings,
    export_log_text,
    load_log_settings,
    parse_log_command,
    resolve_hideable_kind,
    save_log_settings,
    strip_rich_markup,
)
from client.log_styles import format_log_line


def test_parse_log_command_actions():
    assert parse_log_command("") == ("status", None)
    assert parse_log_command("compact on") == ("compact_on", None)
    assert parse_log_command("compact off") == ("compact_off", None)
    assert parse_log_command("compact") == ("compact_toggle", None)
    assert parse_log_command("hide ambient") == ("hide", "ambient")
    assert parse_log_command("show all") == ("show_all", None)
    assert parse_log_command("show combat") == ("show", "combat")
    assert parse_log_command("export /tmp/out.txt") == ("export", "/tmp/out.txt")


def test_resolve_hideable_kind_aliases():
    assert resolve_hideable_kind("ambient") == "ambient"
    assert resolve_hideable_kind("movement") == "env"
    assert resolve_hideable_kind("gigs") == "quest"
    assert resolve_hideable_kind("nope") is None


def test_log_display_hide_and_show():
    settings = LogDisplaySettings()
    hidden = settings.hide_kind("ambient")
    assert hidden.is_hidden("ambient")
    assert not hidden.is_hidden("combat")
    assert hidden.hide_kind("env").is_hidden("env_move")
    shown = hidden.show_kind("ambient")
    assert not shown.is_hidden("ambient")
    assert settings.show_all_kinds().hidden_kinds == frozenset()


def test_compact_mode_uses_plain_prefix():
    full = format_log_line("You punch thug.", kind="combat")
    compact = format_log_line("You punch thug.", kind="combat", compact=True)
    assert "⚔" in full or "⌗" in full
    assert "›" in compact
    assert "⚔" not in compact and "⌗" not in compact


def test_animated_log_hides_kinds_and_skips_separators_in_compact(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("client.log_settings.settings_path", lambda: tmp_path / "settings.json")
    settings = LogDisplaySettings(compact=True, hidden_kinds=frozenset({"ambient"}))
    buf = AnimatedLogBuffer(display=settings)
    buf.append("Distant gunfire stutters.", kind="ambient")
    buf.append("You go north.", kind="env_move")
    buf.append("◈ Neon Square", kind="env")
    rendered = buf.render()
    assert not any("gunfire" in line for line in rendered)
    assert not any("───" in line for line in rendered)
    assert any("Neon Square" in line for line in rendered)


def test_log_settings_persist_round_trip(tmp_path: Path, monkeypatch):
    path = tmp_path / "settings.json"
    monkeypatch.setattr("client.log_settings.settings_path", lambda: path)
    path.write_text(json.dumps({"theme": "neon"}), encoding="utf-8")
    settings = LogDisplaySettings(compact=True, hidden_kinds=frozenset({"ambient", "social"}))
    save_log_settings(settings)
    loaded = load_log_settings()
    assert loaded.compact is True
    assert loaded.hidden_kinds == frozenset({"ambient", "social"})
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["theme"] == "neon"


def test_plain_lines_and_export():
    buf = AnimatedLogBuffer()
    buf.append("[red]Hello[/]", kind="text")
    buf.append("Distant gunfire.", kind="ambient")
    buf.display = LogDisplaySettings(hidden_kinds=frozenset({"ambient"}))
    lines = buf.plain_lines()
    assert lines == ["Hello"]
    assert export_log_text(lines) == "Hello\n"


def test_strip_rich_markup():
    assert strip_rich_markup("[bold red]x[/]") == "x"