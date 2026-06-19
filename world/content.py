from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SKILLS_PATH = DATA_DIR / "skills.yaml"
MODS_PATH = DATA_DIR / "mods.yaml"
QUESTS_PATH = DATA_DIR / "quests.yaml"
SHOPS_PATH = DATA_DIR / "shops.yaml"
NET_NODES_PATH = DATA_DIR / "net_nodes.yaml"


@dataclass
class Skill:
    id: str
    name_zh: str = ""
    name_en: str = ""
    gold_cost: int = 0
    ram_cost: int = 0
    description_zh: str = ""
    description_en: str = ""


@dataclass
class Mod:
    id: str
    name_zh: str = ""
    name_en: str = ""
    weapon_damage: int = 0
    chip_item: str = ""


@dataclass
class Quest:
    id: str
    name_zh: str = ""
    name_en: str = ""
    npc_id: str = ""
    description_zh: str = ""
    description_en: str = ""
    hint_zh: str = ""
    hint_en: str = ""
    reward_gold: int = 0


@dataclass
class Shop:
    id: str
    name_zh: str = ""
    name_en: str = ""
    room_id: str = ""
    open_hour: int = 0
    close_hour: int = 24


@dataclass
class NetNode:
    id: str
    room_id: str = ""
    name_zh: str = ""
    name_en: str = ""
    hackable: bool = True


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_skills(path: Path | None = None) -> dict[str, Skill]:
    raw = _load_yaml(path or SKILLS_PATH)
    return {
        sid: Skill(
            id=sid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            gold_cost=int(data.get("gold_cost", 0)),
            ram_cost=int(data.get("ram_cost", 0)),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
        )
        for sid, data in (raw.get("skills") or {}).items()
    }


def load_mods(path: Path | None = None) -> dict[str, Mod]:
    raw = _load_yaml(path or MODS_PATH)
    return {
        mid: Mod(
            id=mid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            weapon_damage=int(data.get("weapon_damage", 0)),
            chip_item=str(data.get("chip_item", "")),
        )
        for mid, data in (raw.get("mods") or {}).items()
    }


def load_quests(path: Path | None = None) -> dict[str, Quest]:
    raw = _load_yaml(path or QUESTS_PATH)
    return {
        qid: Quest(
            id=qid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            npc_id=str(data.get("npc_id", "")),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
            hint_zh=str(data.get("hint_zh", "")),
            hint_en=str(data.get("hint_en", "")),
            reward_gold=int(data.get("reward_gold", 0)),
        )
        for qid, data in (raw.get("quests") or {}).items()
    }


def load_shops(path: Path | None = None) -> dict[str, Shop]:
    raw = _load_yaml(path or SHOPS_PATH)
    return {
        sid: Shop(
            id=sid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            room_id=str(data.get("room_id", "")),
            open_hour=int(data.get("open_hour", 0)),
            close_hour=int(data.get("close_hour", 24)),
        )
        for sid, data in (raw.get("shops") or {}).items()
    }


def load_net_nodes(path: Path | None = None) -> dict[str, NetNode]:
    raw = _load_yaml(path or NET_NODES_PATH)
    return {
        nid: NetNode(
            id=nid,
            room_id=str(data.get("room_id", "")),
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            hackable=bool(data.get("hackable", True)),
        )
        for nid, data in (raw.get("net_nodes") or {}).items()
    }