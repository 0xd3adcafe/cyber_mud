from __future__ import annotations

from commands.auth_helpers import STARTING_GOLD, handle_register
from commands.registry import CommandContext, dispatch
from tests.conftest import make_player, make_state, save_dir  # noqa: F401


def test_shop_lists_market_wares():
    player = make_player(room_id="square")
    state = make_state()

    result = dispatch("shop", player, state, [], [])

    text = "\n".join(result.lines)
    assert "黑市" in text or "Market" in text
    assert "glowstick" in text.lower() or "螢光棒" in text
    assert "$12" in text or "12" in text


def test_buy_item_with_gold():
    player = make_player(room_id="square", gold=200)
    state = make_state()

    result = dispatch("buy glowstick", player, state, [], [])

    assert "glowstick" in player.inventory
    assert player.gold == 188
    assert any("購買" in line or "buy" in line.lower() for line in result.lines)
    assert result.world_changed


def test_buy_no_gold():
    player = make_player(room_id="square", gold=5)
    state = make_state()

    result = dispatch("buy mod_chip", player, state, [], [])

    assert "mod_chip" not in player.inventory
    assert any("不足" in line or "Not enough" in line for line in result.lines)


def test_sell_item_to_market():
    player = make_player(room_id="square", gold=0)
    player.inventory.append("glowstick")
    state = make_state()

    result = dispatch("sell glowstick", player, state, [], [])

    assert "glowstick" not in player.inventory
    assert player.gold == 5
    assert result.world_changed


def test_shop_closed_after_hours():
    player = make_player(room_id="square")
    state = make_state()
    state.clock.hour = 3

    result = dispatch("shop", player, state, [], [])

    assert any("打烊" in line or "closed" in line.lower() for line in result.lines)


def test_shop_requires_vendor():
    player = make_player(room_id="square")
    state = make_state()
    state.npc_rooms["broker"] = "alley"

    result = dispatch("buy glowstick", player, state, [], [])

    assert any("經紀人" in line or "broker" in line.lower() for line in result.lines)


def test_ripperdoc_buy_without_npc():
    player = make_player(room_id="ripper_clinic", gold=300)
    state = make_state()

    result = dispatch("buy knife", player, state, [], [])

    assert "knife" in player.inventory
    assert player.gold == 215


def test_register_grants_starting_gold(save_dir):
    player = make_player(named=False)
    state = make_state()

    handle_register(CommandContext(player, state, "Newbie secret123", [], []))

    assert player.gold == STARTING_GOLD