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


def _tutorial_profiler_lesson(player, room_id: str, npc_id: str, locale: str) -> str | None:
    if room_id != "tutorial_net" or npc_id != "netcoach":
        return None
    flag = "tutorial_profiler"
    if player.quest_flags.get(flag):
        return None
    player.quest_flags[flag] = "done"
    key = "tutorial.profiler_lesson"
    line = t(locale, key)
    return line if line != key else None


def _scan_npc(ctx: CommandContext, target: str):
    from shared.target_resolve import resolve_npc
    from world.profiler import format_profile_scan, is_profiled, profile_npc, profiler_entry

    result = resolve_npc(ctx, target, verb="scan")
    if result.needs_response:
        return ok(result.lines)
    if not result.ok:
        return ok([t(ctx.player.locale, "profiler.usage")])

    npc_id = result.value
    profile = profiler_entry(npc_id)
    npc = ctx.state.world.npc(npc_id)
    if profile is None:
        label = npc_label_with_id(npc, ctx.player.locale) if npc else target
        return ok([t(ctx.player.locale, "profiler.no_data", name=label)])

    cached = is_profiled(ctx.player, npc_id)
    lines = format_profile_scan(profile, npc, ctx.player, cached=cached)
    if not cached:
        profile_npc(ctx.player, npc_id)
    from world.quests import advance_quest_on_profile_trait, advance_quest_on_scan

    lines.extend(advance_quest_on_scan(ctx.player, ctx.state, npc_id, ctx.player.locale))
    if not cached:
        for trait in profile.traits:
            lines.extend(
                advance_quest_on_profile_trait(ctx.player, ctx.state, npc_id, trait, ctx.player.locale)
            )
    lesson = _tutorial_profiler_lesson(ctx.player, ctx.player.room_id, npc_id, ctx.player.locale)
    if lesson:
        lines.extend(["", lesson])
    from world.footprint import CORPO_SCAN_FOOTPRINT, add_footprint, corpo_footprint_bonus

    lines.extend(
        add_footprint(
            ctx.player,
            corpo_footprint_bonus(ctx.state, ctx.player.room_id, CORPO_SCAN_FOOTPRINT),
            ctx.state,
            ctx.player.locale,
            reason="scan",
        )
    )
    return ok(lines, meta=player_meta(ctx))


def handle(ctx: CommandContext):
    target = ctx.args.strip()
    if target:
        return _scan_npc(ctx, target)

    room = current_room(ctx)
    if room is None:
        return ok([t(ctx.player.locale, "scan.empty")])

    lines = [
        t(ctx.player.locale, "scan.header", name=room_name(room, ctx.player.locale)),
        "",
    ]
    from world.mature_flavor import mature_room_flavor

    if scan_flavor := mature_room_flavor(room, ctx.player):
        lines.append(scan_flavor)
        lines.append("")

    from world.infrastructure import infrastructure_lines

    infra_lines = infrastructure_lines(room, ctx.player.locale, mode="scan")
    if infra_lines:
        lines.extend(infra_lines)
        lines.append("")

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

    from world.interactables import interactable_label

    interact_labels = [
        interactable_label(obj, ctx.player.locale)
        for obj in ctx.state.world.interactables_in_room(ctx.player.room_id)
    ]
    if interact_labels:
        lines.append(t(ctx.player.locale, "scan.interactables", objects="、".join(interact_labels)))

    from world.life import peer_posture_line

    for peer in ctx.peers:
        if peer.named:
            lines.append(t(ctx.player.locale, "scan.player", name=peer_posture_line(peer, ctx.player.locale)))

    hint = room.hidden_hint_zh if ctx.player.locale == "zh" else (room.hidden_hint_en or room.hidden_hint_zh)
    if hint:
        lines.append("")
        lines.append(t(ctx.player.locale, "scan.hidden", hint=hint))

    from world.footprint import CORPO_SCAN_FOOTPRINT, add_footprint, corpo_footprint_bonus

    lines.extend(
        add_footprint(
            ctx.player,
            corpo_footprint_bonus(ctx.state, ctx.player.room_id, CORPO_SCAN_FOOTPRINT),
            ctx.state,
            ctx.player.locale,
            reason="scan",
        )
    )
    return ok(lines, meta=player_meta(ctx))


register("scan", handle)
register("search", handle)