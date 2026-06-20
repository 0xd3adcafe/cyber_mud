from __future__ import annotations

from entities.player import Player
from shared.i18n import t

MAX_LEVEL = 50
MAX_STAT = 20
IMPROVABLE_STATS = ("body", "reflex", "tech", "cool", "intelligence")


def xp_to_next_level(level: int) -> int:
    return 100 + max(0, level - 1) * 50


def award_xp(player: Player, amount: int, locale: str, *, state=None) -> list[str]:
    if amount <= 0 or player.level >= MAX_LEVEL:
        return []
    if state is not None:
        from combat.passives import xp_bonus_percent

        bonus = xp_bonus_percent(player, state)
        if bonus > 0:
            amount = int(amount * (100 + bonus) / 100)
    lines = [t(locale, "progression.xp_gain", amount=str(amount))]
    player.xp += amount
    while player.level < MAX_LEVEL and player.xp >= xp_to_next_level(player.level):
        player.xp -= xp_to_next_level(player.level)
        player.level += 1
        player.perk_points += 1
        player.max_hp += 5
        player.hp += 5
        if player.level % 2 == 0:
            player.attribute_points += 1
        lines.append(
            t(
                locale,
                "progression.level_up",
                level=str(player.level),
                perks=str(player.perk_points),
                attrs=str(player.attribute_points),
            )
        )
    return lines


def apply_stat_bonus(player: Player, bonus: dict[str, int]) -> None:
    for key, value in bonus.items():
        if value <= 0:
            continue
        if key == "max_hp":
            player.max_hp += value
            player.hp += value
        elif key == "max_ram":
            player.max_ram += value
            player.ram += value
        elif key in IMPROVABLE_STATS:
            current = getattr(player, key)
            setattr(player, key, min(MAX_STAT, current + value))


def npc_xp_reward(npc) -> int:
    if npc is None:
        return 0
    explicit = int(getattr(npc, "xp_reward", 0) or 0)
    if explicit > 0:
        return explicit
    return max(10, int(getattr(npc, "hp", 30)) // 2 + int(getattr(npc, "attack", 3)) * 3)


def can_learn_skill(player: Player, skill) -> str | None:
    if skill is None:
        return "learn.unknown"
    if skill.id in player.skills:
        return "learn.already"
    if player.level < skill.level_req:
        return "learn.level_req"
    if skill.prereq_skill and skill.prereq_skill not in player.skills:
        return "learn.prereq_skill"
    return None


def can_learn_talent(player: Player, talent) -> str | None:
    if talent is None:
        return "talent.unknown"
    if talent.id in player.perks:
        return "talent.already"
    if player.perk_points < 1:
        return "talent.no_points"
    if player.level < talent.level_req:
        return "talent.level_req"
    if talent.prereq_talent and talent.prereq_talent not in player.perks:
        return "talent.prereq_talent"
    if talent.prereq_skill and talent.prereq_skill not in player.skills:
        return "talent.prereq_skill"
    return None


def learn_talent(player: Player, talent) -> None:
    player.perks.append(talent.id)
    player.perk_points -= 1
    apply_stat_bonus(player, talent.stat_bonus)


def can_improve_stat(player: Player, stat: str) -> str | None:
    if stat not in IMPROVABLE_STATS:
        return "improve.unknown_stat"
    if player.attribute_points < 1:
        return "improve.no_points"
    if getattr(player, stat) >= MAX_STAT:
        return "improve.max_stat"
    return None


def improve_stat(player: Player, stat: str) -> None:
    setattr(player, stat, getattr(player, stat) + 1)
    player.attribute_points -= 1


def resolve_skill_id(world, name: str) -> str | None:
    needle = name.strip().lower()
    if not needle:
        return None
    for sid, skill in world.skills.items():
        if needle in {sid.lower(), skill.name_zh.lower(), skill.name_en.lower()}:
            return sid
    return None


def resolve_talent_id(world, name: str) -> str | None:
    needle = name.strip().lower()
    if not needle:
        return None
    for tid, talent in world.talents.items():
        if needle in {tid.lower(), talent.name_zh.lower(), talent.name_en.lower()}:
            return tid
    return None


def skill_label(skill, locale: str) -> str:
    if locale == "en" and skill.name_en:
        return skill.name_en
    return skill.name_zh or skill.id


def talent_label(talent, locale: str) -> str:
    if locale == "en" and talent.name_en:
        return talent.name_en
    return talent.name_zh or talent.id