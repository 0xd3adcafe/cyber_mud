from __future__ import annotations

from commands.registry import CommandContext, CommandResult, ok, player_meta
from shared.i18n import t
from shared.locale_content import item_label_with_id, net_node_label_with_id
from shared.target_resolve import resolve_net_node

NET_SHELL_COMMANDS = frozenset({"hack", "probe", "exit", "help", "status"})
NET_ALLOWED_MUD_COMMANDS = frozenset({"look", "scan", "search", "talk", "say", "jam", "distract"})


def net_meta(ctx: CommandContext) -> dict[str, str]:
    was_shell = ctx.player.net_shell
    ctx.player.net_shell = False
    meta = player_meta(ctx)
    ctx.player.net_shell = was_shell
    meta["net_shell"] = "1"
    meta["net_prompt"] = t(ctx.player.locale, "net.prompt")
    return meta


def _nodes_in_room(ctx: CommandContext):
    return ctx.state.world.net_nodes_in_room(ctx.player.room_id)


def _node_labels(ctx: CommandContext) -> list[str]:
    return [net_node_label_with_id(node, ctx.player.locale) for node in _nodes_in_room(ctx)]


def _sector_context_lines(ctx: CommandContext) -> list[str]:
    lines: list[str] = []
    nodes = _nodes_in_room(ctx)
    if nodes:
        labels = [net_node_label_with_id(node, ctx.player.locale) for node in nodes]
        lines.append(t(ctx.player.locale, "net.sector_nodes", nodes="、".join(labels)))
    item_ids = ctx.state.items_in_room(ctx.player.room_id)
    if item_ids:
        labels = []
        for item_id in item_ids:
            item = ctx.state.world.item(item_id)
            if item:
                labels.append(item_label_with_id(item, ctx.player.locale))
        if labels:
            lines.append(t(ctx.player.locale, "net.sector_items", items="、".join(labels)))
    return lines


def _handle_hack(ctx: CommandContext) -> CommandResult:
    target = ctx.args.strip()
    if not target:
        return ok([t(ctx.player.locale, "net.hack_usage")], meta=net_meta(ctx))

    from world.ctos_hacks import try_infra_hack

    infra_lines = try_infra_hack(ctx, target.lower())
    if infra_lines is not None:
        return ok(infra_lines, meta=net_meta(ctx), world_changed=True)

    node_result = resolve_net_node(ctx, target, verb="hack")
    if node_result.needs_response:
        return ok(node_result.lines, meta=net_meta(ctx))
    if not node_result.ok:
        return ok([t(ctx.player.locale, "net.no_node")], meta=net_meta(ctx))
    node = ctx.state.world.net_node(node_result.value)
    if node is None:
        return ok([t(ctx.player.locale, "net.no_node")], meta=net_meta(ctx))

    from commands.lock_helpers import check_entity_lock

    lock_denial = check_entity_lock(ctx, node, "hack")
    if lock_denial is not None:
        return ok(lock_denial, meta=net_meta(ctx))

    if ctx.player.ram < 1:
        return ok([t(ctx.player.locale, "net.no_ram")], meta=net_meta(ctx))

    ctx.player.ram -= 1
    from world.life import gain_fatigue

    gain_fatigue(ctx.player, "netrun")
    label = net_node_label_with_id(node, ctx.player.locale)
    from world.progression import award_xp

    lines = [t(ctx.player.locale, "net.hack_ok", target=label)]
    lines.extend(award_xp(ctx.player, 15, ctx.player.locale))
    from world.proficiencies import award_proficiency_xp

    lines.extend(
        award_proficiency_xp(
            ctx.player,
            "breach_protocol",
            18,
            ctx.player.locale,
            proficiencies=ctx.state.world.proficiencies,
        )
    )
    from world.street_cred import STREET_CRED_PER_HACK, award_street_cred

    lines.extend(award_street_cred(ctx.player, STREET_CRED_PER_HACK, ctx.player.locale))
    from world.reactions import reputation_from_net_hack, shift_reputation

    lines.extend(shift_reputation(ctx.player, reputation_from_net_hack(), ctx.player.locale))
    from world.quests import advance_quest_on_hack

    lines.extend(advance_quest_on_hack(ctx.player, ctx.state, node.id, ctx.player.locale))
    from world.footprint import CORPO_HACK_FOOTPRINT, add_footprint, corpo_footprint_bonus

    lines.extend(
        add_footprint(
            ctx.player,
            corpo_footprint_bonus(ctx.state, ctx.player.room_id, CORPO_HACK_FOOTPRINT),
            ctx.state,
            ctx.player.locale,
            reason="hack",
        )
    )
    return ok(
        lines,
        meta=net_meta(ctx),
        world_changed=True,
    )


def _handle_probe(ctx: CommandContext) -> CommandResult:
    nodes = _nodes_in_room(ctx)
    if not nodes:
        return ok([t(ctx.player.locale, "net.probe_empty")], meta=net_meta(ctx))

    labels = _node_labels(ctx)
    lines = [t(ctx.player.locale, "net.probe_ok", nodes="、".join(labels))]
    from world.ctos_mesh import discover_mesh_in_room, format_mesh_map_lines

    lines.extend(discover_mesh_in_room(ctx.player, ctx.state, ctx.player.room_id))
    lines.extend(format_mesh_map_lines(ctx.player, ctx.state, ctx.player.locale))
    return ok(lines, meta=net_meta(ctx))


def _handle_exit(ctx: CommandContext) -> CommandResult:
    ctx.player.net_shell = False
    return ok(
        [t(ctx.player.locale, "net.exit")],
        meta=player_meta(ctx),
    )


def _handle_help(ctx: CommandContext) -> CommandResult:
    lines = [t(ctx.player.locale, "net.help_header"), ""]
    for key in ("hack", "probe", "status", "look", "scan", "talk", "exit", "help"):
        lines.append(
            t(
                ctx.player.locale,
                "net.help_line",
                name=key,
                desc=t(ctx.player.locale, f"net.help_cmds.{key}"),
            )
        )
    return ok(lines, meta=net_meta(ctx))


def _handle_status(ctx: CommandContext) -> CommandResult:
    labels = _node_labels(ctx)
    nodes_display = "、".join(labels) if labels else t(ctx.player.locale, "net.status_no_nodes")
    lines = [
        t(
            ctx.player.locale,
            "net.status",
            ram=f"{ctx.player.ram}/{ctx.player.max_ram}",
            nodes=nodes_display,
        )
    ]
    sector = _sector_context_lines(ctx)
    if sector:
        lines.extend(["", *sector])
    return ok(lines, meta=net_meta(ctx))


_NET_HANDLERS = {
    "hack": _handle_hack,
    "probe": _handle_probe,
    "exit": _handle_exit,
    "help": _handle_help,
    "status": _handle_status,
}


def dispatch_net(line: str, ctx: CommandContext) -> CommandResult:
    text = line.strip()
    if not text:
        return ok([], meta=net_meta(ctx))
    parts = text.split(maxsplit=1)
    verb = parts[0].lower()
    ctx.args = parts[1] if len(parts) > 1 else ""

    handler = _NET_HANDLERS.get(verb)
    if handler is None:
        return ok([t(ctx.player.locale, "net.unknown_verb", verb=verb)], meta=net_meta(ctx))
    return handler(ctx)


