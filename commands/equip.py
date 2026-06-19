from __future__ import annotations

from commands.bulk_helpers import is_bulk, resolve_equip_targets
from commands.registry import CommandContext, ok, player_meta, register
from shared.equipment import EQUIP_SLOTS
from shared.i18n import t
from shared.locale_content import item_label


def _equip_one(ctx: CommandContext, item_id: str) -> str | None:
    item = ctx.state.world.item(item_id)
    if item is None or item_id not in ctx.player.inventory:
        return None
    if not item.slot or item.slot not in EQUIP_SLOTS:
        return t(ctx.player.locale, "equip.no_slot")
    if item.implant_id:
        return t(ctx.player.locale, "equip.use_install")
    slot = item.slot
    old_id = ctx.player.equipment.get(slot)
    if old_id:
        ctx.player.inventory.append(old_id)
    ctx.player.inventory.remove(item_id)
    ctx.player.equipment[slot] = item_id
    return t(ctx.player.locale, "equip.ok", label=item_label(item, ctx.player.locale), slot=slot)


def handle(ctx: CommandContext):
    if not ctx.args:
        return ok([t(ctx.player.locale, "equip.usage")])

    targets = resolve_equip_targets(ctx, ctx.args)
    if not targets:
        return ok([t(ctx.player.locale, "equip.missing")])

    lines: list[str] = []
    equipped = 0
    for item_id in targets:
        msg = _equip_one(ctx, item_id)
        if msg:
            lines.append(msg)
            equipped += 1
    if not lines:
        return ok([t(ctx.player.locale, "equip.missing")])
    if is_bulk(ctx.args) and equipped:
        lines.insert(0, t(ctx.player.locale, "equip.bulk_ok", count=str(equipped)))
    return ok(
        lines,
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("equip", handle)