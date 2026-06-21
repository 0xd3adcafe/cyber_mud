from __future__ import annotations

from commands.net_shell import _sector_context_lines, net_meta
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t


def enter_net_shell(ctx: CommandContext):
    if ctx.player.in_combat:
        return ok([t(ctx.player.locale, "combat.busy")], meta=player_meta(ctx))
    if ctx.player.net_shell:
        return ok([t(ctx.player.locale, "net.already")], meta=net_meta(ctx))

    from world.net_session import clear_net_session

    ctx.player.net_shell = True
    clear_net_session(ctx.player)
    lines = [
        t(ctx.player.locale, "net.enter"),
        "",
        t(ctx.player.locale, "net.help_header"),
        t(ctx.player.locale, "net.help_line", name="probe", desc=t(ctx.player.locale, "net.help_cmds.probe")),
        t(ctx.player.locale, "net.help_line", name="hack", desc=t(ctx.player.locale, "net.help_cmds.hack")),
        t(ctx.player.locale, "net.help_line", name="exit", desc=t(ctx.player.locale, "net.help_cmds.exit")),
    ]
    sector = _sector_context_lines(ctx)
    if sector:
        lines.extend(["", *sector])
    return ok(lines, meta=net_meta(ctx))


def handle(ctx: CommandContext):
    return enter_net_shell(ctx)


register("net", handle)
register("netrun", handle)