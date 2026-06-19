from __future__ import annotations

from commands.bulk_helpers import is_bulk, resolve_take_targets
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label


def handle(ctx: CommandContext):
    if not ctx.args:
        return ok([t(ctx.player.locale, "take.usage")])

    targets = resolve_take_targets(ctx, ctx.args)
    if not targets:
        return ok([t(ctx.player.locale, "take.missing")])

    pool = ctx.state.room_items.setdefault(ctx.player.room_id, [])
    lines: list[str] = []
    taken = 0
    for item_id in targets:
        item = ctx.state.world.item(item_id)
        if item is None or not item.takeable or item_id not in pool:
            continue
        pool.remove(item_id)
        ctx.player.inventory.append(item_id)
        lines.append(t(ctx.player.locale, "take.ok", label=item_label(item, ctx.player.locale)))
        taken += 1

    if not lines:
        return ok([t(ctx.player.locale, "take.missing")])

    if is_bulk(ctx.args) and taken > 1:
        lines.insert(0, t(ctx.player.locale, "take.bulk_ok", count=str(taken)))

    return ok(
        lines,
        meta=player_meta(ctx),
        world_changed=True,
    )


register("take", handle)