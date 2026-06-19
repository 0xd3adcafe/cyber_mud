from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state


def _give(player, item_id: str) -> None:
    player.inventory.append(item_id)


def test_use_med_stim_heals_and_consumes():
    player = make_player(hp=50, max_hp=100)
    state = make_state()
    _give(player, "med_stim")

    result = dispatch("use med_stim", player, state, [], [])

    assert player.hp == 80
    assert "med_stim" not in player.inventory
    assert any("急救" in line or "Med Stim" in line for line in result.lines)
    assert result.world_changed


def test_eat_food_only():
    player = make_player(hp=70, max_hp=100)
    state = make_state()
    _give(player, "synth_ramen")
    _give(player, "energy_drink")

    eat_ok = dispatch("eat synth_ramen", player, state, [], [])
    assert player.hp == 85
    assert "synth_ramen" not in player.inventory

    eat_fail = dispatch("eat energy_drink", player, state, [], [])
    assert "energy_drink" in player.inventory
    assert any("食物" in line or "food" in line for line in eat_fail.lines)


def test_drink_restores_ram():
    player = make_player(hp=100, max_hp=100, ram=2, max_ram=8)
    state = make_state()
    _give(player, "energy_drink")

    result = dispatch("drink energy_drink", player, state, [], [])

    assert player.ram == 4
    assert player.hp == 100
    assert "energy_drink" not in player.inventory
    assert any("RAM" in line for line in result.lines)


def test_use_no_effect_when_full():
    player = make_player(hp=100, max_hp=100, ram=8, max_ram=8)
    state = make_state()
    _give(player, "med_stim")

    result = dispatch("use med_stim", player, state, [], [])

    assert player.hp == 100
    assert "med_stim" in player.inventory
    assert any("滿狀態" in line or "topped off" in line for line in result.lines)


def test_use_non_consumable_rejected():
    player = make_player()
    state = make_state()
    _give(player, "knife")

    result = dispatch("use knife", player, state, [], [])

    assert "knife" in player.inventory
    assert any("不能使用" in line or "not consumable" in line for line in result.lines)


def test_look_shows_consumable_stats():
    player = make_player()
    state = make_state()
    _give(player, "med_stim")

    result = dispatch("look med_stim", player, state, [], [])

    text = "\n".join(result.lines)
    assert "藥品" in text or "medicine" in text
    assert "30" in text