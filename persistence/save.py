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
        "ram": player.ram,
        "max_ram": player.max_ram,
        "inventory": list(player.inventory),
        "equipment": dict(player.equipment),
        "implants": list(player.implants),
        "skills": list(player.skills),
        "password_hash": player.password_hash,
    }


def player_from_dict(data: dict) -> Player:
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
        ram=int(data.get("ram", 4)),
        max_ram=int(data.get("max_ram", 8)),
        inventory=list(data.get("inventory", [])),
        equipment=dict(data.get("equipment", {})),
        implants=list(data.get("implants", [])),
        skills=list(data.get("skills", [])),
        password_hash=str(data.get("password_hash", "")),
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