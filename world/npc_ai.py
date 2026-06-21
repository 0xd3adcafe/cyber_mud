from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from entities.npc import NPC
from entities.player import Player
from shared.i18n import t
from shared.locale_content import npc_label_with_id
from world.npc_respawn import schedule_npc_respawn
from world.profiler import is_profiled, profiler_entry
from world.state import WorldState
from world.tick_events import TickEvent, move_npc

JAM_RAM_COST = 1
DISTRACT_TICKS = 2
JAM_TICKS = 2
RESIST_TICKS = 1

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "npc_ai.yaml"
NPC_AI_EVERY = 4


@dataclass
class NpcAiConfig:
    faction_rivals: dict[str, list[str]] = field(default_factory=dict)
    motivation_fight_chance: dict[str, float] = field(default_factory=dict)
    motivation_social_chance: dict[str, float] = field(default_factory=dict)


def load_npc_ai_config(path: Path | None = None) -> NpcAiConfig:
    src = path or DATA_PATH
    if not src.exists():
        return NpcAiConfig()
    with src.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return NpcAiConfig(
        faction_rivals={str(k): [str(v) for v in vals] for k, vals in (raw.get("faction_rivals") or {}).items()},
        motivation_fight_chance={str(k): float(v) for k, v in (raw.get("motivation_fight_chance") or {}).items()},
        motivation_social_chance={str(k): float(v) for k, v in (raw.get("motivation_social_chance") or {}).items()},
    )


def npc_current_hp(state: WorldState, npc_id: str) -> int:
    npc = state.world.npc(npc_id)
    if npc is None:
        return 0
    return state.npc_vitals.get(npc_id, npc.hp)


def reset_npc_hp(state: WorldState, npc_id: str) -> None:
    state.npc_vitals.pop(npc_id, None)


def _npc_busy_with_player(state: WorldState, npc_id: str) -> bool:
    for encounter in state.encounters.values():
        if encounter.npc_id == npc_id:
            return True
    return False


def _active_npc_ids(state: WorldState) -> list[str]:
    return [npc_id for npc_id in state.npc_rooms if npc_id not in state.npc_respawns]


def factions_rival(config: NpcAiConfig, faction_a: str, faction_b: str) -> bool:
    if not faction_a or not faction_b or faction_a == faction_b:
        return False
    rivals_a = set(config.faction_rivals.get(faction_a, []))
    rivals_b = set(config.faction_rivals.get(faction_b, []))
    return faction_b in rivals_a or faction_a in rivals_b


def _fight_chance(config: NpcAiConfig, npc_a: NPC, npc_b: NPC) -> float:
    chances = []
    for npc in (npc_a, npc_b):
        if npc.motivation:
            chances.append(config.motivation_fight_chance.get(npc.motivation, 0.2))
        elif npc.hostile:
            chances.append(0.4)
    if npc_a.hostile and npc_b.hostile:
        chances.append(0.5)
    return min(0.95, max(chances) if chances else 0.2)


def _social_chance(config: NpcAiConfig, npc: NPC) -> float:
    if not npc.motivation:
        return 0.0
    return config.motivation_social_chance.get(npc.motivation, 0.0)


def _social_msg_key(npc: NPC) -> str:
    if npc.motivation:
        return f"npc.ai.msg.{npc.motivation}"
    return "npc.ai.msg.socialize"


def _knock_out_npc(state: WorldState, npc_id: str) -> None:
    state.npc_rooms.pop(npc_id, None)
    reset_npc_hp(state, npc_id)
    schedule_npc_respawn(state, npc_id)


def _resolve_brawl(
    state: WorldState,
    attacker_id: str,
    defender_id: str,
    room_id: str,
    *,
    roll: float,
) -> TickEvent | None:
    attacker = state.world.npc(attacker_id)
    defender = state.world.npc(defender_id)
    if attacker is None or defender is None:
        return None

    dmg = max(1, attacker.attack + (1 if roll < 0.5 else 0))
    remaining = npc_current_hp(state, defender_id) - dmg
    state.npc_vitals[defender_id] = max(0, remaining)

    if remaining <= 0:
        _knock_out_npc(state, defender_id)
        return TickEvent(
            kind="npc_ai_defeat",
            room_id=room_id,
            npc_id=defender_id,
            npc_name_zh=defender.name_zh,
            npc_name_en=defender.name_en,
            message_key="npc.ai.defeat",
            message_kwargs={
                "winner_zh": attacker.name_zh,
                "winner_en": attacker.name_en or attacker.name_zh,
                "loser_zh": defender.name_zh,
                "loser_en": defender.name_en or defender.name_zh,
                "damage": str(dmg),
            },
        )

    return TickEvent(
        kind="npc_ai_fight",
        room_id=room_id,
        npc_id=attacker_id,
        npc_name_zh=attacker.name_zh,
        npc_name_en=attacker.name_en,
        message_key="npc.ai.fight",
        message_kwargs={
            "attacker_zh": attacker.name_zh,
            "attacker_en": attacker.name_en or attacker.name_zh,
            "defender_zh": defender.name_zh,
            "defender_en": defender.name_en or defender.name_zh,
            "damage": str(dmg),
            "hp": str(remaining),
        },
    )


