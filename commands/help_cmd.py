from commands.registry import CommandContext, ok_document, player_meta, register
from shared.i18n import t


def handle(ctx: CommandContext):
    lines = [t(ctx.player.locale, "help.header"), ""]
    for name, key in (
        ("look", "look"),
        ("go", "go"),
        ("help", "help"),
        ("quit", "quit"),
    ):
        lines.append(t(ctx.player.locale, "help.line", name=name, desc=t(ctx.player.locale, f"help_cmds.{key}")))
    return ok_document(lines, meta=player_meta(ctx))


register("help", handle)