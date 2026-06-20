from __future__ import annotations

import random
from dataclasses import dataclass, field

from combat.actions import CombatActionResult
from combat.encounter import npc_label, start_encounter
from combat.tick import process_combat_departures
from entities.player import Player
from shared.i18n import t
from world.clock import TimeConfig
from world.corpses import process_corpse_decay
from world.npc_ai import process_npc_ai
from world.npc_respawn import process_npc_respawns
from world.schedule import npc_scheduled_room
from world.state import WorldState
from world.tick_events import TickEvent, move_npc
from world.vitals import apply_hp_regen, apply_ram_regen
from world.wanted import tick_wanted_decay
from world.weather import WeatherConfig, load_weather_config, maybe_tick_weather

PATROL_EVERY = 3
IDLE_EVERY = 6
CHASE_FOLLOW_CHANCE = 0.30


@dataclass
class TickResult:
    time_changed: bool = False
    events: list[TickEvent] = field(default_factory=list)
    combat_results: list[tuple[Player, CombatActionResult]] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.time_changed


def _npc_name(npc, locale: str) -> str:
    return npc.name_zh if locale == "zh" else (npc.name_en or npc.name_zh)


def _apply_npc_schedules(state: WorldState, config: TimeConfig) -> list[TickEvent]:
    period = state.clock.period_id(config)
    events: list[TickEvent] = []
    for npc_id, npc in state.world.npcs.items():
        if not npc.schedule:
            continue
        current = state.npc_room(npc_id)
        target = npc_scheduled_room(npc, period, current)
        events.extend(move_npc(state, npc_id, npc, current, target))
    return events


def _maybe_move_patrolling_npcs(state: WorldState, config: TimeConfig) -> list[TickEvent]:
    if state.tick_count % PATROL_EVERY != 0:
        return []

    period = state.clock.period_id(config)
    events: list[TickEvent] = []
    for npc_id, npc in state.world.npcs.items():
        if npc.schedule:
            continue
        if len(npc.patrol) < 2:
            continue
        current = state.npc_room(npc_id)
        room = state.world.room(current)
        from world.districts import patrol_move_chance

        if random.random() > patrol_move_chance(0.5, room, period_id=period):
            continue
        if current not in npc.patrol:
            current = npc.patrol[0]
        idx = npc.patrol.index(current)
        next_room = npc.patrol[(idx + 1) % len(npc.patrol)]
        events.extend(move_npc(state, npc_id, npc, current, next_room))
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


def _adjacent_room_toward_player(state: WorldState, npc_room_id: str, player_room_id: str) -> str | None:
    npc_room = state.world.room(npc_room_id)
    player_room = state.world.room(player_room_id)
    if npc_room is None or player_room is None:
        return None
    for dest in npc_room.exits.values():
        if dest == player_room_id:
            return dest
    for dest in npc_room.exits.values():
        dest_room = state.world.room(dest)
        if dest_room is None:
            continue
        for next_dest in dest_room.exits.values():
            if next_dest == player_room_id:
                return dest
    return None


def _process_chase(state: WorldState, players: list[Player]) -> list[TickEvent]:
    events: list[TickEvent] = []
    for player in players:
        if not player.chased_by_npc or player.in_combat:
            continue

        npc_id = player.chased_by_npc
        npc = state.world.npc(npc_id)
        if npc is None or not npc.hostile:
            player.chased_by_npc = ""
            continue

        npc_room_id = state.npc_room(npc_id)
        label = npc_label(state, npc_id, player.locale)

        if npc_room_id == player.room_id:
            encounter = start_encounter(state, player, npc_id)
            line = encounter.append_log(player.locale, "chase.restart", target=label)
            events.append(
                TickEvent(
                    kind="chase_restart",
                    room_id=player.room_id,
                    player_name=player.name,
                    npc_id=npc_id,
                    npc_name_zh=npc.name_zh,
                    npc_name_en=npc.name_en,
                    message_key="chase.restart",
                    message_kwargs={"target": label, "line": line},
                )
            )
            continue

        if random.random() < CHASE_FOLLOW_CHANCE:
            next_room = _adjacent_room_toward_player(state, npc_room_id, player.room_id)
            if next_room and next_room != npc_room_id:
                events.extend(move_npc(state, npc_id, npc, npc_room_id, next_room))
                events.append(
                    TickEvent(
                        kind="chase_follow",
                        room_id=player.room_id,
                        player_name=player.name,
                        npc_id=npc_id,
                        npc_name_zh=npc.name_zh,
                        npc_name_en=npc.name_en,
                        message_key="chase.follow",
                        message_kwargs={"target": label},
                    )
                )
    return events


