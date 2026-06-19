from __future__ import annotations

from commands.registry import CommandContext, CommandResult, ok, player_meta
from shared.i18n import t
from shared.names import matches_name

NET_SHELL_COMMANDS = frozenset({"hack", "probe", "exit", "help", "status"})


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


def _find_node(ctx: CommandContext, target: str):
    for node in _nodes_in_room(ctx):
        if matches_name(target, node.id, node.name_zh, node.name_en):
            return node
    return None


def _handle_hack(ctx: CommandContext) -> CommandResult:
    target = ctx.args.strip()
    if not target:
        return ok([t(ctx.player.locale, "net.hack_usage")], meta=net_meta(ctx))

    node = _find_node(ctx, target)
    if node is None:
        return ok([t(ctx.player.locale, "net.no_node")], meta=net_meta(ctx))

    if ctx.player.ram < 1:
        return ok([t(ctx.player.locale, "net.no_ram")], meta=net_meta(ctx))

    ctx.player.ram -= 1
    label = node.name_zh if ctx.player.locale == "zh" else (node.name_en or node.name_zh)
    return ok(
        [t(ctx.player.locale, "net.hack_ok", target=label)],
        meta=net_meta(ctx),
        world_changed=True,
    )


def _handle_probe(ctx: CommandContext) -> CommandResult:
    nodes = _nodes_in_room(ctx)
    if not nodes:
        return ok([t(ctx.player.locale, "net.probe_empty")], meta=net_meta(ctx))

    labels = []
    for node in nodes:
        labels.append(node.name_zh if ctx.player.locale == "zh" else (node.name_en or node.name_zh))
    return ok(
        [t(ctx.player.locale, "net.probe_ok", nodes="、".join(labels))],
        meta=net_meta(ctx),
    )


def _handle_exit(ctx: CommandContext) -> CommandResult:
    ctx.player.net_shell = False
    return ok(
        [t(ctx.player.locale, "net.exit")],
        meta=player_meta(ctx),
    )


def _handle_help(ctx: CommandContext) -> CommandResult:
    lines = [t(ctx.player.locale, "net.help_header"), ""]
    for key in ("hack", "probe", "status", "exit", "help"):
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
    nodes = _nodes_in_room(ctx)
    count = len(nodes)
    return ok(
        [
            t(
                ctx.player.locale,
                "net.status",
                ram=f"{ctx.player.ram}/{ctx.player.max_ram}",
                nodes=str(count),
            )
        ],
        meta=net_meta(ctx),
    )


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


