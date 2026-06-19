from __future__ import annotations

from commands.registry import CommandContext
from shared.locale_content import item_label_with_id
from world.content import Shop
from world.schedule import shop_is_open
from world.world import Room, World


def shop_for_room(world: World, room: Room | None) -> Shop | None:
    if room is None:
        return None
    if room.shop_id:
        return world.shop(room.shop_id)
    for shop in world.shops.values():
        if shop.room_id == room.id:
            return shop
    return None


def shop_label(shop: Shop, locale: str) -> str:
    if locale == "en" and shop.name_en:
        return shop.name_en
    return shop.name_zh or shop.id


def vendor_present(state, shop: Shop, room_id: str) -> bool:
    if not shop.npc_id:
        return True
    return shop.npc_id in state.npcs_in_room(room_id)


def shop_access_error(ctx: CommandContext) -> tuple[str, dict[str, str]] | None:
    room = ctx.state.world.room(ctx.player.room_id)
    shop = shop_for_room(ctx.state.world, room)
    if shop is None:
        return ("trade.no_shop", {})
    if not shop_is_open(shop.id, ctx.state.clock.hour):
        return ("trade.closed", {"shop": shop_label(shop, ctx.player.locale)})
    if not vendor_present(ctx.state, shop, ctx.player.room_id):
        npc = ctx.state.world.npc(shop.npc_id)
        if npc:
            vendor = npc.name_zh if ctx.player.locale == "zh" else (npc.name_en or npc.name_zh)
        else:
            vendor = shop.npc_id
        return ("trade.no_vendor", {"vendor": vendor})
    return None


def active_shop(ctx: CommandContext) -> Shop | None:
    if shop_access_error(ctx) is not None:
        return None
    room = ctx.state.world.room(ctx.player.room_id)
    return shop_for_room(ctx.state.world, room)


def find_shop_item_id(ctx: CommandContext, name: str, shop: Shop) -> str | None:
    from shared.names import matches_name

    needle = name.strip()
    if not needle:
        return None
    for item_id in shop.sells:
        item = ctx.state.world.item(item_id)
        if item and matches_name(needle, item.id, item.name_zh, item.name_en):
            return item_id
    return None


def buy_price(shop: Shop, item_id: str, world: World) -> int | None:
    if item_id not in shop.sells:
        return None
    price = shop.sells[item_id]
    if price > 0:
        return price
    item = world.item(item_id)
    if item is None:
        return None
    return max(1, item.value)


def sell_price(shop: Shop, item_id: str, world: World) -> int | None:
    if not shop.buy_items:
        return None
    item = world.item(item_id)
    if item is None or item.value <= 0:
        return None
    return max(1, int(item.value * shop.buy_rate))


def remove_player_item(player, item_id: str) -> None:
    if item_id in player.inventory:
        player.inventory.remove(item_id)
    for slot, equipped_id in list(player.equipment.items()):
        if equipped_id == item_id:
            player.equipment[slot] = ""
    player.weapon_mods.pop(item_id, None)


def format_shop_lines(ctx: CommandContext, shop: Shop) -> list[str]:
    locale = ctx.player.locale
    from shared.i18n import t

    lines = [t(locale, "trade.header", shop=shop_label(shop, locale)), ""]
    if shop.sells:
        for item_id in sorted(shop.sells):
            item = ctx.state.world.item(item_id)
            if item is None:
                continue
            price = buy_price(shop, item_id, ctx.state.world)
            if price is None:
                continue
            lines.append(
                t(
                    locale,
                    "trade.listing",
                    item=item_label_with_id(item, locale),
                    price=str(price),
                )
            )
    else:
        lines.append(t(locale, "trade.empty_stock"))
    if shop.buy_items:
        rate_pct = int(shop.buy_rate * 100)
        lines.append("")
        lines.append(t(locale, "trade.buys_items", rate=str(rate_pct)))
    lines.append("")
    lines.append(t(locale, "trade.hint"))
    return lines