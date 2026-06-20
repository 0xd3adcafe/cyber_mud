from __future__ import annotations

from commands.bulk_helpers import is_bulk, resolve_inventory_targets
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label


def handle(ctx: CommandContext):
    if not ctx.args:
        return ok([t(ctx.player.locale, "drop.usage")])

    resolved = resolve_inventory_targets(ctx, ctx.args)
    if resolved.needs_response:
        return ok(resolved.lines)
    targets = resolved.value or []
    if not targets:
        return ok([t(ctx.player.locale, "drop.missing")])

    lines: list[str] = []
    dropped = 0
    for item_id in targets:
        if item_id not in ctx.player.inventory:
            continue
        for slot, equipped_id in list(ctx.player.equipment.items()):
            if equipped_id == item_id:
                del ctx.player.equipment[slot]
        ctx.player.inventory.remove(item_id)
        ctx.state.room_items.setdefault(ctx.player.room_id, []).append(item_id)
        item = ctx.state.world.item(item_id)
        lines.append(t(ctx.player.locale, "drop.ok", label=item_label(item, ctx.player.locale)))
        dropped += 1

    if not lines:
        return ok([t(ctx.player.locale, "drop.missing")])

    if is_bulk(ctx.args) and dropped > 1:
        lines.insert(0, t(ctx.player.locale, "drop.bulk_ok", count=str(dropped)))

    return ok(
        lines,
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("drop", handle)