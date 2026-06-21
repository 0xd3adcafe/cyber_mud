from __future__ import annotations

from entities.player import Player
from shared.i18n import t
from world.state import WorldState
from world.world import NPC


def peers_in_room(state: WorldState, room_id: str, npc_id: str) -> list[str]:
    return [nid for nid in state.npcs_in_room(room_id) if nid != npc_id]


def peer_talk_key(npc: NPC, peer_ids: tuple[str, ...]) -> str:
    base = npc.talk_key or npc.id
    if not peer_ids:
        return base
    suffix = "_".join(sorted(peer_ids))
    return f"{base}_peers_{suffix}"


def resolve_bb_talk_line(
    player: Player,
    state: WorldState,
    npc: NPC,
    npc_id: str,
    locale: str,
) -> str:
    peer_ids = tuple(sorted(peers_in_room(state, player.room_id, npc_id)))
    if peer_ids:
        key = peer_talk_key(npc, peer_ids)
        line = t(locale, f"talk.{key}")
        if line != f"talk.{key}":
            return line
    return ""


def bouncer_talk_key(player: Player, npc: NPC) -> str:
    base = npc.talk_key or npc.id
    if player.wanted_level >= 3:
        return f"{base}_wanted_high"
    if player.wanted_level >= 1:
        return f"{base}_wanted"
    if player.street_cred >= 15:
        return f"{base}_cred_high"
    if player.street_cred >= 8:
        return f"{base}_cred"
    return base