from __future__ import annotations

from combat.defend_style import defend_help_key
from commands.registry import CommandContext, ok_panel, player_meta, register
from shared.i18n import t
from shared.ui_json import panel_json


def _help_command_desc(ctx: CommandContext, key: str) -> str:
    if key == "defend":
        return t(ctx.player.locale, defend_help_key(ctx.player, ctx.state.world))
    return t(ctx.player.locale, f"help_cmds.{key}")


HELP_ENTRIES = (
    ("look", "look"),
    ("go", "go"),
    ("interact", "interact"),
    ("craft", "craft"),
    ("disassemble", "disassemble"),
    ("braindance", "braindance"),
    ("take", "take"),
    ("drop", "drop"),
    ("inventory", "inventory"),
    ("equip", "equip"),
    ("unequip", "unequip"),
    ("equipment", "equipment"),
    ("install", "install"),
    ("cyberware", "cyberware"),
    ("uninstall", "uninstall"),
    ("rent", "rent"),
    ("home", "home"),
    ("stash", "stash"),
    ("transit", "transit"),
    ("vehicles", "vehicles"),
    ("drive", "drive"),
    ("use", "use"),
    ("eat", "eat"),
    ("drink", "drink"),
    ("scan", "scan"),
    ("map", "map"),
    ("give", "give"),
    ("appraise", "appraise"),
    ("shop", "shop"),
    ("buy", "buy"),
    ("sell", "sell"),
    ("attack", "attack"),
    ("shoot", "shoot"),
    ("slash", "slash"),
    ("bash", "bash"),
    ("punch", "punch"),
    ("backstab", "backstab"),
    ("defend", "defend"),
    ("flee", "flee"),
    ("quickhack", "quickhack"),
    ("gigs", "gigs"),
    ("net", "net"),
    ("pledge", "pledge"),
    ("recall", "recall"),
    ("talk", "talk"),
    ("say", "say"),
    ("learn", "learn"),
    ("stats", "stats"),
    ("talents", "talents"),
    ("improve", "improve"),
    ("mod", "mod"),
    ("pda", "pda"),
    ("time", "time"),
    ("prompt", "prompt"),
    ("login", "login"),
    ("register", "register"),
    ("help", "help"),
    ("quit", "quit"),
)


def format_help(ctx: CommandContext) -> list[str]:
    lines = [t(ctx.player.locale, "help.header"), ""]
    if not ctx.player.named:
        lines.append(t(ctx.player.locale, "auth.help_note"))
        lines.append("")
    for name, key in HELP_ENTRIES:
        if not ctx.player.named and key not in {"login", "register", "help", "quit"}:
            continue
        lines.append(t(ctx.player.locale, "help.line", name=name, desc=_help_command_desc(ctx, key)))
    return lines


def _help_ui(ctx: CommandContext) -> str:
    items = []
    for name, key in HELP_ENTRIES:
        if not ctx.player.named and key not in {"login", "register", "help", "quit"}:
            continue
        items.append(f"{name} — {_help_command_desc(ctx, key)}")
    return panel_json(
        panel="help",
        title=t(ctx.player.locale, "help.header"),
        sections=[{"kind": "list", "items": items}],
    )


def handle(ctx: CommandContext):
    return ok_panel(
        format_help(ctx),
        panel="help",
        ui_json=_help_ui(ctx),
        meta=player_meta(ctx),
    )


register("help", handle)