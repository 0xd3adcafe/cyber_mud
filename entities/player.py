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
    body: int = 3
    reflex: int = 3
    tech: int = 3
    cool: int = 3
    intelligence: int = 3
    humanity: int = 100
    reputation: int = 0
    ram: int = 4
    max_ram: int = 8
    inventory: list[str] = field(default_factory=list)
    equipment: dict[str, str] = field(default_factory=dict)
    implants: list[str] = field(default_factory=list)
    visited_rooms: list[str] = field(default_factory=list)
    prompt_mud: str = ""
    skills: list[str] = field(default_factory=list)
    password_hash: str = ""
    in_combat: bool = False
    encounter_id: str = ""