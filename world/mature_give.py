from __future__ import annotations

from entities.player import Player
from world.mature import is_mature
from world.mature_social import _resolved_tm
from world.romance import load_romance_profiles, profile_for_npc


def romance_gift_line(player: Player, npc_id: str, item_id: str, locale: str) -> str | None:
    if not is_mature(player):
        return None
    profiles = load_romance_profiles()
    if profile_for_npc(profiles, npc_id) is None:
        return None
    for key in (f"give.{npc_id}.{item_id}", f"give.{npc_id}.default"):
        if line := _resolved_tm(locale, key):
            return line
    return None