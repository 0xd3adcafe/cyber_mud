from __future__ import annotations

import json
from pathlib import Path

from entities.player import Player

SAVE_DIR = Path(__file__).resolve().parent.parent / "data" / "saves"


def _save_path(name: str) -> Path:
    return SAVE_DIR / f"{name.lower()}.json"


def player_exists(name: str) -> bool:
    return _save_path(name).exists()


def list_saves() -> list[str]:
    if not SAVE_DIR.exists():
        return []
    return sorted(p.stem for p in SAVE_DIR.glob("*.json"))


def player_to_dict(player: Player) -> dict:
    return {
        "name": player.name,
        "room_id": player.room_id,
        "locale": player.locale,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "gold": player.gold,
        "body": player.body,
        "reflex": player.reflex,
        "tech": player.tech,
        "cool": player.cool,
        "intelligence": player.intelligence,
        "humanity": player.humanity,
        "reputation": player.reputation,
        "faction": player.faction,
        "ram": player.ram,
        "max_ram": player.max_ram,
        "inventory": list(player.inventory),
        "equipment": dict(player.equipment),
        "implants": list(player.implants),
        "visited_rooms": list(player.visited_rooms),
        "prompt_mud": player.prompt_mud,
        "skills": list(player.skills),
        "password_hash": player.password_hash,
        "in_combat": player.in_combat,
        "encounter_id": player.encounter_id,
        "active_quest": player.active_quest,
        "quest_flags": dict(player.quest_flags),
        "net_shell": player.net_shell,
        "weapon_mods": {wid: list(mods) for wid, mods in player.weapon_mods.items()},
        "chased_by_npc": player.chased_by_npc,
    }


def player_from_dict(data: dict) -> Player:
    weapon_mods_raw = data.get("weapon_mods") or {}
    weapon_mods = {str(k): list(v) for k, v in weapon_mods_raw.items()}
    return Player(
        name=str(data.get("name", "旅人")),
        room_id=str(data.get("room_id", "square")),
        locale=str(data.get("locale", "zh")),
        named=True,
        hp=int(data.get("hp", 100)),
        max_hp=int(data.get("max_hp", 100)),
        gold=int(data.get("gold", 0)),
        body=int(data.get("body", 3)),
        reflex=int(data.get("reflex", 3)),
        tech=int(data.get("tech", 3)),
        cool=int(data.get("cool", 3)),
        intelligence=int(data.get("intelligence", 3)),
        humanity=int(data.get("humanity", 100)),
        reputation=int(data.get("reputation", 0)),
        faction=str(data.get("faction", "")),
        ram=int(data.get("ram", 4)),
        max_ram=int(data.get("max_ram", 8)),
        inventory=list(data.get("inventory", [])),
        equipment=dict(data.get("equipment", {})),
        implants=list(data.get("implants", [])),
        visited_rooms=list(data.get("visited_rooms", [])),
        prompt_mud=str(data.get("prompt_mud", "")),
        skills=list(data.get("skills", [])),
        password_hash=str(data.get("password_hash", "")),
        in_combat=bool(data.get("in_combat", False)),
        encounter_id=str(data.get("encounter_id", "")),
        active_quest=str(data.get("active_quest", "")),
        quest_flags=dict(data.get("quest_flags", {})),
        net_shell=bool(data.get("net_shell", False)),
        weapon_mods=weapon_mods,
        chased_by_npc=str(data.get("chased_by_npc", "")),
    )


def save_player(player: Player) -> Path:
    if not player.named:
        return _save_path(player.name)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    path = _save_path(player.name)
    path.write_text(json.dumps(player_to_dict(player), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_player(name: str) -> Player | None:
    path = _save_path(name)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return player_from_dict(data)


def delete_save(name: str) -> bool:
    path = _save_path(name)
    if not path.exists():
        return False
    path.unlink()
    return True