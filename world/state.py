from __future__ import annotations

from dataclasses import dataclass, field

from world.clock import TimeConfig, WorldClock
from world.world import World


@dataclass
class WorldState:
    world: World
    clock: WorldClock = field(default_factory=WorldClock)
    time_config: TimeConfig = field(default_factory=TimeConfig)
    room_items: dict[str, list[str]] = field(default_factory=dict)

    def items_in_room(self, room_id: str) -> list[str]:
        return list(self.room_items.get(room_id, []))