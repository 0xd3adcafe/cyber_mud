from __future__ import annotations

from commands.helpers import current_room
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import (
    format_room_exits,
    item_label_with_id,
    net_node_label_with_id,
    npc_label_with_id,
    room_name,
)
from world.corpses import corpse_label, corpses_in_room


def handle(ctx: CommandContext):
    room = current_room(ctx)
    if room is None:
        return ok([t(ctx.player.locale, "scan.empty")])

    lines = [
        t(ctx.player.locale, "scan.header", name=room_name(room, ctx.player.locale)),
        "",
    ]

    if room.exits:
        lines.append(
            t(
                ctx.player.locale,
                "scan.exits",
                exits=format_room_exits(room, ctx.state.world, ctx.player.locale),
            )
        )

    item_ids = ctx.state.items_in_room(ctx.player.room_id)
    if item_ids:
        labels = []
        for item_id in item_ids:
            item = ctx.state.world.item(item_id)
            if item:
                labels.append(item_label_with_id(item, ctx.player.locale))
        lines.append(t(ctx.player.locale, "scan.items", items="、".join(labels)))

    npc_labels = []
    for npc_id in ctx.state.npcs_in_room(ctx.player.room_id):
        npc = ctx.state.world.npc(npc_id)
        if npc:
            npc_labels.append(npc_label_with_id(npc, ctx.player.locale))
    if npc_labels:
        lines.append(t(ctx.player.locale, "scan.npcs", npcs="、".join(npc_labels)))

    if ctx.player.net_shell:
        net_labels = [
            net_node_label_with_id(node, ctx.player.locale)
            for node in ctx.state.world.net_nodes_in_room(ctx.player.room_id)
        ]
        if net_labels:
            lines.append(t(ctx.player.locale, "scan.net_nodes", nodes="、".join(net_labels)))

    corpse_labels = [corpse_label(ctx.state, corpse, ctx.player.locale) for corpse in corpses_in_room(ctx.state, ctx.player.room_id)]
    if corpse_labels:
        lines.append(t(ctx.player.locale, "corpse.room_line", corpses="、".join(corpse_labels)))

    for peer in ctx.peers:
        if peer.named:
            lines.append(t(ctx.player.locale, "scan.player", name=peer.name))

    hint = room.hidden_hint_zh if ctx.player.locale == "zh" else (room.hidden_hint_en or room.hidden_hint_zh)
    if hint:
        lines.append("")
        lines.append(t(ctx.player.locale, "scan.hidden", hint=hint))

    return ok(lines, meta=player_meta(ctx))


register("scan", handle)
register("search", handle)