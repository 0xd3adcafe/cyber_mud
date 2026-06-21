from commands.registry import dispatch
from persistence.save import player_from_dict, player_to_dict
from tests.conftest import make_player, make_state
from world.footprint import add_footprint, tick_footprint_decay_player
from world.tick import process_tick
from world.wanted import add_wanted


def test_footprint_persist_roundtrip():
    player = make_player(locale="en", footprint=42)
    restored = player_from_dict(player_to_dict(player))
    assert restored.footprint == 42


def test_corpo_scan_raises_footprint():
    player = make_player(room_id="corpo_plaza", locale="en")
    state = make_state()
    before = player.footprint
    dispatch("scan", player, state, [], [])
    assert player.footprint > before


def test_high_footprint_boosts_wanted():
    player = make_player(locale="en", footprint=70)
    lines = add_wanted(player, 1, "en")
    assert player.wanted_level >= 1
    assert lines


def test_footprint_tick_decay():
    player = make_player(locale="en", footprint=10)
    state = make_state()
    tick_footprint_decay_player(player, state)
    assert player.footprint < 10


def test_add_footprint_caps_at_100():
    player = make_player(locale="en", footprint=95)
    state = make_state()
    add_footprint(player, 20, state, "en")
    assert player.footprint == 100