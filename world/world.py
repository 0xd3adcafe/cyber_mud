from __future__ import annotations

from dataclasses import dataclass, field

from entities.item import Item
from entities.npc import NPC


@dataclass
class Room:
    id: str
    name_zh: str = ""
    name_en: str = ""
    description_zh: str = ""
    description_en: str = ""
    district: str = ""
    exits: dict[str, str] = field(default_factory=dict)


@dataclass
class World:
    start_room: str
    rooms: dict[str, Room]
    items: dict[str, Item]
    npcs: dict[str, NPC]
    factions: dict[str, str]

    def room(self, room_id: str) -> Room | None:
        return self.rooms.get(room_id)

    def item(self, item_id: str) -> Item | None:
        return self.items.get(item_id)

    def npc(self, npc_id: str) -> NPC | None:
        return self.npcs.get(npc_id)