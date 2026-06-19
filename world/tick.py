from __future__ import annotations

import random
from dataclasses import dataclass, field

from combat.actions import CombatActionResult
from combat.tick import process_combat_tick
from entities.player import Player
from world.clock import TimeConfig
from world.state import WorldState
from world.weather import WeatherConfig, load_weather_config, maybe_tick_weather

PATROL_EVERY = 3
IDLE_EVERY = 6


@dataclass
class TickEvent:
    kind: str
    room_id: str = ""
    npc_id: str = ""
    npc_name_zh: str = ""
    npc_name_en: str = ""
    idle_msg_zh: str = ""
    idle_msg_en: str = ""
    district: str = ""
    weather: str = ""


@dataclass
class TickResult:
    time_changed: bool = False
    events: list[TickEvent] = field(default_factory=list)
    combat_results: list[tuple[Player, CombatActionResult]] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.time_changed


def _npc_name(npc, locale: str) -> str:
    return npc.name_zh if locale == "zh" else (npc.name_en or npc.name_zh)


def _maybe_move_patrolling_npcs(state: WorldState) -> list[TickEvent]:
    if state.tick_count % PATROL_EVERY != 0:
        return []

    events: list[TickEvent] = []
    for npc_id, npc in state.world.npcs.items():
        if len(npc.patrol) < 2:
            continue
        if random.random() > 0.5:
            continue

        current = state.npc_room(npc_id)
        if current not in npc.patrol:
            current = npc.patrol[0]
        idx = npc.patrol.index(current)
        next_room = npc.patrol[(idx + 1) % len(npc.patrol)]
        if next_room == current:
            continue

        state.npc_rooms[npc_id] = next_room
        events.append(
            TickEvent(
                kind="npc_leave",
                room_id=current,
                npc_id=npc_id,
                npc_name_zh=npc.name_zh,
                npc_name_en=npc.name_en,
            )
        )
        events.append(
            TickEvent(
                kind="npc_enter",
                room_id=next_room,
                npc_id=npc_id,
                npc_name_zh=npc.name_zh,
                npc_name_en=npc.name_en,
            )
        )
    return events


def _maybe_npc_idle_messages(state: WorldState) -> list[TickEvent]:
    if state.tick_count % IDLE_EVERY != 0:
        return []

    events: list[TickEvent] = []
    for npc_id, npc in state.world.npcs.items():
        if not npc.idle_msg_zh and not npc.idle_msg_en:
            continue
        if random.random() > 0.4:
            continue
        room_id = state.npc_room(npc_id)
        if not room_id:
            continue
        events.append(
            TickEvent(
                kind="npc_idle",
                room_id=room_id,
                npc_id=npc_id,
                npc_name_zh=npc.name_zh,
                npc_name_en=npc.name_en,
                idle_msg_zh=npc.idle_msg_zh,
                idle_msg_en=npc.idle_msg_en,
            )
        )
    return events


def process_tick(
    state: WorldState,
    config: TimeConfig,
    weather_config: WeatherConfig | None = None,
    *,
    players: list[Player] | None = None,
) -> TickResult:
    """Advance world clock and run periodic NPC/weather updates."""
    before = (state.clock.day, state.clock.hour, state.clock.minute)
    state.clock.advance(config.minutes_per_tick)
    after = (state.clock.day, state.clock.hour, state.clock.minute)
    time_changed = before != after

    state.tick_count += 1
    events: list[TickEvent] = []

    wcfg = weather_config or load_weather_config()
    for district in maybe_tick_weather(state, wcfg):
        events.append(
            TickEvent(
                kind="weather_change",
                district=district,
                weather=state.weather.get(district, ""),
            )
        )

    events.extend(_maybe_move_patrolling_npcs(state))
    events.extend(_maybe_npc_idle_messages(state))

    combat_results: list[tuple[Player, CombatActionResult]] = []
    if players:
        combat_results = process_combat_tick(state, players)

    return TickResult(time_changed=time_changed, events=events, combat_results=combat_results)