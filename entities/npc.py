from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NPC:
    id: str
    name_zh: str = ""
    name_en: str = ""
    room_id: str = ""
    description_zh: str = ""
    description_en: str = ""
    hp: int = 30
    max_hp: int = 30
    attack: int = 3
    hostile: bool = False
    patrol: list[str] = field(default_factory=list)
    idle_msg_zh: str = ""
    idle_msg_en: str = ""