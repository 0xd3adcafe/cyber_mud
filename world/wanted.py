from __future__ import annotations

from entities.player import Player
from shared.i18n import t

MAX_WANTED = 5


def add_wanted(player: Player, amount: int = 1, locale: str = "zh") -> list[str]:
    if amount <= 0:
        return []
    from world.footprint import wanted_gain_multiplier

    amount = max(1, int(amount * wanted_gain_multiplier(player)))
    before = player.wanted_level
    player.wanted_level = min(MAX_WANTED, player.wanted_level + amount)
    if player.wanted_level <= before:
        return []
    return [t(locale, "wanted.increase", level=str(player.wanted_level))]


def tick_wanted_decay(player: Player, locale: str = "zh") -> list[str]:
    if player.wanted_level <= 0:
        return []
    player.wanted_level -= 1
    if player.wanted_level <= 0:
        return [t(locale, "wanted.cleared")]
    return [t(locale, "wanted.decay", level=str(player.wanted_level))]


def wanted_damage_penalty(player: Player) -> float:
    return max(0.75, 1.0 - player.wanted_level * 0.05)