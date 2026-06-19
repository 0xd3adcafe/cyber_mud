from __future__ import annotations

from combat.actions import CombatActionResult, resolve_npc_departed, tick_encounter
from combat.encounter import npc_in_player_room
from entities.player import Player
from world.state import WorldState


def process_combat_departures(
    state: WorldState,
    players: list[Player],
) -> list[tuple[Player, CombatActionResult]]:
    results: list[tuple[Player, CombatActionResult]] = []
    if not state.encounters:
        return results

    for encounter_id in list(state.encounters.keys()):
        encounter = state.encounters.get(encounter_id)
        if encounter is None:
            continue
        player = next((p for p in players if p.name == encounter.player_name), None)
        if player is None:
            state.encounters.pop(encounter_id, None)
            continue
        if not npc_in_player_room(state, player, encounter):
            results.append((player, resolve_npc_departed(state, player, encounter)))
    return results


def process_combat_tick(state: WorldState, players: list[Player]) -> list[tuple[Player, CombatActionResult]]:
    results: list[tuple[Player, CombatActionResult]] = []
    if not state.encounters:
        return results

    encounter_ids = list(state.encounters.keys())
    for encounter_id in encounter_ids:
        encounter = state.encounters.get(encounter_id)
        if encounter is None:
            continue
        player = next((p for p in players if p.name == encounter.player_name), None)
        if player is None:
            state.encounters.pop(encounter_id, None)
            continue
        action = tick_encounter(state, encounter, players)
        if action is not None and (action.lines or action.world_changed):
            results.append((player, action))
    return results