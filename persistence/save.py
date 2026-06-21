from __future__ import annotations

import json
from pathlib import Path

from entities.player import Player
from shared.equipment import normalize_equipment
from shared.security import validate_character_name

SAVE_DIR = Path(__file__).resolve().parent.parent / "data" / "saves"


def save_name_allowed(name: str) -> bool:
    return validate_character_name(name) is None


def _save_path(name: str) -> Path:
    if not save_name_allowed(name):
        raise ValueError(f"invalid save name: {name!r}")
    base = SAVE_DIR.resolve()
    path = (base / f"{name.lower()}.json").resolve()
    if not path.is_relative_to(base):
        raise ValueError(f"invalid save path for name: {name!r}")
    return path


def player_exists(name: str) -> bool:
    if not save_name_allowed(name):
        return False
    return _save_path(name).exists()


def list_saves() -> list[str]:
    if not SAVE_DIR.exists():
        return []
    return sorted(p.stem for p in SAVE_DIR.glob("*.json"))


def player_to_dict(player: Player) -> dict:
    from world.cyberware import implanted_ids

    return {
        "name": player.name,
        "room_id": player.room_id,
        "locale": player.locale,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "gold": player.gold,
        "level": player.level,
        "xp": player.xp,
        "attribute_points": player.attribute_points,
        "perk_points": player.perk_points,
        "perks": list(player.perks),
        "body": player.body,
        "reflex": player.reflex,
        "tech": player.tech,
        "cool": player.cool,
        "intelligence": player.intelligence,
        "humanity": player.humanity,
        "reputation": player.reputation,
        "street_cred": player.street_cred,
        "faction": player.faction,
        "ram": player.ram,
        "max_ram": player.max_ram,
        "inventory": list(player.inventory),
        "equipment": dict(player.equipment),
        "implants": implanted_ids(player),
        "cyberware": dict(player.cyberware),
        "home_room_id": player.home_room_id,
        "home_stash": list(player.home_stash),
        "vehicle_id": player.vehicle_id,
        "vehicles": list(player.vehicles),
        "active_vehicle": player.active_vehicle,
        "wanted_level": player.wanted_level,
        "interact_flags": dict(player.interact_flags),
        "braindance_flags": dict(player.braindance_flags),
        "visited_rooms": list(player.visited_rooms),
        "prompt_mud": player.prompt_mud,
        "skills": list(player.skills),
        "proficiency_levels": {str(k): int(v) for k, v in player.proficiency_levels.items()},
        "proficiency_xp": {str(k): int(v) for k, v in player.proficiency_xp.items()},
        "password_hash": player.password_hash,
        "auth_failed_attempts": player.auth_failed_attempts,
        "auth_locked_until": player.auth_locked_until,
        "in_combat": player.in_combat,
        "encounter_id": player.encounter_id,
        "active_quest": player.active_quest,
        "quest_flags": dict(player.quest_flags),
        "net_shell": player.net_shell,
        "weapon_mods": {wid: list(mods) for wid, mods in player.weapon_mods.items()},
        "chased_by_npc": player.chased_by_npc,
        "content_rating": player.content_rating,
        "romance_flags": dict(player.romance_flags),
        "player_status": dict(player.player_status),
        "posture": player.posture,
        "fatigue": player.fatigue,
        "life_anchor": player.life_anchor,
        "profiled_npcs": list(player.profiled_npcs),
        "footprint": player.footprint,
        "discovered_net_links": list(player.discovered_net_links),
    }


