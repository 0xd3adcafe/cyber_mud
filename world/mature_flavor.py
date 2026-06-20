from __future__ import annotations

from entities.player import Player
from shared.mature_i18n import tm
from world.mature import has_mature_tag, is_mature
from world.world import Room

MATURE_ROOM_KEYS = frozenset(
    {
        "kabuki_lounge",
        "kabuki_vip",
        "bd_den",
    }
)

MATURE_NPC_KEYS = frozenset(
    {
        "kabuki_host",
        "kabuki_bouncer",
        "kabuki_dancer",
        "bd_den_clerk",
    }
)


def _resolved_line(locale: str, key: str) -> str | None:
    line = tm(locale, key)
    bare = key.removeprefix("mature.")
    if not line or line == bare or line == key:
        return None
    return line


def mature_room_flavor(room: Room | None, player: Player) -> str | None:
    if room is None or not is_mature(player) or not has_mature_tag(room.tags):
        return None
    if room.id not in MATURE_ROOM_KEYS:
        return None
    return _resolved_line(player.locale, f"room.{room.id}")


def mature_npc_detail(npc_id: str, player: Player) -> str | None:
    if not is_mature(player) or npc_id not in MATURE_NPC_KEYS:
        return None
    return _resolved_line(player.locale, f"npc.{npc_id}")


def romance_stage_suffix(tier: int) -> str:
    if tier >= 3:
        return "_3"
    if tier >= 2:
        return "_2"
    return ""


def romance_line(locale: str, base_key: str, tier: int) -> str:
    suffix = romance_stage_suffix(tier)
    for key in (f"romance.{base_key}{suffix}", f"romance.{base_key}"):
        line = _resolved_line(locale, key)
        if line:
            return line
    return tm(locale, f"romance.{base_key}")