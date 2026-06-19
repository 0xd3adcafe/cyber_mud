from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.progression import IMPROVABLE_STATS, can_improve_stat, improve_stat


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    stat = ctx.args.strip().lower()
    if not stat:
        stats = "／".join(t(locale, f"improve.stat.{name}") for name in IMPROVABLE_STATS)
        return ok([t(locale, "improve.usage", stats=stats)])

    error = can_improve_stat(ctx.player, stat)
    if error:
        return ok([t(locale, error)])

    improve_stat(ctx.player, stat)
    return ok(
        [
            t(
                locale,
                "improve.ok",
                stat=t(locale, f"improve.stat.{stat}"),
                value=str(getattr(ctx.player, stat)),
                remaining=str(ctx.player.attribute_points),
            )
        ],
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("improve", handle)