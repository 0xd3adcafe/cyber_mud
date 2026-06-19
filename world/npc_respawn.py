from __future__ import annotations

from entities.npc import NPC
from world.clock import TimeConfig
from world.schedule import npc_scheduled_room
from world.state import WorldState

DEFAULT_RESPAWN_MINUTES = 10
TIER_RESPAWN_MINUTES: dict[str, int] = {
    "boss": 60,
}


def effective_respawn_minutes(npc: NPC) -> int:
    if npc.respawn_minutes is not None:
        return max(1, npc.respawn_minutes)
    tier_minutes = TIER_RESPAWN_MINUTES.get(npc.tier)
    if tier_minutes is not None:
        return tier_minutes
    return DEFAULT_RESPAWN_MINUTES


def respawn_ticks_for_npc(npc: NPC, config: TimeConfig) -> int:
    minutes = effective_respawn_minutes(npc)
    minutes_per_tick = max(1, config.minutes_per_tick)
    return max(1, -(-minutes // minutes_per_tick))


def schedule_npc_respawn(state: WorldState, npc_id: str) -> None:
    npc = state.world.npc(npc_id)
    if npc is None:
        return
    ticks = respawn_ticks_for_npc(npc, state.time_config)
    state.npc_respawns[npc_id] = state.tick_count + ticks


def respawn_room(state: WorldState, npc: NPC) -> str:
    period = state.clock.period_id(state.time_config)
    fallback = npc.room_id
    if not fallback and npc.patrol:
        fallback = npc.patrol[0]
    return npc_scheduled_room(npc, period, fallback)


def process_npc_respawns(state: WorldState) -> list[tuple[str, str, str, str]]:
    """Return (room_id, npc_id, name_zh, name_en) for each respawned NPC."""
    events: list[tuple[str, str, str, str]] = []
    ready: list[str] = []
    for npc_id, respawn_at in state.npc_respawns.items():
        if state.tick_count < respawn_at:
            continue
        if npc_id in state.npc_rooms:
            ready.append(npc_id)
            continue
        npc = state.world.npc(npc_id)
        if npc is None:
            ready.append(npc_id)
            continue
        room_id = respawn_room(state, npc)
        if not room_id:
            ready.append(npc_id)
            continue
        state.npc_rooms[npc_id] = room_id
        events.append((room_id, npc_id, npc.name_zh, npc.name_en))
        ready.append(npc_id)
    for npc_id in ready:
        state.npc_respawns.pop(npc_id, None)
    return events