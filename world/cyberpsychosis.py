from __future__ import annotations

from entities.player import Player
from shared.i18n import t

PSYCHOSIS_THRESHOLD = 25


def is_cyberpsychotic(player: Player) -> bool:
    return player.humanity <= PSYCHOSIS_THRESHOLD


def player_damage_multiplier(player: Player) -> float:
    if is_cyberpsychotic(player):
        return 0.85
    return 1.0


def psychosis_warning(player: Player, locale: str) -> str | None:
    if is_cyberpsychotic(player):
        return t(locale, "cyberpsychosis.active")
    return None