from __future__ import annotations

from commands.registry import CommandContext
from shared.i18n import t
from shared.locale_content import item_label, room_description, room_name
from shared.names import matches_name
from world.state import WorldState


def find_item_id(
    state: WorldState,
    item_name: str,
    *,
    room_id: str | None = None,
    inventory: list[str] | None = None,
) -> str | None:
    pools: list[list[str]] = []
    if room_id is not None:
        pools.append(state.items_in_room(room_id))
    if inventory is not None:
        pools.append(inventory)
    for pool in pools:
        for item_id in pool:
            item = state.world.item(item_id)
            if item and matches_name(item_name, item.id, item.name_zh, item.name_en):
                return item_id
    return None


def current_room(ctx: CommandContext):
    return ctx.state.world.room(ctx.player.room_id)


def format_look(ctx: CommandContext) -> list[str]:
    room = current_room(ctx)
    if room is None:
        return [t(ctx.player.locale, "look.empty")]

    lines = [
        t(ctx.player.locale, "look.header", name=room_name(room, ctx.player.locale)),
        "",
        room_description(room, ctx.player.locale),
    ]
    if room.exits:
        exits = "、".join(f"{d}→{room.exits[d]}" for d in sorted(room.exits))
        lines.append("")
        lines.append(t(ctx.player.locale, "look.exits", exits=exits))

    item_ids = ctx.state.items_in_room(ctx.player.room_id)
    if item_ids:
        labels = []
        for item_id in item_ids:
            item = ctx.state.world.item(item_id)
            if item:
                labels.append(item.name_zh if ctx.player.locale == "zh" else (item.name_en or item.name_zh))
        if labels:
            lines.append(t(ctx.player.locale, "look.items", items="、".join(labels)))

    npc_labels = []
    for npc in ctx.state.world.npcs.values():
        if npc.room_id == ctx.player.room_id:
            npc_labels.append(npc.name_zh if ctx.player.locale == "zh" else (npc.name_en or npc.name_zh))
    if npc_labels:
        lines.append(t(ctx.player.locale, "look.npcs", npcs="、".join(npc_labels)))

    return lines