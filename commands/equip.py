from __future__ import annotations

from commands.bulk_helpers import is_bulk, resolve_equip_targets
from commands.registry import CommandContext, ok, player_meta, register
from shared.equipment import (
    apply_weapon_equip,
    is_equippable_slot,
    is_weapon_item,
    resolve_slot_id,
    resolve_weapon_equip_slot,
    slot_label,
    weapon_equip_error_key,
)
from shared.i18n import t
from shared.locale_content import item_label


def _equip_one(ctx: CommandContext, item_id: str) -> tuple[bool, list[str]]:
    item = ctx.state.world.item(item_id)
    if item is None or item_id not in ctx.player.inventory:
        return False, []
    if not item.slot or not is_equippable_slot(item.slot):
        return False, [t(ctx.player.locale, "equip.no_slot")]
    if item.implant_id:
        return False, [t(ctx.player.locale, "equip.use_install")]

    error_key = weapon_equip_error_key(item, ctx.player, ctx.state.world, ctx.player.locale)
    if error_key:
        return False, [t(ctx.player.locale, error_key)]

    if is_weapon_item(item):
        slot = resolve_weapon_equip_slot(item, ctx.player)
    else:
        slot = resolve_slot_id(item.slot)

    displaced = apply_weapon_equip(ctx.player, item, slot)
    for displaced_id in displaced:
        ctx.player.inventory.append(displaced_id)

    old_id = ctx.player.equipment.get(slot)
    if old_id:
        ctx.player.inventory.append(old_id)
    ctx.player.inventory.remove(item_id)
    ctx.player.equipment[slot] = item_id

    lines = [
        t(
            ctx.player.locale,
            "equip.ok",
            label=item_label(item, ctx.player.locale),
            slot=slot_label(slot, ctx.player.locale),
        )
    ]
    if displaced:
        labels = [item_label(ctx.state.world.item(did), ctx.player.locale) for did in displaced]
        lines.append(
            t(ctx.player.locale, "equip.cleared_secondary", items="、".join(labels)),
        )
    return True, lines


def handle(ctx: CommandContext):
    if not ctx.args:
        return ok([t(ctx.player.locale, "equip.usage")])

    targets = resolve_equip_targets(ctx, ctx.args)
    if not targets:
        return ok([t(ctx.player.locale, "equip.missing")])

    lines: list[str] = []
    equipped = 0
    for item_id in targets:
        ok_equip, msgs = _equip_one(ctx, item_id)
        lines.extend(msgs)
        if ok_equip:
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