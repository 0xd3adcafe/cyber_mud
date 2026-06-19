from __future__ import annotations

import random

from combat.actions import resolve_flee
from combat.encounter import encounter_for_player
from commands.helpers import quest_hint_for_player
from commands.registry import CommandContext, dispatch
from tests.conftest import make_player, make_state
from world.tick import process_tick


def _start_fight(player, state):
    dispatch("attack thug", player, state, [], [])
    return encounter_for_player(state, player)


def test_flee_fail_sets_chased_by_npc(monkeypatch):
    player = make_player(room_id="alley", name="V")
    state = make_state()
    _start_fight(player, state)
    monkeypatch.setattr(random, "random", lambda: 1.0)
    resolve_flee(state, player)
    assert player.chased_by_npc == "thug"
    from commands.registry import CommandContext, player_meta

    assert "追擊" in player_meta(CommandContext(player, state, "")).get("hint", "")


def test_flee_success_clears_chase(monkeypatch):
    player = make_player(room_id="alley", name="V")
    player.reflex = 10
    state = make_state()
    _start_fight(player, state)
    monkeypatch.setattr(random, "random", lambda: 0.0)
    resolve_flee(state, player)
    assert player.chased_by_npc == ""


def test_chase_restarts_combat_in_same_room(monkeypatch):
    player = make_player(room_id="alley", name="V")
    state = make_state()
    _start_fight(player, state)
    monkeypatch.setattr(random, "random", lambda: 1.0)
    resolve_flee(state, player)
    assert not player.in_combat
    assert player.chased_by_npc == "thug"
    state.npc_rooms["thug"] = "alley"
    process_tick(state, state.time_config, players=[player])
    assert player.in_combat
    assert encounter_for_player(state, player) is not None


def test_chase_follows_to_adjacent_room(monkeypatch):
    player = make_player(room_id="square", name="V")
    state = make_state()
    state.npc_rooms["thug"] = "alley"
    player.chased_by_npc = "thug"
    monkeypatch.setattr(random, "random", lambda: 0.0)
    result = process_tick(state, state.time_config, players=[player])
    assert state.npc_room("thug") == "square"
    assert any(event.kind == "chase_follow" for event in result.events)