def _try_pair_interaction(
    state: WorldState,
    config: NpcAiConfig,
    npc_a_id: str,
    npc_b_id: str,
    room_id: str,
    *,
    roll: float,
) -> TickEvent | None:
    npc_a = state.world.npc(npc_a_id)
    npc_b = state.world.npc(npc_b_id)
    if npc_a is None or npc_b is None:
        return None

    if factions_rival(config, npc_a.faction, npc_b.faction):
        chance = _fight_chance(config, npc_a, npc_b)
        if roll < chance:
            aggressor = npc_a_id
            target = npc_b_id
            if npc_b.motivation == "hunt_rival" and npc_a.motivation != "hunt_rival":
                aggressor, target = npc_b_id, npc_a_id
            elif npc_b.hostile and not npc_a.hostile:
                aggressor, target = npc_b_id, npc_a_id
            return _resolve_brawl(state, aggressor, target, room_id, roll=roll)

    if npc_a.faction and npc_a.faction == npc_b.faction and roll < _social_chance(config, npc_a):
        speaker = npc_a if npc_a.motivation == "socialize" else npc_b
        target = npc_b if speaker is npc_a else npc_a
        return TickEvent(
            kind="npc_ai_social",
            room_id=room_id,
            npc_id=speaker.id,
            npc_name_zh=speaker.name_zh,
            npc_name_en=speaker.name_en,
            message_key=_social_msg_key(speaker),
            message_kwargs={
                "speaker_zh": speaker.name_zh,
                "speaker_en": speaker.name_en or speaker.name_zh,
                "target_zh": target.name_zh,
                "target_en": target.name_en or target.name_zh,
            },
        )

    for speaker, target in ((npc_a, npc_b), (npc_b, npc_a)):
        if speaker.motivation == "trade" and roll < _social_chance(config, speaker):
            return TickEvent(
                kind="npc_ai_social",
                room_id=room_id,
                npc_id=speaker.id,
                npc_name_zh=speaker.name_zh,
                npc_name_en=speaker.name_en,
                message_key=_social_msg_key(speaker),
                message_kwargs={
                    "speaker_zh": speaker.name_zh,
                    "speaker_en": speaker.name_en or speaker.name_zh,
                    "target_zh": target.name_zh,
                    "target_en": target.name_en or target.name_zh,
                },
            )

    return None


def _nearest_rival_room(state: WorldState, config: NpcAiConfig, npc: NPC, current_room: str) -> str | None:
    if npc.motivation != "hunt_rival" or not npc.faction:
        return None
    for other_id, other_room in state.npc_rooms.items():
        if other_id == npc.id or not other_room or other_room == current_room:
            continue
        other = state.world.npc(other_id)
        if other is None or not factions_rival(config, npc.faction, other.faction):
            continue
        return other_room
    return None


def _maybe_hunt_move(state: WorldState, config: NpcAiConfig, *, roll: float) -> list[TickEvent]:
    if roll > 0.6:
        return []
    events: list[TickEvent] = []
    for npc_id in _active_npc_ids(state):
        if _npc_busy_with_player(state, npc_id):
            continue
        npc = state.world.npc(npc_id)
        if npc is None or npc.motivation != "hunt_rival":
            continue
        current = state.npc_room(npc_id)
        target_room = _nearest_rival_room(state, config, npc, current)
        if not target_room or target_room == current:
            continue
        room = state.world.room(current)
        if room is None:
            continue
        for dest in room.exits.values():
            if dest == target_room:
                events.extend(move_npc(state, npc_id, npc, current, dest))
                events.append(
                    TickEvent(
                        kind="npc_ai_hunt",
                        room_id=current,
                        npc_id=npc_id,
                        npc_name_zh=npc.name_zh,
                        npc_name_en=npc.name_en,
                        message_key="npc.ai.hunt",
                        message_kwargs={
                            "name_zh": npc.name_zh,
                            "name_en": npc.name_en or npc.name_zh,
                        },
                    )
                )
                break
    return events


