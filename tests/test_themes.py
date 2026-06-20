import json

from client.themes import (
    DEFAULT_THEME_ID,
    build_textual_theme,
    load_theme_id,
    parse_theme_command,
    resolve_theme_id,
    save_theme_id,
    settings_path,
    theme_ids,
    theme_label,
)


def test_theme_ids_include_backlog_set():
    expected = {
        "night_city",
        "blade_runner",
        "matrix",
        "mr_robot",
        "hackernet",
        "ready_player_one",
        "tron",
        "grok_night",
        "ctos",
        "dedsec",
        "profiler",
    }
    assert expected.issubset(set(theme_ids()))


def test_resolve_theme_id_aliases():
    assert resolve_theme_id("matrix") == "matrix"
    assert resolve_theme_id("TRON") == "tron"
    assert resolve_theme_id("ctos") == "ctos"
    assert resolve_theme_id("dedsec") == "dedsec"
    assert resolve_theme_id("profiler") == "profiler"
    assert resolve_theme_id("unknown-theme") is None


def test_parse_theme_command():
    assert parse_theme_command("") == ("list", None)
    assert parse_theme_command("list") == ("list", None)
    assert parse_theme_command("tron") == ("set", "tron")
    assert parse_theme_command("nope") == ("invalid", None)


def test_build_textual_theme_fallback():
    theme = build_textual_theme("missing")
    assert theme.name == DEFAULT_THEME_ID


def test_theme_label():
    assert "Matrix" in theme_label("matrix")


def test_save_and_load_theme_id(tmp_path, monkeypatch):
    path = tmp_path / "settings.json"
    monkeypatch.setattr("client.themes.settings_path", lambda: path)
    save_theme_id("tron")
    assert json.loads(path.read_text(encoding="utf-8"))["theme"] == "tron"
    assert load_theme_id() == "tron"
    path.unlink()
    assert load_theme_id() == DEFAULT_THEME_ID