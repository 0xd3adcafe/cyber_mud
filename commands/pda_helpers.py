from __future__ import annotations

from commands.helpers import faction_label
from commands.registry import CommandContext
from shared.i18n import t
from shared.locale_content import item_label
from shared.ui_json import panel_json


def format_pda(ctx: CommandContext) -> list[str]:
    locale = ctx.player.locale
    clock = ctx.state.clock
    config = ctx.state.time_config
    lines = [
        t(locale, "pda.header", name=ctx.player.name),
        "",
        t(
            locale,
            "pda.vitals",
            hp=f"{ctx.player.hp}/{ctx.player.max_hp}",
            gold=str(ctx.player.gold),
        ),
        t(
            locale,
            "pda.time",
            clock=clock.format_clock(locale),
            period=clock.format_period(locale, config),
        ),
        t(
            locale,
            "pda.stats",
            body=str(ctx.player.body),
            reflex=str(ctx.player.reflex),
            tech=str(ctx.player.tech),
            cool=str(ctx.player.cool),
            intelligence=str(ctx.player.intelligence),
        ),
        t(locale, "pda.ram", ram=f"{ctx.player.ram}/{ctx.player.max_ram}"),
        t(
            locale,
            "pda.social",
            humanity=str(ctx.player.humanity),
            reputation=str(ctx.player.reputation),
        ),
        t(locale, "pda.faction", faction=faction_label(ctx.state.world, ctx.player.faction, locale)),
        "",
        t(locale, "pda.implants_header"),
    ]
    if ctx.player.implants:
        for implant_id in ctx.player.implants:
            implant = ctx.state.world.implant(implant_id)
            if implant:
                label = implant.name_zh if locale == "zh" else (implant.name_en or implant.name_zh)
                lines.append(f"  • {label}")
            else:
                lines.append(f"  • {implant_id}")
    else:
        lines.append(t(locale, "pda.no_implants"))
    lines.append("")
    lines.append(t(locale, "pda.equipment_header"))
    for slot in ("weapon", "armor", "head", "cyber"):
        item_id = ctx.player.equipment.get(slot, "")
        if item_id:
            item = ctx.state.world.item(item_id)
            lines.append(f"  {slot}: {item_label(item, locale)}")
        else:
            lines.append(t(locale, "pda.no_equip", slot=slot))
    lines.append("")
    lines.append(t(locale, "pda.skills_header"))
    if ctx.player.skills:
        for skill_id in ctx.player.skills:
            lines.append(f"  • {skill_id}")
    else:
        lines.append(t(locale, "pda.no_skills"))
    return lines


def build_pda_ui(ctx: CommandContext) -> str:
    locale = ctx.player.locale
    sections = [
        {
            "kind": "row",
            "label": "HP",
            "value": f"{ctx.player.hp}/{ctx.player.max_hp}",
        },
        {
            "kind": "row",
            "label": t(locale, "pda.stats_label"),
            "value": t(
                locale,
                "pda.stats",
                body=str(ctx.player.body),
                reflex=str(ctx.player.reflex),
                tech=str(ctx.player.tech),
                cool=str(ctx.player.cool),
                intelligence=str(ctx.player.intelligence),
            ),
        },
        {
            "kind": "row",
            "label": "RAM",
            "value": f"{ctx.player.ram}/{ctx.player.max_ram}",
        },
        {
            "kind": "row",
            "label": t(locale, "pda.social_label"),
            "value": t(
                locale,
                "pda.social",
                humanity=str(ctx.player.humanity),
                reputation=str(ctx.player.reputation),
            ),
        },
        {
            "kind": "row",
            "label": t(locale, "pda.faction_label"),
            "value": faction_label(ctx.state.world, ctx.player.faction, locale),
        },
    ]
    if ctx.player.implants:
        implant_lines = []
        for implant_id in ctx.player.implants:
            implant = ctx.state.world.implant(implant_id)
            if implant:
                label = implant.name_zh if locale == "zh" else (implant.name_en or implant.name_zh)
                implant_lines.append(label)
            else:
                implant_lines.append(implant_id)
        sections.append({"kind": "list", "title": t(locale, "pda.implants_header"), "items": implant_lines})
    return panel_json(panel="pda", title=t(locale, "pda.header", name=ctx.player.name), sections=sections)