def _process_player_trauma(state: WorldState, players: list[Player]) -> list[TickEvent]:
    from world.trauma import tick_player_status

    events: list[TickEvent] = []
    for player in players:
        if not player.named:
            continue
        lines = tick_player_status(player, player.locale)
        for line in lines:
            events.append(
                TickEvent(
                    kind="trauma_tick",
                    player_name=player.name,
                    message_key="",
                    message_kwargs={"text": line, "hp": str(player.hp)},
                )
            )
    return events


def _process_hp_regen(state: WorldState, config: TimeConfig, players: list[Player]) -> list[TickEvent]:
    period = state.clock.period_id(config)
    events: list[TickEvent] = []
    for player in players:
        if not player.named:
            continue
        amount = apply_hp_regen(player, period, state=state)
        ram_amount = apply_ram_regen(player, period, state=state)
        from world.life import apply_life_tick

        life_lines = apply_life_tick(player, state, period)
        if amount <= 0 and ram_amount <= 0 and not life_lines:
            continue
        events.append(
            TickEvent(
                kind="hp_regen",
                player_name=player.name,
                message_kwargs={
                    "amount": str(amount),
                    "ram_amount": str(ram_amount),
                    "hp": str(player.hp),
                    "max_hp": str(player.max_hp),
                    "ram": str(player.ram),
                    "max_ram": str(player.max_ram),
                    "life_lines": life_lines,
                },
            )
        )
    return events


def _process_wanted_decay(players: list[Player]) -> list[TickEvent]:
    events: list[TickEvent] = []
    for player in players:
        if not player.named or player.wanted_level <= 0:
            continue
        lines = tick_wanted_decay(player, player.locale)
        if not lines:
            continue
        events.append(
            TickEvent(
                kind="wanted_decay",
                player_name=player.name,
                message_key="wanted.tick",
                message_kwargs={"level": str(player.wanted_level), "text": lines[0]},
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

    for room_id, npc_id, name_zh, name_en in process_npc_respawns(state):
        events.append(
            TickEvent(
                kind="npc_enter",
                room_id=room_id,
                npc_id=npc_id,
                npc_name_zh=name_zh,
                npc_name_en=name_en,
            )
        )

    events.extend(_apply_npc_schedules(state, config))
    events.extend(_maybe_move_patrolling_npcs(state, config))
    events.extend(_maybe_npc_idle_messages(state))
    events.extend(process_npc_ai(state))

    if players:
        events.extend(_process_chase(state, players))
        events.extend(_process_hp_regen(state, config, players))
        events.extend(_process_player_trauma(state, players))
        events.extend(_process_wanted_decay(players))

    for room_id, message_key, message_kwargs in process_corpse_decay(state):
        events.append(
            TickEvent(
                kind="corpse_decay",
                room_id=room_id,
                message_key=message_key,
                message_kwargs=message_kwargs,
                corpse_decay=True,
            )
        )

    combat_results: list[tuple[Player, CombatActionResult]] = []
    if players:
        combat_results = process_combat_departures(state, players)

    return TickResult(time_changed=time_changed, events=events, combat_results=combat_results)