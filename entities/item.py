from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Item:
    id: str
    name_zh: str = ""
    name_en: str = ""
    description_zh: str = ""
    description_en: str = ""
    takeable: bool = True
    slot: str = ""
    weapon_type: str = ""
    weapon_class: str = ""
    weapon_mode: str = ""
    weapon_damage: int = 0
    defense: int = 0
    value: int = 0
    implant_id: str = ""
    consumable: str = ""
    hp_restore: int = 0
    ram_restore: int = 0
    cures_status: str = ""
    locks: dict[str, str] = field(default_factory=dict)