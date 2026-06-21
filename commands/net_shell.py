from __future__ import annotations

from commands.registry import CommandContext, CommandResult, ok, player_meta
from shared.i18n import t
from shared.locale_content import item_label_with_id, net_node_label_with_id
from shared.target_resolve import resolve_net_node

NET_SHELL_COMMANDS = frozenset(
    {"hack", "probe", "exit", "help", "status", "connect", "breach", "exploit", "route", "cat", "cover"}
)
NET_ALLOWED_MUD_COMMANDS = frozenset(
    {"look", "scan", "search", "talk", "say", "jam", "distract", "go", "whisper"}
)


def net_meta(ctx: CommandContext) -> dict[str, str]:
    was_shell = ctx.player.net_shell
    ctx.player.net_shell = False
    meta = player_meta(ctx)
    ctx.player.net_shell = was_shell
    meta["net_shell"] = "1"
    meta["net_prompt"] = t(ctx.player.locale, "net.prompt")
    meta["net_trace"] = str(ctx.player.net_trace)
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


def _resolve_node_target(ctx: CommandContext, target: str, *, verb: str):
    result = resolve_net_node(ctx, target, verb=verb)
    if result.needs_response:
        return None, result.lines
    if not result.ok:
        return None, [t(ctx.player.locale, "net.no_node")]
    return result.value, None


def _handle_hack(ctx: CommandContext) -> CommandResult:
    target = ctx.args.strip()
    if not target:
        return ok([t(ctx.player.locale, "net.hack_usage")], meta=net_meta(ctx))

    from world.ctos_hacks import try_infra_hack

    infra_lines = try_infra_hack(ctx, target.lower())
    if infra_lines is not None:
        return ok(infra_lines, meta=net_meta(ctx), world_changed=True)

    node_id, err = _resolve_node_target(ctx, target, verb="hack")
    if err:
        return ok(err, meta=net_meta(ctx))

    from world.net_session import auto_hack_pipeline

    lines = auto_hack_pipeline(ctx, node_id)
    return ok(lines, meta=net_meta(ctx), world_changed=True)


def _handle_connect(ctx: CommandContext) -> CommandResult:
    target = ctx.args.strip()
    if not target:
        return ok([t(ctx.player.locale, "net.connect_usage")], meta=net_meta(ctx))
    node_id, err = _resolve_node_target(ctx, target, verb="connect")
    if err:
        return ok(err, meta=net_meta(ctx))
    from world.net_session import connect_node

    lines = connect_node(ctx.player, ctx.state, node_id, ctx.player.locale)
    return ok(lines, meta=net_meta(ctx))


def _handle_breach(ctx: CommandContext) -> CommandResult:
    target = ctx.args.strip()
    if not target:
        return ok([t(ctx.player.locale, "net.breach_usage")], meta=net_meta(ctx))
    node_id, err = _resolve_node_target(ctx, target, verb="breach")
    if err:
        return ok(err, meta=net_meta(ctx))
    from world.net_session import breach_node

    lines = breach_node(ctx, node_id)
    return ok(lines, meta=net_meta(ctx), world_changed=True)


def _handle_exploit(ctx: CommandContext) -> CommandResult:
    target = ctx.args.strip()
    if not target:
        return ok([t(ctx.player.locale, "net.exploit_usage")], meta=net_meta(ctx))
    node_id, err = _resolve_node_target(ctx, target, verb="exploit")
    if err:
        return ok(err, meta=net_meta(ctx))
    from world.net_session import exploit_node_rewards

    lines = exploit_node_rewards(ctx.player, ctx.state, node_id, ctx.player.locale)
    return ok(lines, meta=net_meta(ctx), world_changed=True)


def _resolve_mesh_target(ctx: CommandContext, target: str) -> tuple[str | None, list[str] | None]:
    from shared.names import matches_name

    needle = target.strip().lower()
    if not needle:
        return None, [t(ctx.player.locale, "net.no_node")]
    for node_id, node in ctx.state.world.net_nodes.items():
        if matches_name(needle, node.id, node.name_zh, node.name_en):
            return node_id, None
    return None, [t(ctx.player.locale, "net.no_node")]


def _handle_route(ctx: CommandContext) -> CommandResult:
    target = ctx.args.strip()
    if not target:
        return ok([t(ctx.player.locale, "net.route_usage")], meta=net_meta(ctx))
    node_id, err = _resolve_mesh_target(ctx, target)
    if err:
        return ok(err, meta=net_meta(ctx))
    from world.net_session import route_via_mesh

    lines = route_via_mesh(ctx.player, ctx.state, node_id, ctx.player.locale)
    return ok(lines, meta=net_meta(ctx))


def _handle_cat(ctx: CommandContext) -> CommandResult:
    target = ctx.args.strip()
    if not target:
        return ok([t(ctx.player.locale, "net.cat_usage")], meta=net_meta(ctx))
    from world.net_session import cat_file

    lines = cat_file(ctx.player, ctx.state, target, ctx.player.locale)
    return ok(lines, meta=net_meta(ctx))


def _handle_cover(ctx: CommandContext) -> CommandResult:
    from world.net_session import cover_traces

    lines = cover_traces(ctx.player, ctx.state, ctx.player.locale)
    return ok(lines, meta=net_meta(ctx), world_changed=True)


def _handle_probe(ctx: CommandContext) -> CommandResult:
    nodes = _nodes_in_room(ctx)
    if not nodes:
        return ok([t(ctx.player.locale, "net.probe_empty")], meta=net_meta(ctx))

    labels = _node_labels(ctx)
    lines = [t(ctx.player.locale, "net.probe_ok", nodes="、".join(labels))]
    from world.ctos_mesh import discover_mesh_in_room, format_mesh_map_lines
    from world.net_session import probe_trace_bump

    probe_trace_bump(ctx.player, 2)
    lines.extend(discover_mesh_in_room(ctx.player, ctx.state, ctx.player.room_id))
    lines.extend(format_mesh_map_lines(ctx.player, ctx.state, ctx.player.locale))
    return ok(lines, meta=net_meta(ctx))


def _handle_exit(ctx: CommandContext) -> CommandResult:
    from world.net_session import clear_net_session

    ctx.player.net_shell = False
    clear_net_session(ctx.player)
    return ok(
        [t(ctx.player.locale, "net.exit")],
        meta=player_meta(ctx),
    )


def _handle_help(ctx: CommandContext) -> CommandResult:
    lines = [t(ctx.player.locale, "net.help_header"), ""]
    for key in (
        "connect",
        "breach",
        "exploit",
        "hack",
        "probe",
        "route",
        "cat",
        "cover",
        "status",
        "look",
        "scan",
        "talk",
        "exit",
        "help",
    ):
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
    connected = ""
    if ctx.player.net_connected_node:
        node = ctx.state.world.net_node(ctx.player.net_connected_node)
        if node:
            connected = net_node_label_with_id(node, ctx.player.locale)
    lines = [
        t(
            ctx.player.locale,
            "net.status",
            ram=f"{ctx.player.ram}/{ctx.player.max_ram}",
            nodes=nodes_display,
            trace=str(ctx.player.net_trace),
            connected=connected or t(ctx.player.locale, "net.status_no_link"),
        )
    ]
    sector = _sector_context_lines(ctx)
    if sector:
        lines.extend(["", *sector])
    return ok(lines, meta=net_meta(ctx))


_NET_HANDLERS = {
    "hack": _handle_hack,
    "connect": _handle_connect,
    "breach": _handle_breach,
    "exploit": _handle_exploit,
    "route": _handle_route,
    "cat": _handle_cat,
    "cover": _handle_cover,
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