from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_lang_shows_current_locale():
    player = make_player(locale="en", named=True)
    state = make_state()
    result = dispatch("lang", player, state, [], [])
    assert "en" in result.lines[0]


def test_lang_switch_to_zh():
    player = make_player(locale="en", named=True)
    state = make_state()
    result = dispatch("lang zh", player, state, [], [])
    assert player.locale == "zh"
    assert "zh" in result.lines[0]
    assert result.meta.get("locale") == "zh"


def test_lang_invalid():
    player = make_player(locale="en", named=True)
    state = make_state()
    result = dispatch("lang fr", player, state, [], [])
    assert player.locale == "en"
    assert "fr" in result.lines[0]