from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.progression import (
    can_learn_talent,
    learn_talent,
    resolve_talent_id,
    talent_label,
)


def _format_talent_line(ctx: CommandContext, talent) -> str:
    locale = ctx.player.locale
    label = talent_label(talent, locale)
    if talent.id in ctx.player.perks:
        status = t(locale, "talent.status.learned")
    elif can_learn_talent(ctx.player, talent) is None:
        status = t(locale, "talent.status.available")
    else:
        status = t(locale, "talent.status.locked", level=str(talent.level_req))
    desc = talent.description_zh if locale == "zh" else (talent.description_en or talent.description_zh)
    return t(locale, "talent.list_line", name=label, status=status, desc=desc or "")


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    target = ctx.args.strip()
    if not target:
        lines = [t(locale, "talent.header"), ""]
        for talent in ctx.state.world.talents.values():
            lines.append(_format_talent_line(ctx, talent))
        lines.append("")
        lines.append(t(locale, "talent.hint"))
        return ok(lines, meta=player_meta(ctx))

    talent_id = resolve_talent_id(ctx.state.world, target)
    talent = ctx.state.world.talent(talent_id) if talent_id else None
    error = can_learn_talent(ctx.player, talent)
    if error:
        if error == "talent.unknown":
            return ok([t(locale, error, talent=target)])
        if error == "talent.already":
            return ok([t(locale, error, talent=talent_label(talent, locale))])
        return ok([t(locale, error)])

    learn_talent(ctx.player, talent)
    return ok(
        [t(locale, "talent.ok", talent=talent_label(talent, locale))],
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("talents", handle)
register("talent", handle)
register("perks", handle)
register("perk", handle)