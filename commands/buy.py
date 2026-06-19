from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label
from world.trade import (
    active_shop,
    buy_price,
    find_shop_item_id,
    shop_access_error,
    shop_label,
)


def handle(ctx: CommandContext):
    item_name = ctx.args.strip()
    if not item_name:
        return ok([t(ctx.player.locale, "buy.usage")])

    error = shop_access_error(ctx)
    if error is not None:
        key, kwargs = error
        return ok([t(ctx.player.locale, key, **kwargs)])

    shop = active_shop(ctx)
    if shop is None:
        return ok([t(ctx.player.locale, "trade.no_shop")])

    item_id = find_shop_item_id(ctx, item_name, shop)
    if item_id is None:
        return ok([t(ctx.player.locale, "buy.not_sold", item=item_name)])

    item = ctx.state.world.item(item_id)
    if item is None or not item.takeable:
        return ok([t(ctx.player.locale, "buy.not_sold", item=item_name)])

    price = buy_price(shop, item_id, ctx.state.world)
    if price is None:
        return ok([t(ctx.player.locale, "buy.not_sold", item=item_name)])

    if ctx.player.gold < price:
        return ok([t(ctx.player.locale, "buy.no_gold", cost=str(price), gold=str(ctx.player.gold))])

    ctx.player.gold -= price
    ctx.player.inventory.append(item_id)
    label = item_label(item, ctx.player.locale)
    return ok(
        [
            t(
                ctx.player.locale,
                "buy.ok",
                label=label,
                price=str(price),
                shop=shop_label(shop, ctx.player.locale),
            )
        ],
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("buy", handle)