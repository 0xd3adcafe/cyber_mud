from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.target_resolve import resolve_item_id
from shared.i18n import t
from world.craft import perform_disassemble


def handle(ctx: CommandContext):
    target = ctx.args.strip()
    locale = ctx.player.locale
    if not target:
        return ok([t(locale, "disassemble.usage")])

    result = resolve_item_id(ctx, target, scopes=("inventory",), verb="disassemble")
    if result.needs_response:
        return ok(result.lines)
    if not result.ok:
        return ok([t(locale, "disassemble.missing", item=target)])
    item_id = result.value

    lines = perform_disassemble(ctx.player, ctx.state, item_id, locale)
    return ok(lines, meta=player_meta(ctx), world_changed=True)


register("disassemble", handle)