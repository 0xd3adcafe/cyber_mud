from __future__ import annotations

import re

from entities.corpse import Corpse
from entities.player import Player
from shared.i18n import t
from shared.locale_content import command_name_suffix, label_with_command_suffix
from shared.names import matches_name
from world.npc_respawn import schedule_npc_respawn
from world.state import WorldState

CORPSE_DECAY_TICKS = 18
_CORPSE_ALIASES = ("corpse", "屍體", "body", "屍体")
_FROM_SPLIT = re.compile(r"\s+from\s+|\s+從\s+", re.IGNORECASE)


def _corpse_command_suffix(state: WorldState, corpse: Corpse) -> str:
    if corpse.player_name:
        return "corpse"
    npc = state.world.npc(corpse.npc_id)
    if npc is None:
        return corpse.npc_id or "corpse"
    return command_name_suffix(npc.name_en, corpse.npc_id)


def corpse_label(state: WorldState, corpse: Corpse, locale: str) -> str:
    if corpse.player_name:
        base = t(locale, "corpse.player_label", name=corpse.player_name)
        return label_with_command_suffix(base, _corpse_command_suffix(state, corpse))
    npc = state.world.npc(corpse.npc_id)
    if npc is None:
        name = corpse.npc_id
    elif locale == "en":
        name = npc.name_en or npc.name_zh or npc.id
    else:
        name = npc.name_zh or npc.id
    base = t(locale, "corpse.label", name=name)
    return label_with_command_suffix(base, _corpse_command_suffix(state, corpse))


def corpses_in_room(state: WorldState, room_id: str) -> list[Corpse]:
    return [corpse for corpse in state.corpses.values() if corpse.room_id == room_id]


def find_corpse_id(state: WorldState, name: str, room_id: str) -> str | None:
    needle = name.strip()
    if not needle:
        return None
    for corpse in corpses_in_room(state, room_id):
        if matches_name(needle, *_CORPSE_ALIASES):
            return corpse.id
        if corpse.player_name and matches_name(needle, corpse.player_name):
            return corpse.id
        npc = state.world.npc(corpse.npc_id)
        if npc and matches_name(needle, corpse.npc_id, npc.name_zh, npc.name_en):
            return corpse.id
        label = corpse_label(state, corpse, "zh")
        if matches_name(needle, label):
            return corpse.id
        label_en = corpse_label(state, corpse, "en")
        if matches_name(needle, label_en):
            return corpse.id
    return None


def _collect_npc_loot(npc) -> list[str]:
    loot: list[str] = list(npc.loot)
    for item_id in npc.equipment.values():
        if item_id and item_id not in loot:
            loot.append(item_id)
    return loot


def spawn_corpse(state: WorldState, npc_id: str, room_id: str) -> Corpse | None:
    npc = state.world.npc(npc_id)
    if npc is None or not room_id:
        return None
    state.npc_rooms.pop(npc_id, None)
    schedule_npc_respawn(state, npc_id)
    corpse_id = f"{npc_id}_corpse"
    corpse = Corpse(
        id=corpse_id,
        npc_id=npc_id,
        room_id=room_id,
        loot=_collect_npc_loot(npc),
        decay_at_tick=state.tick_count + CORPSE_DECAY_TICKS,
    )
    state.corpses[corpse_id] = corpse
    return corpse


def _player_corpse_id(player_name: str) -> str:
    return f"{player_name}_corpse"


def _collect_player_loot(player: Player) -> list[str]:
    loot: list[str] = []
    for item_id in player.inventory:
        if item_id:
            loot.append(item_id)
    for item_id in player.equipment.values():
        if item_id and item_id not in loot:
            loot.append(item_id)
    return loot


def _strip_player_loot(player: Player, loot: list[str]) -> None:
    dropped = set(loot)
    player.inventory = [item_id for item_id in player.inventory if item_id not in dropped]
    for slot, item_id in list(player.equipment.items()):
        if item_id in dropped:
            player.equipment[slot] = ""
    player.weapon_mods = {
        item_id: mods for item_id, mods in player.weapon_mods.items() if item_id not in dropped
    }


def spawn_player_corpse(state: WorldState, player: Player, room_id: str) -> Corpse | None:
    if not player.name or not room_id:
        return None
    corpse_id = _player_corpse_id(player.name)
    state.corpses.pop(corpse_id, None)
    loot = _collect_player_loot(player)
    _strip_player_loot(player, loot)
    corpse = Corpse(
        id=corpse_id,
        npc_id="",
        player_name=player.name,
        room_id=room_id,
        loot=loot,
        decay_at_tick=state.tick_count + CORPSE_DECAY_TICKS,
    )
    state.corpses[corpse_id] = corpse
    return corpse


def split_take_from(args: str) -> tuple[str, str | None]:
    parts = _FROM_SPLIT.split(args.strip(), maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return args.strip(), None


def ticks_until_decay(state: WorldState, corpse: Corpse) -> int:
    return max(0, corpse.decay_at_tick - state.tick_count)


def decay_time_label(state: WorldState, corpse: Corpse, locale: str) -> str:
    ticks = ticks_until_decay(state, corpse)
    minutes = ticks * state.time_config.minutes_per_tick
    if minutes <= 0:
        return ""
    if minutes < 60:
        return t(locale, "corpse.time_minutes", minutes=str(minutes))
    hours = minutes // 60
    remain = minutes % 60
    if remain:
        return t(locale, "corpse.time_hours_minutes", hours=str(hours), minutes=str(remain))
    return t(locale, "corpse.time_hours", hours=str(hours))


def process_corpse_decay(state: WorldState) -> list[tuple[str, str, dict[str, str]]]:
    """Return (room_id, locale_key, kwargs) tuples for decayed corpses."""
    events: list[tuple[str, str, dict[str, str]]] = []
    doomed: list[str] = []
    for corpse_id, corpse in state.corpses.items():
        if state.tick_count < corpse.decay_at_tick:
            continue
        if corpse.loot:
            pool = state.room_items.setdefault(corpse.room_id, [])
            pool.extend(corpse.loot)
        label_zh = corpse_label(state, corpse, "zh")
        label_en = corpse_label(state, corpse, "en")
        events.append(
            (
                corpse.room_id,
                "corpse.decay",
                {"label_zh": label_zh, "label_en": label_en},
            )
        )
        doomed.append(corpse_id)
    for corpse_id in doomed:
        state.corpses.pop(corpse_id, None)
    return events