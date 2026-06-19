from __future__ import annotations

from commands.helpers import format_look
from commands.registry import CommandContext, ok, ok_document, player_meta, register
from shared.i18n import t


def handle(ctx: CommandContext):
    if ctx.player.in_combat:
        return ok([t(ctx.player.locale, "combat.busy")])

    tutorial = "tutorial"
    if tutorial not in ctx.state.world.rooms:
        return ok([t(ctx.player.locale, "recall.no_tutorial")])

    ctx.player.room_id = tutorial
    lines = [t(ctx.player.locale, "recall.ok"), ""]
    lines.extend(format_look(ctx))
    return ok_document(lines, meta=player_meta(ctx), moved=True, world_changed=True)


register("recall", handle)