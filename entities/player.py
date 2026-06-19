from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Player:
    name: str = "旅人"
    room_id: str = "square"
    locale: str = "zh"
    named: bool = False
    hp: int = 100
    max_hp: int = 100
    gold: int = 0
    inventory: list[str] = field(default_factory=list)
    equipment: dict[str, str] = field(default_factory=dict)