from __future__ import annotations

from entities.player import Player
from shared.i18n import t

STREET_CRED_PER_NPC = 2
STREET_CRED_PER_HACK = 3


def award_street_cred(player: Player, amount: int, locale: str) -> list[str]:
    if amount <= 0:
        return []
    player.street_cred += amount
    return [t(locale, "street_cred.gain", amount=str(amount), total=str(player.street_cred))]


def street_cred_rank(player: Player, locale: str) -> str:
    cred = player.street_cred
    if cred >= 50:
        return t(locale, "street_cred.rank.legend")
    if cred >= 25:
        return t(locale, "street_cred.rank.veteran")
    if cred >= 10:
        return t(locale, "street_cred.rank.rising")
    return t(locale, "street_cred.rank.nobody")