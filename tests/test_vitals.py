from __future__ import annotations

from combat.encounter import start_encounter
from tests.conftest import make_player, make_state
from world.tick import process_tick
from world.vitals import apply_hp_regen, calc_hp_regen


def test_calc_hp_regen_respects_body_and_period():
    player = make_player(body=10, cool=20, hp=50, max_hp=100)
    assert calc_hp_regen(player, "morning") == 8
    assert calc_hp_regen(player, "night") == 3


def test_calc_hp_regen_skips_full_hp_and_combat():
    player = make_player(hp=100, max_hp=100)
    assert calc_hp_regen(player, "morning") == 0

    player.hp = 50
    player.in_combat = True
    assert calc_hp_regen(player, "morning") == 0


def test_tick_regen_out_of_combat():
    player = make_player(body=10, cool=0, hp=50, max_hp=100)
    state = make_state()
    state.clock.hour = 8

    result = process_tick(state, state.time_config, players=[player])

    assert player.hp == 56
    assert any(event.kind == "hp_regen" and event.player_name == player.name for event in result.events)


def test_tick_no_regen_in_combat():
    player = make_player(room_id="alley", body=10, hp=50, max_hp=100)
    state = make_state()
    start_encounter(state, player, "thug")
    state.clock.hour = 8

    result = process_tick(state, state.time_config, players=[player])

    assert player.hp == 50
    assert not any(event.kind == "hp_regen" for event in result.events)