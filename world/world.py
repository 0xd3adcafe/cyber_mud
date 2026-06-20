from __future__ import annotations

from dataclasses import dataclass, field

from entities.implant import Implant
from entities.item import Item
from entities.npc import NPC
from world.content import (
    Braindance,
    DisassembleRecipe,
    Housing,
    Interactable,
    Mod,
    NetNode,
    PassiveChain,
    Quest,
    Quickhack,
    Recipe,
    Shop,
    Skill,
    Talent,
    TransitRoute,
    Vehicle,
)


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
    respawn_room: str
    rooms: dict[str, Room]
    items: dict[str, Item]
    npcs: dict[str, NPC]
    implants: dict[str, Implant]
    factions: dict[str, str]
    skills: dict[str, Skill] = field(default_factory=dict)
    talents: dict[str, Talent] = field(default_factory=dict)
    mods: dict[str, Mod] = field(default_factory=dict)
    quests: dict[str, Quest] = field(default_factory=dict)
    quickhacks: dict[str, Quickhack] = field(default_factory=dict)
    homes: dict[str, Housing] = field(default_factory=dict)
    vehicles: dict[str, Vehicle] = field(default_factory=dict)
    transit_routes: list[TransitRoute] = field(default_factory=list)
    shops: dict[str, Shop] = field(default_factory=dict)
    net_nodes: dict[str, NetNode] = field(default_factory=dict)
    interactables: dict[str, Interactable] = field(default_factory=dict)
    recipes: dict[str, Recipe] = field(default_factory=dict)
    disassemble: dict[str, DisassembleRecipe] = field(default_factory=dict)
    braindances: dict[str, Braindance] = field(default_factory=dict)
    passive_chains: dict[str, PassiveChain] = field(default_factory=dict)

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

    def talent(self, talent_id: str) -> Talent | None:
        return self.talents.get(talent_id)

    def mod(self, mod_id: str) -> Mod | None:
        return self.mods.get(mod_id)

    def quest(self, quest_id: str) -> Quest | None:
        return self.quests.get(quest_id)

    def quickhack(self, quickhack_id: str) -> Quickhack | None:
        return self.quickhacks.get(quickhack_id)

    def home(self, home_id: str) -> Housing | None:
        return self.homes.get(home_id)

    def vehicle(self, vehicle_id: str) -> Vehicle | None:
        return self.vehicles.get(vehicle_id)

    def transit_from(self, room_id: str) -> list[TransitRoute]:
        return [route for route in self.transit_routes if route.from_room == room_id]

    def shop(self, shop_id: str) -> Shop | None:
        return self.shops.get(shop_id)

    def net_node(self, node_id: str) -> NetNode | None:
        return self.net_nodes.get(node_id)

    def net_nodes_in_room(self, room_id: str) -> list[NetNode]:
        return [node for node in self.net_nodes.values() if node.room_id == room_id]

    def interactable(self, interactable_id: str) -> Interactable | None:
        return self.interactables.get(interactable_id)

    def interactables_in_room(self, room_id: str) -> list[Interactable]:
        return [obj for obj in self.interactables.values() if obj.room_id == room_id]

    def recipe(self, recipe_id: str) -> Recipe | None:
        return self.recipes.get(recipe_id)

    def disassemble_recipe(self, item_id: str) -> DisassembleRecipe | None:
        return self.disassemble.get(item_id)

    def braindance(self, bd_id: str) -> Braindance | None:
        return self.braindances.get(bd_id)