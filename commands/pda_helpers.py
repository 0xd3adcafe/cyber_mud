from __future__ import annotations

from commands.helpers import faction_label
from commands.registry import CommandContext
from shared.equipment import EQUIP_SLOTS, slot_label
from shared.i18n import t
from shared.locale_content import item_label
from world.progression import skill_label, talent_label, xp_to_next_level
from world.street_cred import street_cred_rank
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
            "pda.level",
            level=str(ctx.player.level),
            xp=str(ctx.player.xp),
            next_xp=str(xp_to_next_level(ctx.player.level)),
            perks=str(ctx.player.perk_points),
            attrs=str(ctx.player.attribute_points),
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
        t(
            locale,
            "pda.street_cred",
            cred=str(ctx.player.street_cred),
            rank=street_cred_rank(ctx.player, locale),
        ),
        t(locale, "pda.faction", faction=faction_label(ctx.state.world, ctx.player.faction, locale)),
        "",
        t(locale, "pda.implants_header"),
    ]
    from world.cyberware import implanted_ids
    from shared.cyberware_slots import slot_label as cyber_slot_label

    if ctx.player.cyberware:
        for slot, implant_id in sorted(ctx.player.cyberware.items()):
            implant = ctx.state.world.implant(implant_id)
            label = implant.name_zh if locale == "zh" else (implant.name_en or implant.name_zh) if implant else implant_id
            lines.append(f"  • {cyber_slot_label(slot, locale)}: {label}")
    elif implanted_ids(ctx.player):
        for implant_id in implanted_ids(ctx.player):
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
    for slot in EQUIP_SLOTS:
        item_id = ctx.player.equipment.get(slot, "")
        slot_name = slot_label(slot, locale)
        if item_id:
            item = ctx.state.world.item(item_id)
            lines.append(f"  {slot_name}: {item_label(item, locale)}")
        else:
            lines.append(t(locale, "pda.no_equip", slot=slot_name))
    lines.append("")
    lines.append(t(locale, "pda.skills_header"))
    if ctx.player.skills:
        for skill_id in ctx.player.skills:
            skill = ctx.state.world.skill(skill_id)
            lines.append(f"  • {skill_label(skill, locale) if skill else skill_id}")
    else:
        lines.append(t(locale, "pda.no_skills"))
    lines.append("")
    lines.append(t(locale, "pda.talents_header"))
    if ctx.player.perks:
        for talent_id in ctx.player.perks:
            talent = ctx.state.world.talent(talent_id)
            lines.append(f"  • {talent_label(talent, locale) if talent else talent_id}")
    else:
        lines.append(t(locale, "pda.no_talents"))
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
    if ctx.player.cyberware:
        implant_lines = []
        from shared.cyberware_slots import slot_label as cyber_slot_label

        for slot, implant_id in sorted(ctx.player.cyberware.items()):
            implant = ctx.state.world.implant(implant_id)
            if implant:
                label = implant.name_zh if locale == "zh" else (implant.name_en or implant.name_zh)
                implant_lines.append(label)
            else:
                implant_lines.append(implant_id)
        sections.append({"kind": "list", "title": t(locale, "pda.implants_header"), "items": implant_lines})
    return panel_json(panel="pda", title=t(locale, "pda.header", name=ctx.player.name), sections=sections)