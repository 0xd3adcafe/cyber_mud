from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NPC:
    id: str
    name_zh: str = ""
    name_en: str = ""
    room_id: str = ""
    description_zh: str = ""
    description_en: str = ""