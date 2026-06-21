from __future__ import annotations

from entities.player import Player
from shared.i18n import t
from world.content import Shop
from world.districts import district_profile
from world.world import Room

# Buy/sell multipliers when player has pledged (1.0 = neutral).
FACTION_SHOP_RATES: dict[str, dict[str, float]] = {
    "arasaka": {"buy": 0.92, "sell": 1.08},
    "militech": {"buy": 0.94, "sell": 1.06},
    "tyrell": {"buy": 0.9, "sell": 1.1},
    "maelstrom": {"buy": 1.08, "sell": 0.92},
    "dedsec": {"buy": 1.04, "sell": 0.96},
}

# Per-shop overrides (shop_id -> faction -> {buy, sell}).
SHOP_FACTION_RATES: dict[str, dict[str, dict[str, float]]] = {
    "square_market": {
        "tyrell": {"buy": 0.88, "sell": 1.12},
        "maelstrom": {"buy": 1.12, "sell": 0.88},
    },
    "kabuki_bazaar": {
        "maelstrom": {"buy": 1.05, "sell": 0.95},
    },
    "docks_gray": {
        "maelstrom": {"buy": 0.95, "sell": 1.05},
        "arasaka": {"buy": 1.1, "sell": 0.9},
        "militech": {"buy": 1.08, "sell": 0.92},
    },
    "ripperdoc": {
        "arasaka": {"buy": 0.95, "sell": 1.05},
        "tyrell": {"buy": 0.93, "sell": 1.07},
    },
}


def shop_rate_modifiers(player: Player, shop: Shop) -> tuple[float, float]:
    if not player.faction:
        return 1.0, 1.0
    overrides = SHOP_FACTION_RATES.get(shop.id, {}).get(player.faction)
    if overrides:
        return float(overrides.get("buy", 1.0)), float(overrides.get("sell", 1.0))
    base = FACTION_SHOP_RATES.get(player.faction, {})
    return float(base.get("buy", 1.0)), float(base.get("sell", 1.0))


def adjusted_buy_price(base: int, player: Player, shop: Shop) -> int:
    buy_mult, _ = shop_rate_modifiers(player, shop)
    return max(1, int(base * buy_mult))


def adjusted_sell_price(base: int, player: Player, shop: Shop) -> int:
    _, sell_mult = shop_rate_modifiers(player, shop)
    return max(1, int(base * sell_mult))


def faction_talk_key(npc_talk_key: str, player: Player) -> str:
    if not player.faction:
        return npc_talk_key
    return f"{npc_talk_key}_{player.faction}"


def faction_quest_hint_suffix(player: Player, locale: str) -> str:
    if not player.faction:
        return ""
    key = f"faction.hint.{player.faction}"
    line = t(locale, key)
    return line if line != key else ""


def npc_aggro_modifier(player: Player, room: Room | None) -> int:
    if room is None or not room.district:
        return 0
    mod = 0
    if player.faction:
        profile = district_profile(room.district)
        if player.faction in profile.entry_blocked_factions:
            mod += 2
        elif player.faction in profile.allied_factions:
            mod -= 1
    if room.district == "corpo":
        from world.footprint import corp_aggro_bonus

        mod += corp_aggro_bonus(player)
        if player.faction == "dedsec":
            mod += 1
    return mod