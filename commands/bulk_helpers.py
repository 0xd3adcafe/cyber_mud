from __future__ import annotations

from commands.helpers import find_item_id
from commands.registry import CommandContext
from shared.equipment import EQUIP_SLOTS

BULK_MARKERS = frozenset({"all", "全部", "*"})


def is_bulk(args: str) -> bool:
    text = args.strip()
    return text.lower() in BULK_MARKERS or text in BULK_MARKERS


def resolve_take_targets(ctx: CommandContext, args: str) -> list[str]:
    if is_bulk(args):
        targets: list[str] = []
        for item_id in ctx.state.items_in_room(ctx.player.room_id):
            item = ctx.state.world.item(item_id)
            if item and item.takeable:
                targets.append(item_id)
        return targets
    item_id = find_item_id(ctx.state, args, room_id=ctx.player.room_id)
    return [item_id] if item_id else []


def resolve_inventory_targets(ctx: CommandContext, args: str) -> list[str]:
    if is_bulk(args):
        return list(ctx.player.inventory)
    item_id = find_item_id(ctx.state, args, inventory=ctx.player.inventory)
    return [item_id] if item_id else []


def resolve_equip_targets(ctx: CommandContext, args: str) -> list[str]:
    if is_bulk(args):
        targets: list[str] = []
        for item_id in ctx.player.inventory:
            item = ctx.state.world.item(item_id)
            if item and item.slot in EQUIP_SLOTS and not item.implant_id:
                targets.append(item_id)
        return targets
    item_id = find_item_id(ctx.state, args, inventory=ctx.player.inventory)
    return [item_id] if item_id else []


def resolve_unequip_targets(ctx: CommandContext, args: str) -> list[str]:
    if is_bulk(args):
        return list(ctx.player.equipment.values())
    item_id = find_item_id(ctx.state, args, inventory=list(ctx.player.equipment.values()))
    if item_id and item_id in ctx.player.equipment.values():
        return [item_id]
    for slot, equipped_id in ctx.player.equipment.items():
        item = ctx.state.world.item(equipped_id)
        if item and find_item_id(ctx.state, args, inventory=[equipped_id]):
            return [equipped_id]
        if slot == args.strip().lower():
            return [equipped_id]
    return []