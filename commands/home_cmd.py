from __future__ import annotations

from commands.helpers import format_look
from commands.registry import CommandContext, ok, ok_document, player_meta, register
from shared.i18n import t


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    if ctx.player.in_combat:
        return ok([t(locale, "combat.busy")])

    if not ctx.player.home_room_id:
        return ok([t(locale, "home.none")])

    if ctx.player.home_room_id not in ctx.state.world.rooms:
        return ok([t(locale, "home.missing")])

    ctx.player.room_id = ctx.player.home_room_id
    lines = [t(locale, "home.ok"), ""]
    if ctx.player.home_stash:
        lines.append(t(locale, "home.stash_hint", count=str(len(ctx.player.home_stash))))
        lines.append("")
    lines.extend(format_look(ctx))
    return ok_document(lines, meta=player_meta(ctx), moved=True, world_changed=True)


register("home", handle)