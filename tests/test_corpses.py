from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.corpses import CORPSE_DECAY_TICKS, corpses_in_room, find_corpse_id
from world.tick import process_tick


def _killer():
    player = make_player(room_id="alley", name="Vy")
    player.body = 50
    player.equipment["weapon_secondary"] = "knife"
    return player, make_state()


def test_victory_spawns_corpse_and_removes_npc():
    player, state = _killer()
    assert "thug" in state.npcs_in_room("alley")

    result = dispatch("attack thug", player, state, [], [])

    assert not player.in_combat
    assert "thug" not in state.npcs_in_room("alley")
    corpses = corpses_in_room(state, "alley")
    assert len(corpses) == 1
    assert corpses[0].npc_id == "thug"
    assert corpses[0].loot == ["mod_chip", "knife"]
    assert any("屍體" in line for line in result.lines)
    assert result.world_changed


def test_look_corpse_shows_loot():
    player, state = _killer()
    dispatch("attack thug", player, state, [], [])

    result = dispatch("look thug", player, state, [], [])

    assert any("身上" in line for line in result.lines)
    assert any("智慧連結晶片" in line or "戰術折刀" in line for line in result.lines)


def test_corpse_label_shows_english_suffix():
    from world.corpses import corpse_label

    player, state = _killer()
    dispatch("attack thug", player, state, [], [])
    corpse = state.corpses["thug_corpse"]

    assert corpse_label(state, corpse, "zh") == "街頭暴徒的屍體 (Street Thug)"


def test_look_room_shows_corpse_english_suffix():
    player, state = _killer()
    dispatch("attack thug", player, state, [], [])

    result = dispatch("look", player, state, [], [])
    text = "\n".join(result.lines)

    assert "(Street Thug)" in text


def test_take_from_corpse():
    player, state = _killer()
    dispatch("attack thug", player, state, [], [])

    result = dispatch("take mod_chip from thug", player, state, [], [])

    assert "mod_chip" in player.inventory
    assert "mod_chip" not in state.corpses["thug_corpse"].loot
    assert any("取走" in line for line in result.lines)
    assert result.world_changed


def test_take_all_from_corpse():
    player, state = _killer()
    dispatch("attack thug", player, state, [], [])

    result = dispatch("take all from corpse", player, state, [], [])

    assert "mod_chip" in player.inventory
    assert "knife" in player.inventory
    assert state.corpses["thug_corpse"].loot == []
    assert result.world_changed


def test_corpse_decays_and_drops_loot():
    player, state = _killer()
    dispatch("attack thug", player, state, [], [])
    corpse = state.corpses["thug_corpse"]
    corpse.decay_at_tick = state.tick_count

    result = process_tick(state, state.time_config, players=[player])

    assert "thug_corpse" not in state.corpses
    assert "mod_chip" in state.items_in_room("alley")
    assert "knife" in state.items_in_room("alley")
    assert any(event.kind == "corpse_decay" for event in result.events)


def test_corpse_decay_ticks_default():
    player, state = _killer()
    dispatch("attack thug", player, state, [], [])
    corpse = state.corpses["thug_corpse"]
    assert corpse.decay_at_tick == state.tick_count + CORPSE_DECAY_TICKS


def test_find_corpse_by_alias():
    player, state = _killer()
    dispatch("attack thug", player, state, [], [])

    assert find_corpse_id(state, "屍體", "alley") == "thug_corpse"
    assert find_corpse_id(state, "corpse", "alley") == "thug_corpse"