def has_security_detail_resistance(player: Player, npc_id: str) -> bool:
    if not is_profiled(player, npc_id):
        return False
    profile = profiler_entry(npc_id)
    return profile is not None and "security_detail" in profile.traits


def tick_npc_distract(state: WorldState) -> None:
    for store in (state.npc_patrol_jam, state.npc_aggro_distract):
        for npc_id in list(store.keys()):
            store[npc_id] -= 1
            if store[npc_id] <= 0:
                store.pop(npc_id, None)


def patrol_is_jammed(state: WorldState, npc_id: str) -> bool:
    return state.npc_patrol_jam.get(npc_id, 0) > 0


def aggro_is_suppressed(state: WorldState, npc_id: str) -> bool:
    return state.npc_aggro_distract.get(npc_id, 0) > 0


def _effect_ticks(player: Player, npc_id: str, base: int) -> tuple[int, bool]:
    if has_security_detail_resistance(player, npc_id):
        return RESIST_TICKS, True
    return base, False


def try_jam_npc(player: Player, state: WorldState, npc_id: str, locale: str) -> list[str]:
    npc = state.world.npc(npc_id)
    if npc is None:
        return [t(locale, "ctos.distract.missing", name=npc_id)]
    label = npc_label_with_id(npc, locale)
    if len(npc.patrol) < 2:
        return [t(locale, "ctos.distract.no_patrol", name=label)]
    if player.ram < JAM_RAM_COST:
        return [t(locale, "ctos.distract.need_ram", cost=str(JAM_RAM_COST))]

    player.ram -= JAM_RAM_COST
    ticks, resisted = _effect_ticks(player, npc_id, JAM_TICKS)
    state.npc_patrol_jam[npc_id] = ticks
    lines = [t(locale, "ctos.distract.jam_ok", name=label, ticks=str(ticks))]
    if resisted:
        lines.append(t(locale, "ctos.distract.resisted", name=label))
    from world.life import gain_fatigue

    gain_fatigue(player, "netrun")
    return lines


def try_distract_npc(player: Player, state: WorldState, npc_id: str, locale: str) -> list[str]:
    npc = state.world.npc(npc_id)
    if npc is None:
        return [t(locale, "ctos.distract.missing", name=npc_id)]
    label = npc_label_with_id(npc, locale)
    if not npc.hostile or npc.aggro <= 0:
        return [t(locale, "ctos.distract.no_aggro", name=label)]

    ticks, resisted = _effect_ticks(player, npc_id, DISTRACT_TICKS)
    state.npc_aggro_distract[npc_id] = ticks
    if player.chased_by_npc == npc_id:
        player.chased_by_npc = ""
    lines = [t(locale, "ctos.distract.distract_ok", name=label, ticks=str(ticks))]
    if resisted:
        lines.append(t(locale, "ctos.distract.resisted", name=label))
    return lines


def process_npc_ai(state: WorldState, config: NpcAiConfig | None = None, *, roll: float | None = None) -> list[TickEvent]:
    if state.tick_count % NPC_AI_EVERY != 0:
        return []
    cfg = config or load_npc_ai_config()
    rng = roll if roll is not None else random.random()
    events: list[TickEvent] = []

    by_room: dict[str, list[str]] = {}
    for npc_id in _active_npc_ids(state):
        if _npc_busy_with_player(state, npc_id):
            continue
        npc = state.world.npc(npc_id)
        if npc is None or (not npc.faction and not npc.motivation):
            continue
        room_id = state.npc_room(npc_id)
        by_room.setdefault(room_id, []).append(npc_id)

    for room_id, npc_ids in by_room.items():
        if len(npc_ids) < 2:
            continue
        sorted_ids = sorted(npc_ids)
        for idx, npc_a_id in enumerate(sorted_ids):
            for npc_b_id in sorted_ids[idx + 1 :]:
                event = _try_pair_interaction(state, cfg, npc_a_id, npc_b_id, room_id, roll=rng)
                if event is not None:
                    events.append(event)
                    if event.kind == "npc_ai_defeat":
                        events.append(
                            TickEvent(
                                kind="npc_leave",
                                room_id=room_id,
                                npc_id=event.npc_id,
                                npc_name_zh=event.npc_name_zh,
                                npc_name_en=event.npc_name_en,
                            )
                        )
                    break
            if events and events[-1].room_id == room_id:
                break

    events.extend(_maybe_hunt_move(state, cfg, roll=rng))
    return events