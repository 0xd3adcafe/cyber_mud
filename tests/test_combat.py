from __future__ import annotations

import random

from combat.actions import resolve_defend, resolve_flee, resolve_npc_attack, resolve_player_attack, resolve_quickhack
from combat.encounter import encounter_for_player
from commands.registry import dispatch, player_meta, CommandContext
from tests.conftest import make_player, make_state
from world.tick import process_tick


def _fighter(*, room_id: str = "alley", body: int = 3, intelligence: int = 6, reflex: int = 4):
    player = make_player(room_id=room_id, name="V")
    player.body = body
    player.intelligence = intelligence
    player.reflex = reflex
    player.ram = 8
    return player, make_state()


def test_attack_starts_combat_with_hostile_npc():
    player, state = _fighter()
    result = dispatch("attack thug", player, state, [], [])
    assert player.in_combat
    assert player.encounter_id
    assert any("開火" in line or "交戰" in line or "擊中" in line for line in result.lines)
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    assert encounter.npc_id == "thug"
    assert encounter.npc_hp == 30 - player.body


def test_attack_without_target_not_in_combat():
    player, state = _fighter()
    result = dispatch("attack", player, state, [], [])
    assert not player.in_combat
    assert any("用法" in line for line in result.lines)


def test_combat_gates_movement():
    player, state = _fighter()
    dispatch("attack thug", player, state, [], [])
    result = dispatch("go south", player, state, [], [])
    assert player.room_id == "alley"
    assert any("戰鬥中" in line for line in result.lines)


def test_defend_sets_flag():
    player, state = _fighter()
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    result = resolve_defend(state, player)
    assert encounter.defending
    assert any("防禦" in line for line in result.lines)


def test_defend_halves_npc_damage():
    player, state = _fighter()
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    encounter.defending = True
    encounter.npc_cd = 0
    before_hp = player.hp
    result = resolve_npc_attack(state, player, encounter)
    raw = state.world.npc("thug").attack
    expected = max(1, raw // 2)
    assert player.hp == before_hp - expected
    assert not encounter.defending
    assert any("反擊" in line for line in result.lines)


def test_quickhack_costs_ram_and_deals_damage():
    player, state = _fighter(intelligence=5)
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    encounter.player_cd = 0
    before_ram = player.ram
    before_hp = encounter.npc_hp
    result = resolve_quickhack(state, player)
    assert player.ram == before_ram - 2
    assert encounter.npc_hp == before_hp - 10
    assert any("快速破解" in line for line in result.lines)


def test_flee_success_ends_combat(monkeypatch):
    player, state = _fighter(reflex=10)
    dispatch("attack thug", player, state, [], [])
    monkeypatch.setattr(random, "random", lambda: 0.0)
    result = resolve_flee(state, player)
    assert not player.in_combat
    assert result.ended
    assert any("脫離" in line for line in result.lines)


def test_player_meta_includes_combat_fields():
    player, state = _fighter()
    dispatch("attack thug", player, state, [], [])
    meta = player_meta(CommandContext(player, state, ""))
    assert meta["combat"] == "1"
    assert "combat_cd" in meta
    assert "combat_log" in meta
    assert meta["combat_target"] == "街頭暴徒"


def test_combat_tick_npc_counterattack():
    player, state = _fighter()
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    encounter.npc_cd = 0
    encounter.player_cd = 0
    before_hp = player.hp
    result = process_tick(state, state.time_config, players=[player])
    assert result.combat_results
    assert player.hp < before_hp


def test_victory_ends_combat():
    player, state = _fighter(body=50)
    player.equipment["weapon"] = "knife"
    result = dispatch("attack thug", player, state, [], [])
    assert not player.in_combat
    assert any("擊倒" in line for line in result.lines)
    assert result.world_changed