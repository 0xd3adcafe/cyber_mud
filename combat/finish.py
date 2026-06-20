from __future__ import annotations

from combat.actions import CombatActionResult, _finish_victory
from combat.encounter import encounter_for_player, npc_label
from entities.player import Player
from shared.i18n import t
from world.mature import is_mature
from world.mature_social import random_mature_finish_line
from world.state import WorldState

FINISH_HP_RATIO = 0.3
FINISH_HP_CAP = 15


def can_finish(encounter, npc) -> bool:
    if npc is None:
        return False
    max_hp = npc.max_hp or npc.hp or 30
    threshold = min(FINISH_HP_CAP, max(1, int(max_hp * FINISH_HP_RATIO)))
    return encounter.npc_hp > 0 and encounter.npc_hp <= threshold


def resolve_finish(state: WorldState, player: Player) -> CombatActionResult:
    locale = player.locale
    if not is_mature(player):
        return CombatActionResult([t(locale, "mature.refused")])

    encounter = encounter_for_player(state, player)
    if encounter is None:
        return CombatActionResult([t(locale, "combat.not_in_combat")])

    npc = state.world.npc(encounter.npc_id)
    label = npc_label(state, encounter.npc_id, locale)
    if not can_finish(encounter, npc):
        return CombatActionResult([t(locale, "combat.finish_too_strong", target=label)])

    lines: list[str] = []
    finish_line = random_mature_finish_line(locale, target=label)
    if finish_line:
        lines.append(finish_line)
    else:
        lines.append(t(locale, "combat.finish", target=label))

    encounter.npc_hp = 0
    return _finish_victory(state, player, encounter, lines)