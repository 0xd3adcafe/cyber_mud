from __future__ import annotations

from entities.player import Player
from shared.i18n import t
from world.state import WorldState


def braindance_label(bd, locale: str) -> str:
    if locale == "en" and bd.name_en:
        return bd.name_en
    return bd.name_zh or bd.id


def play_braindance(
    player: Player,
    state: WorldState,
    bd_id: str,
    locale: str,
    *,
    free: bool = False,
) -> list[str]:
    bd = state.world.braindance(bd_id)
    if bd is None:
        return [t(locale, "braindance.unknown", name=bd_id)]

    if bd.sets_flag and player.braindance_flags.get(bd.sets_flag) == "done":
        return [t(locale, "braindance.already", name=braindance_label(bd, locale))]

    if not free and player.gold < bd.cost:
        return [t(locale, "braindance.no_gold", cost=str(bd.cost))]

    if not free:
        player.gold -= bd.cost

    lines = list(bd.lines_zh if locale == "zh" else (bd.lines_en or bd.lines_zh))
    if bd.sets_flag:
        player.braindance_flags[bd.sets_flag] = "done"
    if bd.street_cred > 0:
        from world.street_cred import award_street_cred

        lines.extend(award_street_cred(player, bd.street_cred, locale))
    return lines