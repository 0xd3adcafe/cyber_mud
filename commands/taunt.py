from __future__ import annotations

from commands.helpers import find_npc_id
from commands.registry import CommandContext, ok, player_meta, register
from combat.encounter import encounter_for_player, npc_label
from shared.i18n import t
from world.mature import is_mature
from world.mature_social import random_mature_taunt_line


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    target = ctx.args.strip()
    if not target:
        return ok([t(locale, "taunt.usage")])
    if not is_mature(ctx.player):
        return ok([t(locale, "mature.refused")])

    npc_id = find_npc_id(ctx.state, target, ctx.player.room_id)
    if npc_id is None:
        return ok([t(locale, "taunt.missing", name=target)])

    encounter = encounter_for_player(ctx.state, ctx.player)
    if encounter is None or encounter.npc_id != npc_id:
        label = npc_label(ctx.state, npc_id, locale)
        return ok([t(locale, "taunt.not_in_combat", target=label)])

    label = npc_label(ctx.state, npc_id, locale)
    line = random_mature_taunt_line(locale, target=label)
    if not line:
        return ok([t(locale, "taunt.not_in_combat", target=label)])
    return ok([line], meta=player_meta(ctx))


register("taunt", handle)