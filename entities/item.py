from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Item:
    id: str
    name_zh: str = ""
    name_en: str = ""
    description_zh: str = ""
    description_en: str = ""
    takeable: bool = True
    slot: str = ""
    weapon_damage: int = 0
    defense: int = 0
    value: int = 0
    implant_id: str = ""