from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Implant:
    id: str
    name_zh: str = ""
    name_en: str = ""
    body: int = 0
    reflex: int = 0
    tech: int = 0
    cool: int = 0
    intelligence: int = 0
    max_hp: int = 0
    ram_bonus: int = 0
    humanity_cost: int = 0
    slot: str = "arms"
    category: str = ""
    ripperdoc_only: bool = False
    description_zh: str = ""
    description_en: str = ""