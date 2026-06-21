from __future__ import annotations

from entities.player import Player
from shared.mature_i18n import tm
from world.mature import has_mature_tag, is_mature
from world.mature_voice import mature_voice_line
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
    if tier >= 5:
        return "_5"
    if tier >= 4:
        return "_4"
    if tier >= 3:
        return "_3"
    if tier >= 2:
        return "_2"
    return ""


def _voice_line_ok(line: str, stem: str) -> bool:
    if not line:
        return False
    if line == stem or line.endswith(stem):
        return False
    return not line.startswith(f"{stem}.")


def romance_line(locale: str, base_key: str, tier: int, *, voice: str = "noir") -> str:
    suffix = romance_stage_suffix(tier)
    for key in (f"romance.{base_key}{suffix}", f"romance.{base_key}"):
        line = mature_voice_line(locale, key, voice)
        if _voice_line_ok(line, key):
            return line
    return mature_voice_line(locale, f"romance.{base_key}", voice)


def scene_line(locale: str, base_key: str, tier: int, *, voice: str = "noir") -> str:
    suffix = romance_stage_suffix(tier)
    for key in (f"scene.{base_key}{suffix}", f"scene.{base_key}"):
        line = mature_voice_line(locale, key, voice)
        if _voice_line_ok(line, key):
            return line
    return mature_voice_line(locale, f"scene.{base_key}", voice)