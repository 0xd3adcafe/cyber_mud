from __future__ import annotations

from commands.bulk_helpers import is_bulk, resolve_unequip_targets
from commands.registry import CommandContext, ok, player_meta, register
from shared.equipment import slot_label
from shared.i18n import t
from shared.locale_content import item_label


def _unequip_one(ctx: CommandContext, item_id: str) -> str | None:
    slot = None
    for s, equipped_id in ctx.player.equipment.items():
        if equipped_id == item_id:
            slot = s
            break
    if slot is None:
        return None
    del ctx.player.equipment[slot]
    ctx.player.inventory.append(item_id)
    item = ctx.state.world.item(item_id)
    return t(
        ctx.player.locale,
        "unequip.ok",
        label=item_label(item, ctx.player.locale),
        slot=slot_label(slot, ctx.player.locale),
    )


def handle(ctx: CommandContext):
    if not ctx.args:
        return ok([t(ctx.player.locale, "unequip.usage")])

    resolved = resolve_unequip_targets(ctx, ctx.args)
    if resolved.needs_response:
        return ok(resolved.lines)
    targets = resolved.value or []
    if not targets:
        return ok([t(ctx.player.locale, "unequip.missing")])

    lines: list[str] = []
    count = 0
    for item_id in targets:
        msg = _unequip_one(ctx, item_id)
        if msg:
            lines.append(msg)
            count += 1
    if not lines:
        return ok([t(ctx.player.locale, "unequip.missing")])
    if is_bulk(ctx.args) and count:
        lines.insert(0, t(ctx.player.locale, "unequip.bulk_ok", count=str(count)))
    return ok(
        lines,
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("unequip", handle)