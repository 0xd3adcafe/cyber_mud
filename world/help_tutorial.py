from __future__ import annotations

from commands.help_cmd import HELP_CATEGORIES, _category_entries, _category_title, _help_command_desc
from commands.registry import CommandContext
from shared.i18n import t
from shared.locale_content import room_name


TUTORIAL_CATEGORIES: tuple[str, ...] = (
    "explore",
    "life",
    "items",
    "equipment",
    "cyberware",
    "combat",
    "netrun",
    "city_os",
    "quests",
    "panels",
)


def tutorial_room_ids(world) -> list[str]:
    return sorted(rid for rid in world.rooms if rid == "tutorial" or rid.startswith("tutorial_"))


def format_help_tutorial(ctx: CommandContext) -> list[str]:
    locale = ctx.player.locale
    lines = [t(locale, "help.tutorial.header"), ""]
    lines.append(t(locale, "help.tutorial.rooms_header"))
    for rid in tutorial_room_ids(ctx.state.world):
        room = ctx.state.world.room(rid)
        if room is None:
            continue
        name = room_name(room, locale)
        desc = room.description_en if locale == "en" else room.description_zh
        snippet = (desc or "").strip().splitlines()[0][:72] if desc else ""
        lines.append(t(locale, "help.tutorial.room_line", room=name, blurb=snippet))
    lines.append("")
    lines.append(t(locale, "help.tutorial.commands_header"))
    for category_id, keys in HELP_CATEGORIES:
        if category_id not in TUTORIAL_CATEGORIES:
            continue
        entries = _category_entries(ctx, keys, category_id=category_id)
        if not entries:
            continue
        lines.append(_category_title(ctx, category_id))
        for name, key in entries:
            lines.append(t(locale, "help.line", name=name, desc=_help_command_desc(ctx, key)))
        lines.append("")
    if lines and lines[-1] == "":
        lines.pop()
    lines.append("")
    lines.append(t(locale, "help.tutorial.footer"))
    return lines