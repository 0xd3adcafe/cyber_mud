from __future__ import annotations

import random

from entities.player import Player
from shared.i18n import t
from shared.mature_i18n import tm
from world.mature import has_mature_tag, is_mature
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
            if key and (line := _resolved_tm(locale, key, **kwargs)):
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
    index = random.randint(1, 3)
    return f"combat.{event}_broadcast_{index}"


def random_mature_taunt_line(locale: str, *, target: str) -> str | None:
    key = f"combat.taunt_{random.randint(1, 3)}"
    return _resolved_tm(locale, key, target=target)


def random_mature_finish_line(locale: str, *, target: str) -> str | None:
    key = f"combat.finish_{random.randint(1, 3)}"
    return _resolved_tm(locale, key, target=target)