from __future__ import annotations

import random

from entities.npc import NPC
from entities.player import Player
from shared.i18n import t
from world.state import WorldState

REPUTATION_MIN = -20
REPUTATION_MAX = 100

PLEDGE_REPUTATION: dict[str, int] = {
    "arasaka": 5,
    "militech": 4,
    "tyrell": 6,
    "maelstrom": -3,
    "dedsec": 5,
}


def shift_reputation(player: Player, delta: int, locale: str) -> list[str]:
    if delta == 0:
        return []
    before = player.reputation
    player.reputation = max(REPUTATION_MIN, min(REPUTATION_MAX, player.reputation + delta))
    if player.reputation == before:
        return []
    change = player.reputation - before
    sign = f"+{change}" if change > 0 else str(change)
    return [t(locale, "reputation.shift", rep=str(player.reputation), delta=sign)]


def reputation_from_pledge(faction_id: str) -> int:
    return PLEDGE_REPUTATION.get(faction_id, 2)


def reputation_from_quickhack() -> int:
    return 1


def reputation_from_net_hack() -> int:
    return 2


def reputation_from_combat_victory(npc: NPC | None) -> int:
    if npc is None:
        return 1
    if npc.faction in {"arasaka", "militech", "tyrell"}:
        return -2
    if npc.hostile:
        return 2
    return 1


def broker_talk_extra(player: Player, npc_id: str, locale: str) -> str | None:
    if npc_id != "broker":
        return None
    if player.reputation >= 20:
        line = t(locale, "talk.broker_rep_high")
        return line if line != "talk.broker_rep_high" else None
    if player.reputation <= -5:
        line = t(locale, "talk.broker_rep_low")
        return line if line != "talk.broker_rep_low" else None
    if player.wanted_level >= 2:
        line = t(locale, "talk.broker_wanted", level=str(player.wanted_level))
        return line if line != "talk.broker_wanted" else None
    return None


def ambient_tick_line(player: Player, state: WorldState, period_id: str, locale: str) -> str | None:
    if random.random() > 0.22:
        return None
    room = state.world.room(player.room_id)
    if room is None:
        return None
    if player.wanted_level >= 2:
        line = t(locale, "world.ambient.wanted", level=str(player.wanted_level))
        if line != "world.ambient.wanted":
            return line
    if player.faction and room.district == "corpo":
        key = f"world.ambient.faction_{player.faction}"
        line = t(locale, key)
        if line != key:
            return line
    if room.district:
        key = f"world.ambient.{room.district}"
        line = t(locale, key)
        if line != key:
            return line
    key = f"world.ambient.period_{period_id}"
    line = t(locale, key)
    return line if line != key else None