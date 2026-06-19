from __future__ import annotations

from dataclasses import dataclass, field

from entities.implant import Implant
from entities.item import Item
from entities.npc import NPC
from world.content import Mod, NetNode, Quest, Shop, Skill


@dataclass
class Room:
    id: str
    name_zh: str = ""
    name_en: str = ""
    description_zh: str = ""
    description_en: str = ""
    district: str = ""
    grid_x: int = 0
    grid_y: int = 0
    hidden_hint_zh: str = ""
    hidden_hint_en: str = ""
    tags: list[str] = field(default_factory=list)
    shop_id: str = ""
    exits: dict[str, str] = field(default_factory=dict)


@dataclass
class World:
    start_room: str
    rooms: dict[str, Room]
    items: dict[str, Item]
    npcs: dict[str, NPC]
    implants: dict[str, Implant]
    factions: dict[str, str]
    skills: dict[str, Skill] = field(default_factory=dict)
    mods: dict[str, Mod] = field(default_factory=dict)
    quests: dict[str, Quest] = field(default_factory=dict)
    shops: dict[str, Shop] = field(default_factory=dict)
    net_nodes: dict[str, NetNode] = field(default_factory=dict)

    def room(self, room_id: str) -> Room | None:
        return self.rooms.get(room_id)

    def item(self, item_id: str) -> Item | None:
        return self.items.get(item_id)

    def npc(self, npc_id: str) -> NPC | None:
        return self.npcs.get(npc_id)

    def implant(self, implant_id: str) -> Implant | None:
        return self.implants.get(implant_id)

    def skill(self, skill_id: str) -> Skill | None:
        return self.skills.get(skill_id)

    def mod(self, mod_id: str) -> Mod | None:
        return self.mods.get(mod_id)

    def quest(self, quest_id: str) -> Quest | None:
        return self.quests.get(quest_id)

    def shop(self, shop_id: str) -> Shop | None:
        return self.shops.get(shop_id)

    def net_node(self, node_id: str) -> NetNode | None:
        return self.net_nodes.get(node_id)

    def net_nodes_in_room(self, room_id: str) -> list[NetNode]:
        return [node for node in self.net_nodes.values() if node.room_id == room_id]