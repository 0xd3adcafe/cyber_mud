from __future__ import annotations

from commands.help_cmd import HELP_CATEGORIES, format_help
from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_help_groups_commands_by_category():
    player, state = make_player(), make_state()
    lines = format_help(type("Ctx", (), {"player": player, "state": state, "args": ""})())
    text = "\n".join(lines)
    assert "── 探索移動 ──" in text
    assert "── 戰鬥 ──" in text
    assert "── 委託任務 ──" in text
    look_idx = text.index("look")
    combat_idx = text.index("── 戰鬥 ──")
    assert look_idx < combat_idx


def test_help_ui_json_has_category_sections():
    player, state = make_player(), make_state()
    result = dispatch("help", player, state, [], [])
    assert result.panel == "help"
    import json

    ui = json.loads(result.ui_json)
    titles = [section["title"] for section in ui["sections"]]
    assert "探索移動" in titles
    assert "戰鬥" in titles
    assert len(titles) == len(HELP_CATEGORIES)


def test_help_unnamed_shows_auth_only():
    player = make_player(named=False)
    state = make_state()
    lines = format_help(type("Ctx", (), {"player": player, "state": state, "args": ""})())
    text = "\n".join(lines)
    assert "── 登入 ──" in text
    assert "look" not in text
    assert "login" in text