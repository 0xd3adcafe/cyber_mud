from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.target_resolve import resolve_braindance
from world.braindance import braindance_label, play_braindance


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    target = ctx.args.strip()
    if not target:
        lines = [t(locale, "braindance.header"), ""]
        from world.mature import is_mature

        for bid, bd in ctx.state.world.braindances.items():
            if bd.rating == "mature" and not is_mature(ctx.player):
                continue
            label = braindance_label(bd, locale)
            lines.append(t(locale, "braindance.line", name=label, cost=str(bd.cost)))
        lines.append("")
        lines.append(t(locale, "braindance.usage"))
        return ok(lines, meta=player_meta(ctx))

    bd_result = resolve_braindance(ctx, target, verb="braindance")
    if bd_result.needs_response:
        return ok(bd_result.lines)
    if not bd_result.ok:
        return ok([t(locale, "braindance.unknown", name=target)])
    bd_id = bd_result.value

    lines = play_braindance(ctx.player, ctx.state, bd_id, locale)
    return ok(lines, meta=player_meta(ctx), world_changed=True)


register("braindance", handle)
register("bd", handle)