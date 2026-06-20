from __future__ import annotations

import random
from dataclasses import dataclass

from entities.item import Item
from entities.player import Player
from shared.equipment import (
    BLADE_WEAPON_TYPES,
    BLUNT_WEAPON_TYPES,
    RANGED_WEAPON_TYPES,
    active_weapon,
    is_blade_weapon_type,
    is_blunt_weapon_type,
    is_ranged_weapon_type,
)
from world.world import World

STYLE_SHOOT = "shoot"
STYLE_SLASH = "slash"
STYLE_BASH = "bash"
STYLE_PUNCH = "punch"
STYLE_BACKSTAB = "backstab"

ALL_STYLES = (
    STYLE_SHOOT,
    STYLE_SLASH,
    STYLE_BASH,
    STYLE_PUNCH,
    STYLE_BACKSTAB,
)


@dataclass(frozen=True)
class AttackStyle:
    id: str
    weapon_types: frozenset[str]
    cd_ticks: int
    hit_key: str
    start_key: str
    unarmed_only: bool = False
    weapon_predicate: str = ""


STYLES: dict[str, AttackStyle] = {
    STYLE_SHOOT: AttackStyle(
        STYLE_SHOOT,
        RANGED_WEAPON_TYPES,
        cd_ticks=2,
        hit_key="combat.shoot_hit",
        start_key="combat.start_shoot",
        weapon_predicate="ranged",
    ),
    STYLE_SLASH: AttackStyle(
        STYLE_SLASH,
        BLADE_WEAPON_TYPES,
        cd_ticks=1,
        hit_key="combat.slash_hit",
        start_key="combat.start_slash",
        weapon_predicate="blade",
    ),
    STYLE_BASH: AttackStyle(
        STYLE_BASH,
        BLUNT_WEAPON_TYPES,
        cd_ticks=1,
        hit_key="combat.bash_hit",
        start_key="combat.start_bash",
        weapon_predicate="blunt",
    ),
    STYLE_PUNCH: AttackStyle(
        STYLE_PUNCH,
        frozenset(),
        cd_ticks=1,
        hit_key="combat.punch_hit",
        start_key="combat.start_punch",
        unarmed_only=True,
    ),
    STYLE_BACKSTAB: AttackStyle(
        STYLE_BACKSTAB,
        BLADE_WEAPON_TYPES,
        cd_ticks=2,
        hit_key="combat.backstab_hit",
        start_key="combat.start_backstab",
        weapon_predicate="blade",
    ),
}


def equipped_weapon(player: Player, world: World) -> Item | None:
    return active_weapon(player, world)


def weapon_type(player: Player, world: World) -> str:
    item = equipped_weapon(player, world)
    if item is None:
        return ""
    return item.weapon_type or ""


def _weapon_matches_style(style: AttackStyle, wtype: str) -> bool:
    if style.weapon_predicate == "ranged":
        return is_ranged_weapon_type(wtype)
    if style.weapon_predicate == "blade":
        return is_blade_weapon_type(wtype)
    if style.weapon_predicate == "blunt":
        return is_blunt_weapon_type(wtype)
    return wtype in style.weapon_types


def default_style_for_weapon(player: Player, world: World) -> str:
    wtype = weapon_type(player, world)
    if is_ranged_weapon_type(wtype):
        return STYLE_SHOOT
    if is_blade_weapon_type(wtype):
        return STYLE_SLASH
    if is_blunt_weapon_type(wtype):
        return STYLE_BASH
    return STYLE_PUNCH


def style_error_key(style_id: str, player: Player, world: World) -> str | None:
    style = STYLES.get(style_id)
    if style is None:
        return "combat.unknown_style"
    wtype = weapon_type(player, world)
    if style.unarmed_only:
        if wtype:
            return "combat.punch_need_unarmed"
        return None
    if not _weapon_matches_style(style, wtype):
        if style_id == STYLE_SHOOT:
            return "combat.need_ranged"
        if style_id == STYLE_SLASH:
            return "combat.need_blade"
        if style_id == STYLE_BASH:
            return "combat.need_blunt"
        if style_id == STYLE_BACKSTAB:
            return "combat.need_blade"
        return "combat.wrong_weapon"
    return None


def roll_backstab(player: Player) -> bool:
    chance = min(0.85, 0.35 + player.cool * 0.05)
    return random.random() < chance


def calc_strike_damage(
    *,
    style_id: str,
    player: Player,
    world: World,
    weapon_damage: int,
    bonus_damage: int,
    backstab_hit: bool,
    room_modifier,
    proficiency_bonus: int = 0,
) -> int:
    body = player.body
    prof = proficiency_bonus
    if style_id == STYLE_PUNCH:
        raw = body + bonus_damage + prof + player.cool // 2
    elif style_id == STYLE_SHOOT:
        raw = body + weapon_damage + bonus_damage + prof + player.reflex // 2
    elif style_id == STYLE_BASH:
        raw = int((body + weapon_damage + bonus_damage + prof) * 1.15)
    elif style_id == STYLE_BACKSTAB and backstab_hit:
        raw = int((body + weapon_damage + bonus_damage + prof) * 2.0) + player.cool
    elif style_id == STYLE_BACKSTAB:
        raw = body + weapon_damage + bonus_damage + prof
    else:
        raw = body + weapon_damage + bonus_damage + prof
    return room_modifier(raw)