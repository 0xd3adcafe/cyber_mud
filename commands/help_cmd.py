from commands.registry import CommandContext, ok_document, player_meta, register
from shared.i18n import t


HELP_ENTRIES = (
    ("look", "look"),
    ("go", "go"),
    ("take", "take"),
    ("drop", "drop"),
    ("inventory", "inventory"),
    ("pda", "pda"),
    ("time", "time"),
    ("login", "login"),
    ("register", "register"),
    ("help", "help"),
    ("quit", "quit"),
)


def handle(ctx: CommandContext):
    lines = [t(ctx.player.locale, "help.header"), ""]
    if not ctx.player.named:
        lines.append(t(ctx.player.locale, "auth.help_note"))
        lines.append("")
    for name, key in HELP_ENTRIES:
        if not ctx.player.named and key not in {"login", "register", "help", "quit"}:
            continue
        lines.append(t(ctx.player.locale, "help.line", name=name, desc=t(ctx.player.locale, f"help_cmds.{key}")))
    return ok_document(lines, meta=player_meta(ctx))


register("help", handle)