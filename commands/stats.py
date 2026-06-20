from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.proficiencies import format_proficiency_stats
from world.progression import skill_label, talent_label, xp_to_next_level
from world.street_cred import street_cred_rank


def format_stats_lines(ctx: CommandContext) -> list[str]:
    locale = ctx.player.locale
    player = ctx.player
    next_xp = xp_to_next_level(player.level)
    lines = [
        t(locale, "stats.header", name=player.name),
        "",
        t(
            locale,
            "stats.level",
            level=str(player.level),
            xp=str(player.xp),
            next_xp=str(next_xp),
        ),
        t(
            locale,
            "stats.points",
            perks=str(player.perk_points),
            attrs=str(player.attribute_points),
        ),
        t(
            locale,
            "stats.street_cred",
            cred=str(player.street_cred),
            rank=street_cred_rank(player, locale),
            humanity=str(player.humanity),
        ),
        "",
        t(
            locale,
            "stats.attributes",
            body=str(player.body),
            reflex=str(player.reflex),
            tech=str(player.tech),
            cool=str(player.cool),
            intelligence=str(player.intelligence),
        ),
        "",
    ]
    lines.extend(format_proficiency_stats(player, ctx.state.world.proficiencies, locale))
    lines.append("")
    lines.append(t(locale, "stats.skills_header"))
    if player.skills:
        for skill_id in player.skills:
            skill = ctx.state.world.skill(skill_id)
            label = skill_label(skill, locale) if skill else skill_id
            lines.append(f"  • {label}")
    else:
        lines.append(t(locale, "stats.no_skills"))
    lines.append("")
    lines.append(t(locale, "stats.talents_header"))
    if player.perks:
        for talent_id in player.perks:
            talent = ctx.state.world.talent(talent_id)
            label = talent_label(talent, locale) if talent else talent_id
            lines.append(f"  • {label}")
    else:
        lines.append(t(locale, "stats.no_talents"))
    return lines


def handle(ctx: CommandContext):
    return ok(format_stats_lines(ctx), meta=player_meta(ctx))


register("stats", handle)