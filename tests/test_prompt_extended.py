from __future__ import annotations

from commands.registry import dispatch
from shared.prompt_tokens import CP2077_TEMPLATES, expand_prompt
from tests.conftest import make_player, make_state
from world.weather import set_district_weather


def test_expand_extended_tokens():
    player = make_player(name="V")
    player.gold = 500
    player.faction = "arasaka"
    player.ram = 3
    player.max_ram = 8
    state = make_state()
    set_district_weather(state, "watson", "acid_rain")

    expanded = expand_prompt("%w|%g|%p|%f|%m", player, state)
    assert "500" in expanded
    assert "3/8" in expanded
    assert "荒坂公司" in expanded
    assert "酸雨" in expanded or "acid_rain" in expanded
    assert any(period in expanded for period in ("夜晚", "午後", "上午", "黎明", "正午", "黃昏"))


def test_expand_faction_none():
    player = make_player(name="V")
    state = make_state()
    expanded = expand_prompt("%f", player, state)
    assert "邊緣人" in expanded


def test_prompt_template_command():
    player = make_player()
    state = make_state()
    result = dispatch("prompt template street", player, state, [], [])
    assert player.prompt_mud == CP2077_TEMPLATES["street"]
    assert result.world_changed
    assert "street" in "\n".join(result.lines)


def test_prompt_template_unknown():
    player = make_player()
    state = make_state()
    result = dispatch("prompt template missing", player, state, [], [])
    text = "\n".join(result.lines)
    assert "未知範本" in text
    assert "street" in text