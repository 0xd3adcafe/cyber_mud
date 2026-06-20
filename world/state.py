from __future__ import annotations

from dataclasses import dataclass, field

from entities.corpse import Corpse
from world.clock import TimeConfig, WorldClock
from world.world import World


@dataclass
class WorldState:
    world: World
    clock: WorldClock = field(default_factory=WorldClock)
    time_config: TimeConfig = field(default_factory=TimeConfig)
    room_items: dict[str, list[str]] = field(default_factory=dict)
    encounters: dict[str, "Encounter"] = field(default_factory=dict)
    npc_rooms: dict[str, str] = field(default_factory=dict)
    corpses: dict[str, Corpse] = field(default_factory=dict)
    npc_respawns: dict[str, int] = field(default_factory=dict)
    npc_vitals: dict[str, int] = field(default_factory=dict)
    weather: dict[str, str] = field(default_factory=dict)
    tick_count: int = 0

    def items_in_room(self, room_id: str) -> list[str]:
        return list(self.room_items.get(room_id, []))

    def npc_room(self, npc_id: str) -> str:
        return self.npc_rooms.get(npc_id, "")

    def npcs_in_room(self, room_id: str) -> list[str]:
        return [npc_id for npc_id, rid in self.npc_rooms.items() if rid == room_id]