from __future__ import annotations

from commands.registry import CommandContext, ok_panel, player_meta, register
from shared.i18n import t
from shared.ui_json import panel_json


HELP_ENTRIES = (
    ("look", "look"),
    ("go", "go"),
    ("take", "take"),
    ("drop", "drop"),
    ("inventory", "inventory"),
    ("equip", "equip"),
    ("unequip", "unequip"),
    ("equipment", "equipment"),
    ("install", "install"),
    ("scan", "scan"),
    ("map", "map"),
    ("give", "give"),
    ("appraise", "appraise"),
    ("attack", "attack"),
    ("defend", "defend"),
    ("flee", "flee"),
    ("quickhack", "quickhack"),
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
        lines.append(t(ctx.player.locale, "help.line", name=name, desc=t(ctx.player.locale, f"help_cmds.{key}")))
    return lines


def _help_ui(ctx: CommandContext) -> str:
    items = []
    for name, key in HELP_ENTRIES:
        if not ctx.player.named and key not in {"login", "register", "help", "quit"}:
            continue
        items.append(f"{name} — {t(ctx.player.locale, f'help_cmds.{key}')}")
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