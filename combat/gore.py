from __future__ import annotations

import random

from entities.corpse import Corpse
from entities.player import Player
from shared.mature_i18n import tm
from world.mature import is_mature


def is_gore_worthy(damage: int, npc_max_hp: int) -> bool:
    return damage >= max(12, npc_max_hp // 2)


def gore_crit_line(locale: str, *, target: str, damage: str) -> str | None:
    key = f"combat.crit_{random.randint(1, 3)}"
    line = tm(locale, key, target=target, damage=damage)
    return line if line != key else None


def gore_kill_line(locale: str, *, target: str) -> str | None:
    key = f"combat.kill_{random.randint(1, 3)}"
    line = tm(locale, key, target=target)
    return line if line != key else None


def gore_corpse_lines(locale: str, *, name: str) -> list[str]:
    key = f"combat.corpse_{random.randint(1, 2)}"
    line = tm(locale, key, name=name)
    if line == key:
        return []
    return [line]


def maybe_gore_crit(player: Player, locale: str, *, target: str, damage: int, npc_max_hp: int) -> str | None:
    if not is_mature(player) or not is_gore_worthy(damage, npc_max_hp):
        return None
    return gore_crit_line(locale, target=target, damage=str(damage))


def maybe_gore_kill(player: Player, locale: str, *, target: str) -> str | None:
    if not is_mature(player):
        return None
    return gore_kill_line(locale, target=target)


def maybe_gore_corpse(player: Player, locale: str, corpse: Corpse, state) -> list[str]:
    if not is_mature(player) or corpse.player_name:
        return []
    from world.corpses import corpse_label

    label = corpse_label(state, corpse, locale)
    return gore_corpse_lines(locale, name=label)