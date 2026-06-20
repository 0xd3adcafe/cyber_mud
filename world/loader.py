from __future__ import annotations

from pathlib import Path

import yaml

from entities.implant import Implant
from entities.item import Item
from shared.equipment import WEAPON_ITEM_SLOT, normalize_equipment, resolve_slot_id
from entities.npc import NPC
from world.content import (
    load_all_braindances,
    load_all_quests,
    load_housing,
    load_interactables,
    load_mods,
    load_net_nodes,
    load_passive_chains,
    load_quests,
    load_quickhacks,
    load_recipes,
    load_shops,
    load_skills,
    load_talents,
    load_transit,
    load_vehicles,
)
from world.world import Room, World

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_PATH = DATA_DIR / "world.yaml"
POPULATION_PATH = DATA_DIR / "world_population.yaml"
IMPLANTS_PATH = DATA_DIR / "implants.yaml"


def _load_world_raw(path: Path | None = None) -> dict:
    src = path or DATA_PATH
    with src.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    overlay_path = POPULATION_PATH if path is None else path.parent / "world_population.yaml"
    if overlay_path.exists() and overlay_path != src:
        with overlay_path.open(encoding="utf-8") as fh:
            overlay = yaml.safe_load(fh) or {}
        for key in ("items", "npcs"):
            if overlay.get(key):
                raw.setdefault(key, {}).update(overlay[key])
    return raw


def _merge_room_items(raw: dict, path: Path | None = None) -> dict[str, list[str]]:
    overlay_path = POPULATION_PATH if path is None else path.parent / "world_population.yaml"
    room_items = {
        str(rid): [str(i) for i in items]
        for rid, items in (raw.get("room_items") or {}).items()
    }
    if overlay_path.exists():
        with overlay_path.open(encoding="utf-8") as fh:
            overlay = yaml.safe_load(fh) or {}
        for rid, items in (overlay.get("room_items") or {}).items():
            merged = list(room_items.get(str(rid), []))
            for item_id in items:
                if item_id not in merged:
                    merged.append(str(item_id))
            room_items[str(rid)] = merged
    return room_items


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
            max_hp=int(data.get("max_hp", 0)),
            ram_bonus=int(data.get("ram_bonus", 0)),
            slot=str(data.get("slot", "arms")),
            category=str(data.get("category", "")),
            ripperdoc_only=bool(data.get("ripperdoc_only", False)),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
        )
        for iid, data in (raw.get("implants") or {}).items()
    }


def load_world(path: Path | None = None) -> World:
    raw = _load_world_raw(path)

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
            tags=[str(tag) for tag in (data.get("tags") or [])],
            shop_id=str(data.get("shop_id", "")),
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
            slot=(
                WEAPON_ITEM_SLOT
                if str(data.get("slot", "")) == WEAPON_ITEM_SLOT
                else resolve_slot_id(str(data.get("slot", "")))
            ),
            weapon_type=str(data.get("weapon_type", "")),
            weapon_class=str(data.get("weapon_class", "")),
            weapon_mode=str(data.get("weapon_mode", "")),
            weapon_damage=int(data.get("weapon_damage", 0)),
            defense=int(data.get("defense", 0)),
            value=int(data.get("value", 0)),
            implant_id=str(data.get("implant_id", "")),
            consumable=str(data.get("consumable", "")),
            hp_restore=int(data.get("hp_restore", 0)),
            ram_restore=int(data.get("ram_restore", 0)),
            cures_status=str(data.get("cures_status", "")),
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
            aggro=int(data.get("aggro", 0)),
            quest_id=str(data.get("quest_id", "")),
            schedule={str(k): str(v) for k, v in (data.get("schedule") or {}).items()},
            talk_key=str(data.get("talk_key", "")),
            loot=[str(item_id) for item_id in (data.get("loot") or [])],
            equipment=normalize_equipment(
                {
                    str(slot): str(item_id)
                    for slot, item_id in (data.get("equipment") or {}).items()
                    if item_id
                }
            ),
            tier=str(data.get("tier", "")),
            respawn_minutes=int(data["respawn_minutes"]) if "respawn_minutes" in data else None,
            xp_reward=int(data.get("xp_reward", 0)),
            faction=str(data.get("faction", "")),
            motivation=str(data.get("motivation", "")),
            tags=[str(tag) for tag in (data.get("tags") or [])],
        )
        for nid, data in (raw.get("npcs") or {}).items()
    }

    factions = {str(k): str(v) for k, v in (raw.get("factions") or {}).items()}
    implants = _load_implants()
    recipes, disassemble = load_recipes()

    start_room = str(raw.get("start_room", "square"))
    return World(
        start_room=start_room,
        respawn_room=str(raw.get("respawn_room", start_room)),
        rooms=rooms,
        items=items,
        npcs=npcs,
        implants=implants,
        factions=factions,
        skills=load_skills(),
        talents=load_talents(),
        mods=load_mods(),
        quests=load_all_quests(),
        quickhacks=load_quickhacks(),
        homes=load_housing(),
        vehicles=load_vehicles(),
        transit_routes=load_transit(),
        shops=load_shops(),
        net_nodes=load_net_nodes(),
        interactables=load_interactables(),
        recipes=recipes,
        disassemble=disassemble,
        braindances=load_all_braindances(),
        passive_chains=load_passive_chains(),
    )


def default_room_items(path: Path | None = None) -> dict[str, list[str]]:
    src = path or DATA_PATH
    with src.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return _merge_room_items(raw, path)