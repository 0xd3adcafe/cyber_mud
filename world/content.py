from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SKILLS_PATH = DATA_DIR / "skills.yaml"
TALENTS_PATH = DATA_DIR / "talents.yaml"
MODS_PATH = DATA_DIR / "mods.yaml"
QUESTS_PATH = DATA_DIR / "quests.yaml"
QUICKHACKS_PATH = DATA_DIR / "quickhacks.yaml"
HOUSING_PATH = DATA_DIR / "housing.yaml"
VEHICLES_PATH = DATA_DIR / "vehicles.yaml"
TRANSIT_PATH = DATA_DIR / "transit.yaml"
SHOPS_PATH = DATA_DIR / "shops.yaml"
NET_NODES_PATH = DATA_DIR / "net_nodes.yaml"


@dataclass
class Skill:
    id: str
    name_zh: str = ""
    name_en: str = ""
    gold_cost: int = 0
    ram_cost: int = 0
    level_req: int = 1
    category: str = ""
    prereq_skill: str = ""
    description_zh: str = ""
    description_en: str = ""


@dataclass
class Talent:
    id: str
    name_zh: str = ""
    name_en: str = ""
    level_req: int = 1
    category: str = ""
    prereq_talent: str = ""
    prereq_skill: str = ""
    description_zh: str = ""
    description_en: str = ""
    stat_bonus: dict[str, int] = field(default_factory=dict)


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
    objective_type: str = ""
    objective_target: str = ""
    complete_npc_id: str = ""
    reward_gold: int = 0
    reward_xp: int = 0
    reward_street_cred: int = 0
    street_cred_req: int = 0


@dataclass
class Quickhack:
    id: str
    name_zh: str = ""
    name_en: str = ""
    ram_cost: int = 2
    damage_mult: float = 1.0
    status_effect: str = ""
    status_duration: int = 0
    skill_req: str = ""
    description_zh: str = ""
    description_en: str = ""


@dataclass
class Housing:
    id: str
    room_id: str = ""
    name_zh: str = ""
    name_en: str = ""
    cost: int = 0
    stash_capacity: int = 10
    rent_room: str = ""
    description_zh: str = ""
    description_en: str = ""


@dataclass
class Vehicle:
    id: str
    name_zh: str = ""
    name_en: str = ""
    cost: int = 0
    dealer_room: str = ""
    description_zh: str = ""
    description_en: str = ""
    routes: list[str] = field(default_factory=list)


@dataclass
class TransitRoute:
    from_room: str
    to_room: str
    fare: int = 0
    name_zh: str = ""
    name_en: str = ""
    requires_home: str = ""


@dataclass
class Shop:
    id: str
    name_zh: str = ""
    name_en: str = ""
    room_id: str = ""
    npc_id: str = ""
    open_hour: int = 0
    close_hour: int = 24
    sells: dict[str, int] = field(default_factory=dict)
    buy_items: bool = True
    buy_rate: float = 0.5


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
            level_req=int(data.get("level_req", 1)),
            category=str(data.get("category", "")),
            prereq_skill=str(data.get("prereq_skill", "")),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
        )
        for sid, data in (raw.get("skills") or {}).items()
    }


def load_talents(path: Path | None = None) -> dict[str, Talent]:
    raw = _load_yaml(path or TALENTS_PATH)
    return {
        tid: Talent(
            id=tid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            level_req=int(data.get("level_req", 1)),
            category=str(data.get("category", "")),
            prereq_talent=str(data.get("prereq_talent", "")),
            prereq_skill=str(data.get("prereq_skill", "")),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
            stat_bonus={str(k): int(v) for k, v in (data.get("stat_bonus") or {}).items()},
        )
        for tid, data in (raw.get("talents") or {}).items()
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
            reward_xp=int(data.get("reward_xp", 0)),
            reward_street_cred=int(data.get("reward_street_cred", 0)),
            street_cred_req=int(data.get("street_cred_req", 0)),
            objective_type=str(data.get("objective_type", "")),
            objective_target=str(data.get("objective_target", "")),
            complete_npc_id=str(data.get("complete_npc_id", "")),
        )
        for qid, data in (raw.get("quests") or {}).items()
    }


def load_quickhacks(path: Path | None = None) -> dict[str, Quickhack]:
    raw = _load_yaml(path or QUICKHACKS_PATH)
    return {
        qid: Quickhack(
            id=qid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            ram_cost=int(data.get("ram_cost", 2)),
            damage_mult=float(data.get("damage_mult", 1.0)),
            status_effect=str(data.get("status_effect", "")),
            status_duration=int(data.get("status_duration", 0)),
            skill_req=str(data.get("skill_req", "")),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
        )
        for qid, data in (raw.get("quickhacks") or {}).items()
    }


def load_housing(path: Path | None = None) -> dict[str, Housing]:
    raw = _load_yaml(path or HOUSING_PATH)
    return {
        hid: Housing(
            id=hid,
            room_id=str(data.get("room_id", hid)),
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            cost=int(data.get("cost", 0)),
            stash_capacity=int(data.get("stash_capacity", 10)),
            rent_room=str(data.get("rent_room", "")),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
        )
        for hid, data in (raw.get("housing") or {}).items()
    }


def load_vehicles(path: Path | None = None) -> dict[str, Vehicle]:
    raw = _load_yaml(path or VEHICLES_PATH)
    return {
        vid: Vehicle(
            id=vid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            cost=int(data.get("cost", 0)),
            dealer_room=str(data.get("dealer_room", "")),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
            routes=[str(r) for r in (data.get("routes") or [])],
        )
        for vid, data in (raw.get("vehicles") or {}).items()
    }


def load_transit(path: Path | None = None) -> list[TransitRoute]:
    raw = _load_yaml(path or TRANSIT_PATH)
    routes: list[TransitRoute] = []
    for from_room, dests in (raw.get("transit") or {}).items():
        for to_room, data in (dests or {}).items():
            routes.append(
                TransitRoute(
                    from_room=str(from_room),
                    to_room=str(to_room),
                    fare=int(data.get("fare", 0)),
                    name_zh=str(data.get("name_zh", "")),
                    name_en=str(data.get("name_en", "")),
                    requires_home=str(data.get("requires_home", "")),
                )
            )
    return routes


def load_shops(path: Path | None = None) -> dict[str, Shop]:
    raw = _load_yaml(path or SHOPS_PATH)
    return {
        sid: Shop(
            id=sid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            room_id=str(data.get("room_id", "")),
            npc_id=str(data.get("npc_id", "")),
            open_hour=int(data.get("open_hour", 0)),
            close_hour=int(data.get("close_hour", 24)),
            sells={str(k): int(v) for k, v in (data.get("sells") or {}).items()},
            buy_items=bool(data.get("buy_items", True)),
            buy_rate=float(data.get("buy_rate", 0.5)),
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