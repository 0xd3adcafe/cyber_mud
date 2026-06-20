from __future__ import annotations

from dataclasses import dataclass, field

from entities.npc import NPC
from world.state import WorldState


@dataclass
class TickEvent:
    kind: str
    room_id: str = ""
    npc_id: str = ""
    npc_name_zh: str = ""
    npc_name_en: str = ""
    idle_msg_zh: str = ""
    idle_msg_en: str = ""
    district: str = ""
    weather: str = ""
    player_name: str = ""
    message_key: str = ""
    message_kwargs: dict[str, str] = field(default_factory=dict)
    corpse_decay: bool = False


def move_npc(state: WorldState, npc_id: str, npc: NPC, from_room: str, to_room: str) -> list[TickEvent]:
    if not to_room or to_room == from_room:
        return []
    state.npc_rooms[npc_id] = to_room
    return [
        TickEvent(
            kind="npc_leave",
            room_id=from_room,
            npc_id=npc_id,
            npc_name_zh=npc.name_zh,
            npc_name_en=npc.name_en,
        ),
        TickEvent(
            kind="npc_enter",
            room_id=to_room,
            npc_id=npc_id,
            npc_name_zh=npc.name_zh,
            npc_name_en=npc.name_en,
        ),
    ]