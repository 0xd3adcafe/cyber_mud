from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.factions import adjusted_buy_price, adjusted_sell_price, shop_rate_modifiers
from world.loader import load_world
from world.quests import accept_quest, quest_available


def test_tyrell_shop_discount():
    world = load_world()
    shop = world.shop("square_market")
    player = make_player(faction="tyrell")
    buy_mult, sell_mult = shop_rate_modifiers(player, shop)
    assert buy_mult < 1.0
    assert sell_mult > 1.0
    assert adjusted_buy_price(100, player, shop) == 88
    assert adjusted_sell_price(100, player, shop) == 112


def test_tyrell_talk_branch():
    state = make_state()
    player = make_player(locale="en", room_id="square", faction="tyrell")
    result = dispatch("talk broker", player, state, [], [])
    assert any("Tyrell" in line or "tyrell" in line.lower() for line in result.lines)


def test_tyrell_intel_requires_pledge():
    state = make_state()
    player = make_player(locale="en")
    player.quest_flags["hack_core"] = "done"
    quest = state.world.quest("tyrell_intel")
    assert quest is not None
    assert not quest_available(player, quest)

    player.faction = "tyrell"
    assert quest_available(player, quest)


def test_buy_applies_faction_price():
    state = make_state()
    player = make_player(locale="en", room_id="square", faction="tyrell", gold=500)
    before = dispatch("buy glowstick", player, state, [], [])
    assert player.gold == 500 - 10  # 12 * 0.88 rounded via int = 10
    assert before.lines