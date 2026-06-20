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
    aggro: int = 0
    quest_id: str = ""
    schedule: dict[str, str] = field(default_factory=dict)
    talk_key: str = ""
    loot: list[str] = field(default_factory=list)
    equipment: dict[str, str] = field(default_factory=dict)
    tier: str = ""
    respawn_minutes: int | None = None
    xp_reward: int = 0
    faction: str = ""
    motivation: str = ""
    tags: list[str] = field(default_factory=list)