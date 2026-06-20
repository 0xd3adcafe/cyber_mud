from __future__ import annotations

from commands.helpers import find_item_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.craft import perform_disassemble


def handle(ctx: CommandContext):
    target = ctx.args.strip()
    locale = ctx.player.locale
    if not target:
        return ok([t(locale, "disassemble.usage")])

    item_id = find_item_id(ctx.state, target, inventory=ctx.player.inventory)
    if item_id is None:
        return ok([t(locale, "disassemble.missing", item=target)])

    lines = perform_disassemble(ctx.player, ctx.state, item_id, locale)
    return ok(lines, meta=player_meta(ctx), world_changed=True)


register("disassemble", handle)