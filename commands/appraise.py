from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.target_resolve import resolve_item_id
from shared.i18n import t
from shared.locale_content import item_label
from world.trade import appraisal_value


def handle(ctx: CommandContext):
    if not ctx.args:
        return ok([t(ctx.player.locale, "appraise.usage")])

    result = resolve_item_id(
        ctx,
        ctx.args,
        scopes=("ground", "inventory", "equipped"),
        verb="appraise",
    )
    if result.needs_response:
        return ok(result.lines)
    if not result.ok:
        return ok([t(ctx.player.locale, "appraise.missing")])
    item_id = result.value

    item = ctx.state.world.item(item_id)
    if item is None:
        return ok([t(ctx.player.locale, "appraise.missing")])

    room = ctx.state.world.room(ctx.player.room_id)
    value, tier = appraisal_value(item, room)
    label = item_label(item, ctx.player.locale)
    tier_label = t(ctx.player.locale, f"appraise.tier.{tier}")
    return ok(
        [t(ctx.player.locale, "appraise.ok", label=label, value=str(value), tier=tier_label)],
        meta=player_meta(ctx),
    )


register("appraise", handle)