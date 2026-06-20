from __future__ import annotations

from commands.registry import CommandContext
from shared.equipment import is_equippable_slot
from shared.target_resolve import TargetResolveResult, resolve_item_id

BULK_MARKERS = frozenset({"all", "全部", "*"})


def is_bulk(args: str) -> bool:
    text = args.strip()
    return text.lower() in BULK_MARKERS or text in BULK_MARKERS


def resolve_take_targets(ctx: CommandContext, args: str) -> TargetResolveResult[list[str]]:
    if is_bulk(args):
        targets: list[str] = []
        for item_id in ctx.state.items_in_room(ctx.player.room_id):
            item = ctx.state.world.item(item_id)
            if item and item.takeable:
                targets.append(item_id)
        return TargetResolveResult(value=targets)
    result = resolve_item_id(ctx, args, scopes=("ground",), verb="take")
    if result.needs_response:
        return TargetResolveResult(lines=result.lines)
    if result.ok:
        return TargetResolveResult(value=[result.value])
    return TargetResolveResult(value=[])


def resolve_inventory_targets(ctx: CommandContext, args: str) -> TargetResolveResult[list[str]]:
    if is_bulk(args):
        return TargetResolveResult(value=list(ctx.player.inventory))
    result = resolve_item_id(ctx, args, scopes=("inventory",), verb="drop")
    if result.needs_response:
        return TargetResolveResult(lines=result.lines)
    if result.ok:
        return TargetResolveResult(value=[result.value])
    return TargetResolveResult(value=[])


def resolve_equip_targets(ctx: CommandContext, args: str) -> TargetResolveResult[list[str]]:
    if is_bulk(args):
        targets: list[str] = []
        for item_id in ctx.player.inventory:
            item = ctx.state.world.item(item_id)
            if item and is_equippable_slot(item.slot) and not item.implant_id:
                targets.append(item_id)
        return TargetResolveResult(value=targets)
    result = resolve_item_id(ctx, args, scopes=("inventory",), verb="equip")
    if result.needs_response:
        return TargetResolveResult(lines=result.lines)
    if result.ok:
        return TargetResolveResult(value=[result.value])
    return TargetResolveResult(value=[])


def resolve_unequip_targets(ctx: CommandContext, args: str) -> TargetResolveResult[list[str]]:
    if is_bulk(args):
        return TargetResolveResult(value=[v for v in ctx.player.equipment.values() if v])
    from commands.helpers import resolve_equipment_slot_name

    slot = resolve_equipment_slot_name(ctx, args)
    if slot:
        item_id = ctx.player.equipment.get(slot, "")
        if item_id:
            return TargetResolveResult(value=[item_id])
    result = resolve_item_id(ctx, args, scopes=("equipped",), verb="unequip")
    if result.needs_response:
        return TargetResolveResult(lines=result.lines)
    if result.ok:
        return TargetResolveResult(value=[result.value])
    return TargetResolveResult(value=[])