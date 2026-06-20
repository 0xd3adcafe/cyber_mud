from __future__ import annotations

from combat.defend_style import defend_help_key
from commands.registry import CommandContext, ok_panel, player_meta, register
from shared.i18n import t
from shared.ui_json import panel_json

_AUTH_KEYS = frozenset({"login", "register", "help", "quit"})

HELP_CATEGORIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("auth", ("login", "register", "help", "quit")),
    ("explore", ("look", "go", "scan", "map", "interact", "time", "recall", "lang")),
    ("items", ("take", "drop", "inventory", "give", "appraise", "craft", "disassemble")),
    ("equipment", ("equip", "unequip", "equipment", "mod", "use", "eat", "drink")),
    ("cyberware", ("install", "cyberware", "uninstall")),
    ("housing", ("rent", "home", "stash")),
    ("travel", ("transit", "vehicles", "drive")),
    ("trade", ("shop", "buy", "sell")),
    ("social", ("talk", "say", "pledge", "learn")),
    ("combat", ("attack", "shoot", "slash", "bash", "punch", "backstab", "defend", "flee", "quickhack")),
    ("netrun", ("net",)),
    ("quests", ("gigs",)),
    ("growth", ("stats", "talents", "improve")),
    ("panels", ("pda", "prompt")),
    ("media", ("braindance",)),
)


def _help_command_desc(ctx: CommandContext, key: str) -> str:
    if key == "defend":
        return t(ctx.player.locale, defend_help_key(ctx.player, ctx.state.world))
    return t(ctx.player.locale, f"help_cmds.{key}")


def _category_entries(ctx: CommandContext, keys: tuple[str, ...]) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for key in keys:
        if not ctx.player.named and key not in _AUTH_KEYS:
            continue
        entries.append((key, key))
    return entries


def _category_title(ctx: CommandContext, category_id: str) -> str:
    return t(ctx.player.locale, f"help.category.{category_id}")


def format_help(ctx: CommandContext) -> list[str]:
    locale = ctx.player.locale
    lines = [t(locale, "help.header"), ""]
    if not ctx.player.named:
        lines.append(t(locale, "auth.help_note"))
        lines.append("")
    for category_id, keys in HELP_CATEGORIES:
        entries = _category_entries(ctx, keys)
        if not entries:
            continue
        lines.append(t(locale, "help.category_line", name=_category_title(ctx, category_id)))
        for name, key in entries:
            lines.append(t(locale, "help.line", name=name, desc=_help_command_desc(ctx, key)))
        lines.append("")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def _help_ui(ctx: CommandContext) -> str:
    sections: list[dict] = []
    for category_id, keys in HELP_CATEGORIES:
        items = [
            f"{name} — {_help_command_desc(ctx, key)}"
            for name, key in _category_entries(ctx, keys)
        ]
        if items:
            sections.append(
                {
                    "kind": "list",
                    "title": _category_title(ctx, category_id),
                    "items": items,
                }
            )
    return panel_json(
        panel="help",
        title=t(ctx.player.locale, "help.header"),
        sections=sections,
    )


def handle(ctx: CommandContext):
    return ok_panel(
        format_help(ctx),
        panel="help",
        ui_json=_help_ui(ctx),
        meta=player_meta(ctx),
    )


register("help", handle)