from __future__ import annotations

from combat.actions import resolve_npc_attack
from combat.encounter import encounter_for_player
from combat.tick import process_combat_tick
from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.corpses import corpses_in_room


def _victim():
    player = make_player(room_id="alley", name="V")
    player.hp = 1
    player.inventory = ["glowstick"]
    player.equipment["weapon_secondary"] = "knife"
    return player, make_state()


def test_player_death_spawns_corpse_and_respawns():
    player, state = _victim()
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    encounter.npc_cd = 0

    result = resolve_npc_attack(state, player, encounter)

    assert not player.in_combat
    assert player.room_id == "ripper_clinic"
    assert player.hp == player.max_hp
    assert player.inventory == []
    assert not player.equipment.get("weapon_primary") and not player.equipment.get("weapon_secondary")
    assert result.moved
    assert result.world_changed
    corpses = corpses_in_room(state, "alley")
    assert len(corpses) == 1
    assert corpses[0].player_name == "V"
    assert "glowstick" in corpses[0].loot
    assert "knife" in corpses[0].loot
    assert any("義體診所" in line for line in result.lines)
    assert any("屍體" in line for line in result.lines)


def test_player_death_via_combat_tick():
    player, state = _victim()
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    encounter.npc_cd = 0
    encounter.player_cd = 0

    results = process_combat_tick(state, [player])

    assert results
    assert player.room_id == "ripper_clinic"
    assert "V_corpse" in state.corpses


def test_other_player_can_loot_player_corpse():
    victim, state = _victim()
    looter = make_player(room_id="alley", name="X")
    dispatch("attack thug", victim, state, [], [])
    encounter = encounter_for_player(state, victim)
    assert encounter is not None
    encounter.npc_cd = 0
    resolve_npc_attack(state, victim, encounter)

    result = dispatch("take knife from V", looter, state, [victim], [victim, looter])

    assert "knife" in looter.inventory
    assert "knife" not in state.corpses["V_corpse"].loot
    assert result.world_changed