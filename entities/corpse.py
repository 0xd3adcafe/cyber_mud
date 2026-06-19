from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Corpse:
    id: str
    npc_id: str
    room_id: str
    loot: list[str] = field(default_factory=list)
    decay_at_tick: int = 0
    player_name: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "npc_id": self.npc_id,
            "room_id": self.room_id,
            "loot": list(self.loot),
            "decay_at_tick": self.decay_at_tick,
            "player_name": self.player_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Corpse:
        return cls(
            id=str(data.get("id", "")),
            npc_id=str(data.get("npc_id", "")),
            room_id=str(data.get("room_id", "")),
            loot=[str(item_id) for item_id in (data.get("loot") or [])],
            decay_at_tick=int(data.get("decay_at_tick", 0)),
            player_name=str(data.get("player_name", "")),
        )