from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.target_resolve import resolve_item_id
from shared.i18n import t
from shared.locale_content import item_label
from world.trade import (
    active_shop,
    remove_player_item,
    sell_price,
    shop_access_error,
    shop_label,
)


def handle(ctx: CommandContext):
    item_name = ctx.args.strip()
    if not item_name:
        return ok([t(ctx.player.locale, "sell.usage")])

    error = shop_access_error(ctx)
    if error is not None:
        key, kwargs = error
        return ok([t(ctx.player.locale, key, **kwargs)])

    shop = active_shop(ctx)
    if shop is None:
        return ok([t(ctx.player.locale, "trade.no_shop")])
    if not shop.buy_items:
        return ok([t(ctx.player.locale, "sell.not_buying")])

    result = resolve_item_id(
        ctx,
        item_name,
        scopes=("ground", "inventory", "equipped"),
        verb="sell",
    )
    if result.needs_response:
        return ok(result.lines)
    if not result.ok:
        return ok([t(ctx.player.locale, "sell.missing", item=item_name)])
    item_id = result.value

    item = ctx.state.world.item(item_id)
    if item is None:
        return ok([t(ctx.player.locale, "sell.missing", item=item_name)])

    price = sell_price(shop, item_id, ctx.state.world, player=ctx.player)
    if price is None:
        return ok([t(ctx.player.locale, "sell.refused", item=item_label(item, ctx.player.locale))])

    remove_player_item(ctx.player, item_id)
    ctx.player.gold += price
    label = item_label(item, ctx.player.locale)
    return ok(
        [
            t(
                ctx.player.locale,
                "sell.ok",
                label=label,
                price=str(price),
                shop=shop_label(shop, ctx.player.locale),
            )
        ],
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("sell", handle)