from __future__ import annotations

from commands.registry import CommandContext
from shared.i18n import t


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
        "",
        t(locale, "pda.implants_header"),
    ]
    if ctx.player.implants:
        for implant_id in ctx.player.implants:
            lines.append(f"  • {implant_id}")
    else:
        lines.append(t(locale, "pda.no_implants"))
    lines.append("")
    lines.append(t(locale, "pda.skills_header"))
    if ctx.player.skills:
        for skill_id in ctx.player.skills:
            lines.append(f"  • {skill_id}")
    else:
        lines.append(t(locale, "pda.no_skills"))
    return lines