from __future__ import annotations

from pathlib import Path

import yaml

from entities.implant import Implant
from entities.item import Item
from entities.npc import NPC
from world.world import Room, World

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_PATH = DATA_DIR / "world.yaml"
IMPLANTS_PATH = DATA_DIR / "implants.yaml"


def _load_implants(path: Path | None = None) -> dict[str, Implant]:
    src = path or IMPLANTS_PATH
    if not src.exists():
        return {}
    with src.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return {
        iid: Implant(
            id=iid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            body=int(data.get("body", 0)),
            reflex=int(data.get("reflex", 0)),
            tech=int(data.get("tech", 0)),
            cool=int(data.get("cool", 0)),
            intelligence=int(data.get("intelligence", 0)),
            humanity_cost=int(data.get("humanity_cost", 0)),
            slot=str(data.get("slot", "cyber")),
        )
        for iid, data in (raw.get("implants") or {}).items()
    }


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
            grid_x=int(data.get("grid_x", 0)),
            grid_y=int(data.get("grid_y", 0)),
            hidden_hint_zh=str(data.get("hidden_hint_zh", "")),
            hidden_hint_en=str(data.get("hidden_hint_en", "")),
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
            weapon_damage=int(data.get("weapon_damage", 0)),
            defense=int(data.get("defense", 0)),
            value=int(data.get("value", 0)),
            implant_id=str(data.get("implant_id", "")),
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
            hp=int(data.get("hp", 30)),
            max_hp=int(data.get("max_hp", data.get("hp", 30))),
            attack=int(data.get("attack", 3)),
            hostile=bool(data.get("hostile", False)),
            patrol=[str(r) for r in (data.get("patrol") or [])],
            idle_msg_zh=str(data.get("idle_msg_zh", "")),
            idle_msg_en=str(data.get("idle_msg_en", "")),
        )
        for nid, data in (raw.get("npcs") or {}).items()
    }

    factions = {str(k): str(v) for k, v in (raw.get("factions") or {}).items()}
    implants = _load_implants()

    return World(
        start_room=str(raw.get("start_room", "square")),
        rooms=rooms,
        items=items,
        npcs=npcs,
        implants=implants,
        factions=factions,
    )


def default_room_items(path: Path | None = None) -> dict[str, list[str]]:
    src = path or DATA_PATH
    with src.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return {
        str(rid): [str(i) for i in items]
        for rid, items in (raw.get("room_items") or {}).items()
    }