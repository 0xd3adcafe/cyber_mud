from __future__ import annotations

import random

from entities.player import Player
from shared.i18n import t
from shared.mature_i18n import tm
from world.mature import has_mature_tag, is_mature
from world.mature_voice import mature_combat_key_line, mature_combat_line
from world.world import Room

MATURE_PRESENCE_ROOMS = frozenset(
    {
        "kabuki_lounge",
        "kabuki_vip",
        "bd_den",
    }
)


def _resolved_tm(locale: str, key: str, **kwargs: str) -> str | None:
    line = tm(locale, key, **kwargs)
    bare = key.removeprefix("mature.")
    if not line or line == key or line == bare:
        return None
    return line


def localized_broadcast_line(
    player: Player,
    default_key: str,
    *,
    mature_key: str = "",
    mature_fallback_key: str = "",
    **kwargs: str,
) -> str:
    locale = player.locale
    if mature_key and is_mature(player):
        for key in (mature_key, mature_fallback_key):
            if not key:
                continue
            if key.startswith("combat."):
                if line := mature_combat_key_line(locale, key, **kwargs):
                    return line
                continue
            if line := _resolved_tm(locale, key, **kwargs):
                return line
    return t(locale, default_key, **kwargs)


def mature_room(room: Room | None) -> bool:
    return room is not None and has_mature_tag(room.tags)


def mature_say_self_line(locale: str, room_id: str, message: str) -> str | None:
    for key in (f"social.say_ok.{room_id}", "social.say_ok.default"):
        if line := _resolved_tm(locale, key, message=message):
            return line
    return None


def mature_say_broadcast_keys(room_id: str) -> tuple[str, str]:
    return (
        f"social.say_broadcast.{room_id}",
        "social.say_broadcast.default",
    )


def mature_presence_broadcast_keys(room_id: str, event: str) -> tuple[str, str]:
    return (
        f"social.presence_{event}.{room_id}",
        f"social.presence_{event}.default",
    )


def presence_mature_key_for_room(room_id: str, event: str) -> str:
    if room_id not in MATURE_PRESENCE_ROOMS:
        return ""
    return mature_presence_broadcast_keys(room_id, event)[0]


def random_mature_combat_broadcast(event: str) -> str:
    from world.mature_voice import COMBAT_LINE_COUNTS

    pool = f"{event}_broadcast"
    count = COMBAT_LINE_COUNTS.get(pool, 3)
    index = random.randint(1, count)
    return f"combat.{event}_broadcast_{index}"


def random_mature_taunt_line(locale: str, *, target: str) -> str | None:
    return mature_combat_line(locale, "taunt", target=target)


def random_mature_finish_line(locale: str, *, target: str) -> str | None:
    return mature_combat_line(locale, "finish", target=target)