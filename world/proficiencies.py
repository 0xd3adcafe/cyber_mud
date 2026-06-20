from __future__ import annotations

from entities.player import Player
from shared.equipment import (
    BLADE_WEAPON_TYPES,
    BLUNT_WEAPON_TYPES,
    active_weapon,
)
from shared.i18n import t
from world.content import Proficiency

PROFICIENCY_MAX = 60

ATTRIBUTE_ORDER = ("body", "reflex", "tech", "intelligence", "cool")

HEAVY_WEAPON_TYPES = frozenset(
    {
        "shotgun",
        "sniper_rifle",
        "heavy_machine_gun",
    }
)

RIFLE_WEAPON_TYPES = frozenset(
    {
        "smg",
        "assault_rifle",
        "precision_rifle",
    }
)

HANDGUN_WEAPON_TYPES = frozenset(
    {
        "handgun",
        "revolver",
        "gun",
    }
)


def xp_to_next_proficiency(level: int) -> int:
    if level >= PROFICIENCY_MAX:
        return 0
    return 30 + level * 8


def proficiency_level(player: Player, prof_id: str) -> int:
    return int(player.proficiency_levels.get(prof_id, 0))


def proficiency_progress(player: Player, prof_id: str) -> int:
    return int(player.proficiency_xp.get(prof_id, 0))


def proficiency_label(prof: Proficiency, locale: str) -> str:
    if locale == "en" and prof.name_en:
        return prof.name_en
    return prof.name_zh or prof.id


def proficiency_for_weapon_type(weapon_type: str) -> str | None:
    if not weapon_type:
        return None
    if weapon_type in HANDGUN_WEAPON_TYPES:
        return "handguns"
    if weapon_type in HEAVY_WEAPON_TYPES:
        return "annihilation"
    if weapon_type in RIFLE_WEAPON_TYPES:
        return "assault"
    if weapon_type in BLADE_WEAPON_TYPES:
        return "blades"
    if weapon_type in BLUNT_WEAPON_TYPES:
        return "street_brawler"
    return None


def proficiency_for_strike(player, world, *, style_id: str) -> str | None:
    if style_id == "punch":
        return "street_brawler"
    if style_id == "backstab":
        return "stealth"
    if style_id == "bash":
        return "street_brawler"
    item = active_weapon(player, world)
    if item is None:
        return "street_brawler"
    return proficiency_for_weapon_type(item.weapon_type or "")


def proficiency_damage_bonus(player: Player, prof_id: str | None) -> int:
    if not prof_id:
        return 0
    return proficiency_level(player, prof_id) // 5


def proficiency_quickhack_multiplier(player: Player) -> float:
    level = proficiency_level(player, "quickhacking")
    return 1.0 + level * 0.01


def award_proficiency_xp(
    player: Player,
    prof_id: str,
    amount: int,
    locale: str,
    *,
    proficiencies: dict[str, Proficiency] | None = None,
) -> list[str]:
    if amount <= 0 or not prof_id:
        return []
    if proficiencies is not None and prof_id not in proficiencies:
        return []

    lines: list[str] = []
    current_level = proficiency_level(player, prof_id)
    if current_level >= PROFICIENCY_MAX:
        return lines

    player.proficiency_xp[prof_id] = proficiency_progress(player, prof_id) + amount
    while (
        proficiency_level(player, prof_id) < PROFICIENCY_MAX
        and player.proficiency_xp.get(prof_id, 0) >= xp_to_next_proficiency(proficiency_level(player, prof_id))
    ):
        need = xp_to_next_proficiency(proficiency_level(player, prof_id))
        player.proficiency_xp[prof_id] -= need
        new_level = proficiency_level(player, prof_id) + 1
        player.proficiency_levels[prof_id] = new_level
        label = prof_id
        if proficiencies and prof_id in proficiencies:
            label = proficiency_label(proficiencies[prof_id], locale)
        lines.append(
            t(
                locale,
                "proficiency.level_up",
                skill=label,
                level=str(new_level),
            )
        )
    return lines


def format_proficiency_stats(player: Player, proficiencies: dict[str, Proficiency], locale: str) -> list[str]:
    by_attr: dict[str, list[str]] = {attr: [] for attr in ATTRIBUTE_ORDER}
    for prof_id, prof in proficiencies.items():
        level = proficiency_level(player, prof_id)
        if level <= 0:
            continue
        label = proficiency_label(prof, locale)
        by_attr.setdefault(prof.attribute, []).append(f"{label} {level}")

    lines = [t(locale, "stats.proficiencies_header"), ""]
    has_any = False
    for attr in ATTRIBUTE_ORDER:
        entries = by_attr.get(attr, [])
        if not entries:
            continue
        has_any = True
        attr_label = t(locale, f"improve.stat.{attr}")
        lines.append(t(locale, "stats.proficiency_group", attribute=attr_label, skills=" │ ".join(entries)))
    if not has_any:
        lines.append(t(locale, "stats.no_proficiencies"))
    return lines