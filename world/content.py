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
INTERACTABLES_PATH = DATA_DIR / "interactables.yaml"
RECIPES_PATH = DATA_DIR / "recipes.yaml"
BRAINDANCES_PATH = DATA_DIR / "braindances.yaml"
PASSIVE_CHAINS_PATH = DATA_DIR / "passive_chains.yaml"


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
class QuestStage:
    objective_type: str = ""
    objective_target: str = ""


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
    stages: list[QuestStage] = field(default_factory=list)


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


@dataclass
class Interactable:
    id: str
    room_id: str = ""
    name_zh: str = ""
    name_en: str = ""
    description_zh: str = ""
    description_en: str = ""
    message_zh: str = ""
    message_en: str = ""
    requires_item: str = ""
    requires_skill: str = ""
    gives_item: str = ""
    once_key: str = ""
    braindance_id: str = ""


@dataclass
class Recipe:
    id: str
    name_zh: str = ""
    name_en: str = ""
    station_room_tags: list[str] = field(default_factory=list)
    ingredients: dict[str, int] = field(default_factory=dict)
    gold_cost: int = 0
    output: str = ""
    output_count: int = 1


@dataclass
class DisassembleRecipe:
    id: str
    outputs: dict[str, int] = field(default_factory=dict)
    gold_gain: int = 0


@dataclass
class Braindance:
    id: str
    name_zh: str = ""
    name_en: str = ""
    cost: int = 0
    lines_zh: list[str] = field(default_factory=list)
    lines_en: list[str] = field(default_factory=list)
    sets_flag: str = ""
    street_cred: int = 0


@dataclass
class PassiveChain:
    id: str
    name_zh: str = ""
    name_en: str = ""
    requires_implants: list[str] = field(default_factory=list)
    requires_skills: list[str] = field(default_factory=list)
    requires_perks: list[str] = field(default_factory=list)
    min_street_cred: int = 0
    bonus_attack: int = 0
    quickhack_mult: float = 1.0
    bonus_xp_percent: int = 0
    description_zh: str = ""
    description_en: str = ""


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


def _parse_quest_stages(data: dict) -> list[QuestStage]:
    stages_raw = data.get("stages") or []
    if stages_raw:
        return [
            QuestStage(
                objective_type=str(stage.get("objective_type", "")),
                objective_target=str(stage.get("objective_target", "")),
            )
            for stage in stages_raw
        ]
    objective_type = str(data.get("objective_type", ""))
    if objective_type:
        return [
            QuestStage(
                objective_type=objective_type,
                objective_target=str(data.get("objective_target", "")),
            )
        ]
    return []


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
            stages=_parse_quest_stages(data),
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


def load_interactables(path: Path | None = None) -> dict[str, Interactable]:
    raw = _load_yaml(path or INTERACTABLES_PATH)
    return {
        iid: Interactable(
            id=iid,
            room_id=str(data.get("room_id", "")),
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
            message_zh=str(data.get("message_zh", "")),
            message_en=str(data.get("message_en", "")),
            requires_item=str(data.get("requires_item", "")),
            requires_skill=str(data.get("requires_skill", "")),
            gives_item=str(data.get("gives_item", "")),
            once_key=str(data.get("once_key", "")),
            braindance_id=str(data.get("braindance_id", "")),
        )
        for iid, data in (raw.get("interactables") or {}).items()
    }


def load_recipes(path: Path | None = None) -> tuple[dict[str, Recipe], dict[str, DisassembleRecipe]]:
    raw = _load_yaml(path or RECIPES_PATH)
    recipes = {
        rid: Recipe(
            id=rid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            station_room_tags=[str(tag) for tag in (data.get("station_room_tags") or [])],
            ingredients={str(k): int(v) for k, v in (data.get("ingredients") or {}).items()},
            gold_cost=int(data.get("gold_cost", 0)),
            output=str(data.get("output", "")),
            output_count=int(data.get("output_count", 1)),
        )
        for rid, data in (raw.get("recipes") or {}).items()
    }
    disassemble = {
        iid: DisassembleRecipe(
            id=iid,
            outputs={str(k): int(v) for k, v in (data.get("outputs") or {}).items()},
            gold_gain=int(data.get("gold_gain", 0)),
        )
        for iid, data in (raw.get("disassemble") or {}).items()
    }
    return recipes, disassemble


def load_braindances(path: Path | None = None) -> dict[str, Braindance]:
    raw = _load_yaml(path or BRAINDANCES_PATH)
    return {
        bid: Braindance(
            id=bid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            cost=int(data.get("cost", 0)),
            lines_zh=[str(line) for line in (data.get("lines_zh") or [])],
            lines_en=[str(line) for line in (data.get("lines_en") or [])],
            sets_flag=str(data.get("sets_flag", "")),
            street_cred=int(data.get("street_cred", 0)),
        )
        for bid, data in (raw.get("braindances") or {}).items()
    }


def load_passive_chains(path: Path | None = None) -> dict[str, PassiveChain]:
    raw = _load_yaml(path or PASSIVE_CHAINS_PATH)
    return {
        cid: PassiveChain(
            id=cid,
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
            requires_implants=[str(i) for i in (data.get("requires_implants") or [])],
            requires_skills=[str(s) for s in (data.get("requires_skills") or [])],
            requires_perks=[str(p) for p in (data.get("requires_perks") or [])],
            min_street_cred=int(data.get("min_street_cred", 0)),
            bonus_attack=int(data.get("bonus_attack", 0)),
            quickhack_mult=float(data.get("quickhack_mult", 1.0)),
            bonus_xp_percent=int(data.get("bonus_xp_percent", 0)),
            description_zh=str(data.get("description_zh", "")),
            description_en=str(data.get("description_en", "")),
        )
        for cid, data in (raw.get("chains") or {}).items()
    }