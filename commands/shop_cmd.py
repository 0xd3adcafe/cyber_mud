from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.trade import active_shop, format_shop_lines, shop_access_error


def handle(ctx: CommandContext):
    error = shop_access_error(ctx)
    if error is not None:
        key, kwargs = error
        return ok([t(ctx.player.locale, key, **kwargs)])

    shop = active_shop(ctx)
    if shop is None:
        return ok([t(ctx.player.locale, "trade.no_shop")])

    return ok(format_shop_lines(ctx, shop), meta=player_meta(ctx))


register("shop", handle)