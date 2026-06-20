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

    from world.mature import gate_content_rating

    refusal = gate_content_rating(player, bd.rating, locale)
    if refusal is not None:
        return refusal

    if bd.sets_flag and player.braindance_flags.get(bd.sets_flag) == "done":
        return [t(locale, "braindance.already", name=braindance_label(bd, locale))]

    if not free and player.gold < bd.cost:
        return [t(locale, "braindance.no_gold", cost=str(bd.cost))]

    if not free:
        player.gold -= bd.cost

    from world.mature import is_mature

    if bd.rating == "mature" and is_mature(player):
        from shared.mature_i18n import tm

        mature_lines = [tm(locale, f"braindance.{bd_id}.line_{index + 1}") for index in range(8)]
        lines = [line for line in mature_lines if not line.startswith("braindance.")]
        if not lines:
            lines = list(bd.lines_zh if locale == "zh" else (bd.lines_en or bd.lines_zh))
    else:
        lines = list(bd.lines_zh if locale == "zh" else (bd.lines_en or bd.lines_zh))
    if bd.sets_flag:
        player.braindance_flags[bd.sets_flag] = "done"
    if bd.street_cred > 0:
        from world.street_cred import award_street_cred

        lines.extend(award_street_cred(player, bd.street_cred, locale))
    return lines