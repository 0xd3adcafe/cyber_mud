from __future__ import annotations

from commands.helpers import faction_label
from commands.registry import CommandContext
from commands.talents_cmd import format_talent_line
from shared.equipment import EQUIP_SLOTS, slot_label
from shared.i18n import t
from shared.locale_content import item_label
from world.life import posture_label
from world.proficiencies import (
    ATTRIBUTE_ORDER,
    format_proficiency_stats,
    proficiency_label,
    proficiency_level,
)
from world.progression import skill_label, xp_to_next_level
from world.street_cred import street_cred_rank
from shared.ui_json import panel_json


def _proficiency_sidebar_items(ctx: CommandContext) -> list[str]:
    locale = ctx.player.locale
    proficiencies = ctx.state.world.proficiencies
    items: list[str] = []
    for attr in ATTRIBUTE_ORDER:
        entries: list[str] = []
        for prof_id, prof in proficiencies.items():
            if prof.attribute != attr:
                continue
            level = proficiency_level(ctx.player, prof_id)
            if level > 0:
                entries.append(f"{proficiency_label(prof, locale)} {level}")
        if entries:
            attr_label = t(locale, f"improve.stat.{attr}")
            items.append(
                t(locale, "stats.proficiency_group", attribute=attr_label, skills=" │ ".join(entries)).strip()
            )
    return items or [t(locale, "stats.no_proficiencies").strip()]


def _talent_catalog_items(ctx: CommandContext) -> list[str]:
    return [
        format_talent_line(ctx, talent).strip()
        for talent in ctx.state.world.talents.values()
    ]


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
            "pda.life",
            posture=posture_label(ctx.player.posture, locale),
            fatigue=str(ctx.player.fatigue),
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
    lines.extend(format_proficiency_stats(ctx.player, ctx.state.world.proficiencies, locale))
    lines.append("")
    lines.append(t(locale, "pda.skills_header"))
    if ctx.player.skills:
        for skill_id in ctx.player.skills:
            skill = ctx.state.world.skill(skill_id)
            lines.append(f"  • {skill_label(skill, locale) if skill else skill_id}")
    else:
        lines.append(t(locale, "pda.no_skills"))
    lines.append("")
    lines.append(t(locale, "talent.header"))
    for talent in ctx.state.world.talents.values():
        lines.append(format_talent_line(ctx, talent))
    lines.append("")
    lines.append(t(locale, "talent.hint"))
    return lines


def build_pda_ui(ctx: CommandContext) -> str:
    locale = ctx.player.locale
    clock = ctx.state.clock
    config = ctx.state.time_config
    sections: list[dict] = [
        {
            "id": "vitals",
            "kind": "row",
            "label": t(locale, "pda.ui.vitals"),
            "value": t(
                locale,
                "pda.vitals",
                hp=f"{ctx.player.hp}/{ctx.player.max_hp}",
                gold=str(ctx.player.gold),
            ),
        },
        {
            "id": "level",
            "kind": "row",
            "label": t(locale, "pda.ui.level"),
            "value": t(
                locale,
                "pda.level",
                level=str(ctx.player.level),
                xp=str(ctx.player.xp),
                next_xp=str(xp_to_next_level(ctx.player.level)),
                perks=str(ctx.player.perk_points),
                attrs=str(ctx.player.attribute_points),
            ),
        },
        {
            "id": "time",
            "kind": "row",
            "label": t(locale, "pda.ui.time"),
            "value": t(
                locale,
                "pda.time",
                clock=clock.format_clock(locale),
                period=clock.format_period(locale, config),
            ),
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
            "id": "ram",
            "kind": "row",
            "label": "RAM",
            "value": f"{ctx.player.ram}/{ctx.player.max_ram}",
        },
        {
            "id": "life",
            "kind": "row",
            "label": t(locale, "pda.life_label"),
            "value": t(
                locale,
                "pda.life",
                posture=posture_label(ctx.player.posture, locale),
                fatigue=str(ctx.player.fatigue),
            ),
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
            "id": "street_cred",
            "kind": "row",
            "label": t(locale, "pda.ui.street_cred"),
            "value": t(
                locale,
                "pda.street_cred",
                cred=str(ctx.player.street_cred),
                rank=street_cred_rank(ctx.player, locale),
            ),
        },
        {
            "id": "faction",
            "kind": "row",
            "label": t(locale, "pda.faction_label"),
            "value": faction_label(ctx.state.world, ctx.player.faction, locale),
        },
    ]

    implant_lines: list[str] = []
    if ctx.player.cyberware:
        from shared.cyberware_slots import slot_label as cyber_slot_label

        for slot, implant_id in sorted(ctx.player.cyberware.items()):
            implant = ctx.state.world.implant(implant_id)
            if implant:
                label = implant.name_zh if locale == "zh" else (implant.name_en or implant.name_zh)
                implant_lines.append(f"{cyber_slot_label(slot, locale)}: {label}")
            else:
                implant_lines.append(implant_id)
    else:
        from world.cyberware import implanted_ids

        for implant_id in implanted_ids(ctx.player):
            implant = ctx.state.world.implant(implant_id)
            if implant:
                label = implant.name_zh if locale == "zh" else (implant.name_en or implant.name_zh)
                implant_lines.append(label)
            else:
                implant_lines.append(implant_id)
    sections.append(
        {
            "kind": "list",
            "title": t(locale, "pda.implants_header"),
            "items": implant_lines or [t(locale, "pda.no_implants").strip()],
        }
    )

    equip_lines: list[str] = []
    for slot in EQUIP_SLOTS:
        item_id = ctx.player.equipment.get(slot, "")
        slot_name = slot_label(slot, locale)
        if item_id:
            item = ctx.state.world.item(item_id)
            equip_lines.append(f"{slot_name}: {item_label(item, locale)}")
        else:
            equip_lines.append(t(locale, "pda.no_equip", slot=slot_name).strip())
    sections.append({"kind": "list", "title": t(locale, "pda.equipment_header"), "items": equip_lines})

    sections.append(
        {
            "kind": "list",
            "title": t(locale, "stats.proficiencies_header"),
            "items": _proficiency_sidebar_items(ctx),
        }
    )

    skill_lines = [
        skill_label(ctx.state.world.skill(skill_id), locale) if ctx.state.world.skill(skill_id) else skill_id
        for skill_id in ctx.player.skills
    ]
    sections.append(
        {
            "kind": "list",
            "title": t(locale, "pda.skills_header"),
            "items": skill_lines or [t(locale, "pda.no_skills").strip()],
        }
    )

    sections.append(
        {
            "kind": "list",
            "title": t(locale, "talent.header"),
            "items": _talent_catalog_items(ctx),
        }
    )

    return panel_json(panel="pda", title=t(locale, "pda.header", name=ctx.player.name), sections=sections)