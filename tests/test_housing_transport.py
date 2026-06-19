from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_rent_and_home():
    player = make_player(room_id="square", gold=600)
    state = make_state()
    result = dispatch("rent watson_flat", player, state, [], [])
    assert player.home_room_id == "watson_flat"
    assert player.gold == 100
    assert any("租" in line for line in result.lines)

    dispatch("home", player, state, [], [])
    assert player.room_id == "watson_flat"


def test_stash_put_take():
    player = make_player(room_id="square", gold=600)
    state = make_state()
    dispatch("rent watson_flat", player, state, [], [])
    dispatch("take glowstick", player, state, [], [])
    dispatch("home", player, state, [], [])
    dispatch("stash put glowstick", player, state, [], [])
    assert "glowstick" not in player.inventory
    assert "glowstick" in player.home_stash
    dispatch("stash take glowstick", player, state, [], [])
    assert "glowstick" in player.inventory


def test_transit_to_docks():
    player = make_player(room_id="square", gold=50)
    state = make_state()
    dispatch("transit docks", player, state, [], [])
    assert player.room_id == "docks"
    assert player.gold == 45


def test_buy_vehicle_and_drive():
    player = make_player(room_id="docks", gold=1000)
    state = make_state()
    dispatch("vehicles buy archer", player, state, [], [])
    assert player.vehicle_id == "archer_hella"
    dispatch("drive square", player, state, [], [])
    assert player.room_id == "square"