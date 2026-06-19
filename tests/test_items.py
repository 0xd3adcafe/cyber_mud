from __future__ import annotations

from commands.registry import dispatch
from persistence.save import load_player, save_player
from tests.conftest import make_player, make_state


def _ctx():
    return make_player(), make_state()


def test_take_glowstick():
    player, state = _ctx()
    result = dispatch("take glowstick", player, state, [], [])
    assert "glowstick" in player.inventory
    assert "glowstick" not in state.room_items.get("square", [])
    assert result.world_changed
    assert any("螢光棒" in line for line in result.lines)


def test_take_alias_get():
    player, state = _ctx()
    dispatch("get glowstick", player, state, [], [])
    assert "glowstick" in player.inventory


def test_drop_glowstick():
    player, state = _ctx()
    dispatch("take glowstick", player, state, [], [])
    result = dispatch("drop glowstick", player, state, [], [])
    assert "glowstick" not in player.inventory
    assert "glowstick" in state.room_items["square"]
    assert result.world_changed
    assert any("丟下" in line for line in result.lines)


def test_inventory_empty():
    player, state = _ctx()
    result = dispatch("inventory", player, state, [], [])
    assert any("空的" in line for line in result.lines)


def test_inventory_with_item():
    player, state = _ctx()
    dispatch("take glowstick", player, state, [], [])
    result = dispatch("inventory", player, state, [], [])
    assert any("螢光棒" in line for line in result.lines)


def test_take_persists_in_save(save_dir):
    player, state = _ctx()
    dispatch("take glowstick", player, state, [], [])
    save_player(player)
    loaded = load_player("V")
    assert loaded is not None
    assert "glowstick" in loaded.inventory