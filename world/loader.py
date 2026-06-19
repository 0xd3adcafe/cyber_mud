from __future__ import annotations

from pathlib import Path

import yaml

from entities.item import Item
from entities.npc import NPC
from world.world import Room, World

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "world.yaml"


def load_world(path: Path | None = None) -> World:
    src = path or DATA_PATH
    with src.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    rooms = {
        rid: Room(
            id=rid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
            district=str(data.get("district", "")),
            exits={str(k): str(v) for k, v in (data.get("exits") or {}).items()},
        )
        for rid, data in (raw.get("rooms") or {}).items()
    }

    items = {
        iid: Item(
            id=iid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
            takeable=bool(data.get("takeable", True)),
            slot=str(data.get("slot", "")),
        )
        for iid, data in (raw.get("items") or {}).items()
    }

    npcs = {
        nid: NPC(
            id=nid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            room_id=str(data.get("room_id", "")),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
        )
        for nid, data in (raw.get("npcs") or {}).items()
    }

    factions = {str(k): str(v) for k, v in (raw.get("factions") or {}).items()}

    return World(
        start_room=str(raw.get("start_room", "square")),
        rooms=rooms,
        items=items,
        npcs=npcs,
        factions=factions,
    )