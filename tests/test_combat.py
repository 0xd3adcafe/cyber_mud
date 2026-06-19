from __future__ import annotations

import random
from unittest.mock import patch

from combat.actions import resolve_defend, resolve_flee, resolve_npc_attack, resolve_quickhack
from combat.strike import resolve_player_attack
from combat.encounter import encounter_for_player
from commands.registry import dispatch, player_meta, CommandContext
from tests.conftest import make_player, make_state
from combat.tick import process_combat_tick
from world.tick import PATROL_EVERY, process_tick


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
    assert any("拳" in line or "攻擊" in line or "擊中" in line or "架勢" in line for line in result.lines)
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    assert encounter.npc_id == "thug"
    assert encounter.npc_hp == 26


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
    assert any("閃避" in line for line in result.lines)


def test_defend_message_uses_armor():
    player, state = _fighter()
    player.equipment["outer_torso"] = "jacket"
    dispatch("attack thug", player, state, [], [])
    result = resolve_defend(state, player)
    assert any("護甲" in line for line in result.lines)


def test_defend_message_uses_weapon():
    player, state = _fighter()
    player.equipment["weapon_secondary"] = "knife"
    dispatch("attack thug", player, state, [], [])
    result = resolve_defend(state, player)
    assert any("架開" in line and "戰術折刀" in line for line in result.lines)


def test_help_defend_desc_follows_equipment():
    player, state = _fighter()
    player.equipment["outer_torso"] = "jacket"
    player.equipment["head"] = "trainee_helmet"
    result = dispatch("help", player, state, [], [])
    defend_line = next(line for line in result.lines if "defend" in line)
    assert "護甲＋頭盔" in defend_line


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
    player.skills = ["quickhack"]
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    encounter.player_cd = 0
    before_ram = player.ram
    before_hp = encounter.npc_hp
    result = resolve_quickhack(state, player)
    assert player.ram == before_ram - 2
    assert encounter.npc_hp == before_hp - 10
    assert any("過熱" in line or "快速破解" in line for line in result.lines)


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


def test_combat_tick_cd_only_is_silent():
    player, state = _fighter()
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    encounter.npc_cd = 2
    encounter.player_cd = 1
    assert not process_combat_tick(state, [player])


def test_combat_tick_npc_counterattack():
    player, state = _fighter()
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    encounter.npc_cd = 0
    encounter.player_cd = 0
    before_hp = player.hp
    results = process_combat_tick(state, [player])
    assert results
    assert player.hp < before_hp


def test_victory_ends_combat():
    player, state = _fighter(body=50)
    player.equipment["weapon_secondary"] = "knife"
    result = dispatch("attack thug", player, state, [], [])
    assert not player.in_combat
    assert any("擊倒" in line for line in result.lines)
    assert result.world_changed


def test_npc_leaves_room_ends_combat_on_command():
    player, state = _fighter(room_id="alley")
    dispatch("attack thug", player, state, [], [])
    assert player.in_combat
    state.npc_rooms["thug"] = "square"
    result = resolve_defend(state, player)
    assert not player.in_combat
    assert result.ended
    assert any("離開" in line for line in result.lines)


def test_npc_patrol_ends_combat_on_tick():
    player, state = _fighter(room_id="alley")
    dispatch("attack thug", player, state, [], [])
    assert player.in_combat
    state.tick_count = PATROL_EVERY - 1
    with patch("world.tick.random.random", return_value=0.1):
        result = process_tick(state, state.time_config, players=[player])
    assert not player.in_combat
    assert result.combat_results
    _, combat_result = result.combat_results[0]
    assert combat_result.ended
    assert any("離開" in line for line in combat_result.lines)