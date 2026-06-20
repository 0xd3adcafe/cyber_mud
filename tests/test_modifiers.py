from __future__ import annotations

import random

import pytest

from combat.strike import resolve_player_attack
from combat.encounter import encounter_for_player
from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.modifiers import (
    apply_damage_modifier,
    combat_damage_multiplier,
    flee_chance_bonus,
    modified_flee_chance,
    movement_fail_chance,
    rest_period_multiplier,
    rest_unsafe_district_penalty,
    rest_weather_multiplier,
)


def test_acid_rain_reduces_damage():
    assert combat_damage_multiplier("acid_rain") == 0.9
    state = make_state()
    state.weather["watson"] = "acid_rain"
    assert apply_damage_modifier(state, "alley", 10) == 8


def test_fog_increases_flee_chance():
    assert flee_chance_bonus("fog") == 0.10
    state = make_state()
    state.weather["docks"] = "fog"
    modified = modified_flee_chance(0.5, state, "docks")
    assert modified == 0.65


def test_neon_haze_has_no_penalty():
    assert combat_damage_multiplier("neon_haze") == 1.0
    assert flee_chance_bonus("neon_haze") == 0.0
    assert movement_fail_chance("neon_haze") == 0.0


def test_acid_rain_affects_combat_damage():
    player = make_player(room_id="alley", name="Vy")
    player.body = 10
    state = make_state()
    state.weather["watson"] = "acid_rain"
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    assert encounter.npc_hp == 21


def test_rest_weather_outdoor_penalty():
    assert rest_weather_multiplier("acid_rain", outdoor=True, table={"acid_rain": 0.35}) == 0.35
    assert rest_weather_multiplier("acid_rain", outdoor=False, table={"acid_rain": 0.35}) == 1.0


def test_rest_period_indoor_night_bonus():
    assert rest_period_multiplier("night", indoor=True, table={"night": 1.2}) == pytest.approx(1.32)


def test_rest_unsafe_district_penalty():
    assert rest_unsafe_district_penalty(1, 2, outdoor=True) == 0.5
    assert rest_unsafe_district_penalty(2, 2, outdoor=True) == 1.0


def test_movement_blocked_by_weather(monkeypatch):
    player = make_player(room_id="alley")
    state = make_state()
    state.weather["watson"] = "acid_rain"
    monkeypatch.setattr(random, "random", lambda: 0.0)
    result = dispatch("go south", player, state, [], [])
    assert player.room_id == "alley"
    assert any("天氣" in line for line in result.lines)