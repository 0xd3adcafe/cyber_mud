from __future__ import annotations

from commands.helpers import find_item_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label


def handle(ctx: CommandContext):
    if not ctx.args:
        return ok([t(ctx.player.locale, "appraise.usage")])

    item_id = find_item_id(
        ctx.state,
        ctx.args,
        room_id=ctx.player.room_id,
        inventory=ctx.player.inventory,
    )
    if item_id is None:
        for slot, equipped_id in ctx.player.equipment.items():
            item = ctx.state.world.item(equipped_id)
            if item and find_item_id(ctx.state, ctx.args, inventory=[equipped_id]):
                item_id = equipped_id
                break

    if item_id is None:
        return ok([t(ctx.player.locale, "appraise.missing")])

    item = ctx.state.world.item(item_id)
    if item is None:
        return ok([t(ctx.player.locale, "appraise.missing")])

    label = item_label(item, ctx.player.locale)
    return ok(
        [t(ctx.player.locale, "appraise.ok", label=label, value=str(item.value))],
        meta=player_meta(ctx),
    )


register("appraise", handle)