def player_from_dict(data: dict) -> Player:
    from world.cyberware import migrate_legacy_implants
    from world.loader import load_world

    weapon_mods_raw = data.get("weapon_mods") or {}
    weapon_mods = {str(k): list(v) for k, v in weapon_mods_raw.items()}
    cyberware_raw = data.get("cyberware") or {}
    cyberware = {str(k): str(v) for k, v in cyberware_raw.items()}
    player = Player(
        name=str(data.get("name", "Traveler")),
        room_id=str(data.get("room_id", "square")),
        locale=str(data.get("locale", "en")),
        named=True,
        hp=int(data.get("hp", 100)),
        max_hp=int(data.get("max_hp", 100)),
        gold=int(data.get("gold", 0)),
        level=int(data.get("level", 1)),
        xp=int(data.get("xp", 0)),
        attribute_points=int(data.get("attribute_points", 0)),
        perk_points=int(data.get("perk_points", 0)),
        perks=list(data.get("perks", [])),
        body=int(data.get("body", 3)),
        reflex=int(data.get("reflex", 3)),
        tech=int(data.get("tech", 3)),
        cool=int(data.get("cool", 3)),
        intelligence=int(data.get("intelligence", 3)),
        humanity=int(data.get("humanity", 100)),
        reputation=int(data.get("reputation", 0)),
        street_cred=int(data.get("street_cred", 0)),
        faction=str(data.get("faction", "")),
        ram=int(data.get("ram", 4)),
        max_ram=int(data.get("max_ram", 8)),
        inventory=list(data.get("inventory", [])),
        equipment=normalize_equipment(dict(data.get("equipment", {}))),
        implants=list(data.get("implants", [])),
        cyberware=cyberware,
        home_room_id=str(data.get("home_room_id", "")),
        home_stash=list(data.get("home_stash", [])),
        vehicle_id=str(data.get("vehicle_id", "")),
        vehicles=list(data.get("vehicles", [])),
        active_vehicle=str(data.get("active_vehicle", "")),
        wanted_level=int(data.get("wanted_level", 0)),
        interact_flags=dict(data.get("interact_flags", {})),
        braindance_flags=dict(data.get("braindance_flags", {})),
        visited_rooms=list(data.get("visited_rooms", [])),
        prompt_mud=str(data.get("prompt_mud", "")),
        skills=list(data.get("skills", [])),
        proficiency_levels={str(k): int(v) for k, v in (data.get("proficiency_levels") or {}).items()},
        proficiency_xp={str(k): int(v) for k, v in (data.get("proficiency_xp") or {}).items()},
        password_hash=str(data.get("password_hash", "")),
        auth_failed_attempts=int(data.get("auth_failed_attempts", 0)),
        auth_locked_until=float(data.get("auth_locked_until", 0.0)),
        in_combat=bool(data.get("in_combat", False)),
        encounter_id=str(data.get("encounter_id", "")),
        active_quest=str(data.get("active_quest", "")),
        quest_flags=dict(data.get("quest_flags", {})),
        net_shell=bool(data.get("net_shell", False)),
        weapon_mods=weapon_mods,
        chased_by_npc=str(data.get("chased_by_npc", "")),
        content_rating=str(data.get("content_rating", "teen")),
        romance_flags=dict(data.get("romance_flags", {})),
        player_status={str(k): int(v) for k, v in (data.get("player_status") or {}).items()},
        posture=str(data.get("posture", "standing")),
        fatigue=int(data.get("fatigue", 0)),
        life_anchor=str(data.get("life_anchor", "")),
        profiled_npcs=list(data.get("profiled_npcs", [])),
        footprint=int(data.get("footprint", 0)),
        discovered_net_links=list(data.get("discovered_net_links", [])),
    )
    if not player.cyberware and player.implants:
        migrate_legacy_implants(player, load_world())
    from world.vehicles_player import migrate_vehicle_fields

    migrate_vehicle_fields(player)
    return player


def _ensure_save_dir() -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        SAVE_DIR.chmod(0o700)
    except OSError:
        pass


def save_player(player: Player) -> Path:
    if not player.named:
        raise ValueError("cannot save unnamed player")
    _ensure_save_dir()
    path = _save_path(player.name)
    path.write_text(json.dumps(player_to_dict(player), ensure_ascii=False, indent=2), encoding="utf-8")
    path.chmod(0o600)
    return path


def load_player(name: str) -> Player | None:
    if not save_name_allowed(name):
        return None
    path = _save_path(name)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return player_from_dict(data)


def delete_save(name: str) -> bool:
    if not save_name_allowed(name):
        return False
    path = _save_path(name)
    if not path.exists():
        return False
    path.unlink()
    return True