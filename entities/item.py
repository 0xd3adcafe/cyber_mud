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