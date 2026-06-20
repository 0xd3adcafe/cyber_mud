from __future__ import annotations

from commands.registry import dispatch
from entities.npc import NPC
from tests.conftest import make_player, make_state
from world.npc_respawn import (
    effective_respawn_minutes,
    respawn_ticks_for_npc,
    schedule_npc_respawn,
)
from world.tick import process_tick


def _killer():
    player = make_player(room_id="alley", name="Vy")
    player.body = 50
    player.equipment["weapon_secondary"] = "knife"
    return player, make_state()


def test_death_schedules_respawn():
    player, state = _killer()
    dispatch("attack thug", player, state, [], [])

    assert "thug" not in state.npc_rooms
    assert state.npc_respawns["thug"] == state.tick_count + 1


def test_npc_respawns_after_ticks():
    player, state = _killer()
    dispatch("attack thug", player, state, [], [])
    state.npc_respawns["thug"] = state.tick_count

    result = process_tick(state, state.time_config, players=[player])

    assert "thug" in state.npc_rooms
    assert "thug" not in state.npc_respawns
    assert any(event.kind == "npc_enter" and event.npc_id == "thug" for event in result.events)


def test_schedule_skips_missing_npc():
    state = make_state()
    schedule_npc_respawn(state, "phantom")
    assert "phantom" not in state.npc_respawns


def test_default_respawn_minutes():
    npc = NPC(id="mob")
    assert effective_respawn_minutes(npc) == 10
    assert respawn_ticks_for_npc(npc, make_state().time_config) == 1


def test_boss_tier_respawn_minutes():
    npc = NPC(id="boss", tier="boss")
    assert effective_respawn_minutes(npc) == 60
    assert respawn_ticks_for_npc(npc, make_state().time_config) == 6


def test_explicit_respawn_minutes_overrides_tier():
    npc = NPC(id="boss", tier="boss", respawn_minutes=15)
    assert effective_respawn_minutes(npc) == 15
    assert respawn_ticks_for_npc(npc, make_state().time_config) == 2