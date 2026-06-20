from __future__ import annotations

from unittest.mock import patch

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.clock import WorldClock
from world.quests import accept_quest, quest_is_done
from world.schedule import shop_is_open
from world.trade import appraisal_tier, appraisal_value


def test_docks_gray_shop_hours():
    assert shop_is_open("docks_gray", 20) is True
    assert shop_is_open("docks_gray", 12) is False


def test_street_appraisal_at_docks():
    player = make_player(room_id="docks")
    state = make_state()
    player.inventory.append("mod_chip")
    item = state.world.item("mod_chip")
    room = state.world.room("docks")
    value, tier = appraisal_value(item, room)
    assert tier == "street"
    assert value < item.value
    result = dispatch("appraise mod_chip", player, state, [], [])
    assert any(str(value) in line for line in result.lines)


def test_corp_appraisal_in_corpo_lobby():
    player = make_player(room_id="corpo_lobby", locale="en")
    state = make_state()
    player.inventory.append("mod_chip")
    item = state.world.item("mod_chip")
    room = state.world.room("corpo_lobby")
    assert appraisal_tier(room) == "corp"
    value, tier = appraisal_value(item, room)
    assert tier == "corp"
    assert value == item.value
    result = dispatch("appraise mod_chip", player, state, [], [])
    assert any("corporate" in line for line in result.lines)


def test_give_mod_chip_to_broker_advances_gray_market():
    player = make_player(room_id="square", gold=500, street_cred=5)
    state = make_state()
    state.clock = WorldClock(hour=20)
    state.npc_rooms["broker"] = "square"
    state.npc_rooms["dock_smuggler"] = "docks"
    player.quest_flags["broker_rumor"] = "done"
    accept_quest(player, state, "gray_market", "zh")
    with patch("commands.go.movement_blocked_by_weather", return_value=False):
        dispatch("go south", player, state, [], [])
    dispatch("talk smuggler", player, state, [], [])
    dispatch("buy mod_chip", player, state, [], [])
    with patch("commands.go.movement_blocked_by_weather", return_value=False):
        dispatch("go north", player, state, [], [])
    state.npc_rooms["broker"] = "square"
    result = dispatch("give mod_chip broker", player, state, [], [])
    assert "mod_chip" not in player.inventory
    assert player.quest_flags["gray_market"] == "stage_4"
    assert any("交給" in line or "give" in line.lower() for line in result.lines)
    dispatch("talk broker", player, state, [], [])
    assert player.quest_flags["gray_market"] == "ready"
    dispatch("talk broker", player, state, [], [])
    assert quest_is_done(player, "gray_market")


def test_give_npc_refused_without_quest():
    player = make_player(room_id="square")
    state = make_state()
    state.npc_rooms["broker"] = "square"
    dispatch("take glowstick", player, state, [], [])
    result = dispatch("give glowstick broker", player, state, [], [])
    assert "glowstick" in player.inventory
    assert any("不想要" in line for line in result.lines)