from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.names import matches_name
from world.braindance import braindance_label, play_braindance


def _resolve_bd_id(ctx: CommandContext, name: str) -> str | None:
    needle = name.strip().lower()
    for bid, bd in ctx.state.world.braindances.items():
        if matches_name(needle, bid, bd.name_zh, bd.name_en):
            return bid
    return None


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

    bd_id = _resolve_bd_id(ctx, target)
    if bd_id is None:
        return ok([t(locale, "braindance.unknown", name=target)])

    lines = play_braindance(ctx.player, ctx.state, bd_id, locale)
    return ok(lines, meta=player_meta(ctx), world_changed=True)


register("braindance", handle)
register("bd", handle)