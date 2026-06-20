from __future__ import annotations

from unittest.mock import patch

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.status_effects import (
    EFFECT_OVERHEAT,
    EFFECT_POISON,
    player_overheat_damage_multiplier,
    poison_tick_damage,
)
from world.trauma import apply_player_poison, tick_player_status


def test_poison_tick_damage_scales_with_body():
    assert poison_tick_damage(10) == 2
    assert poison_tick_damage(3) == 1


def test_overheat_reduces_damage_multiplier():
    assert player_overheat_damage_multiplier({}) == 1.0
    assert player_overheat_damage_multiplier({EFFECT_OVERHEAT: 2}) == 0.85


def test_poison_ticks_out_of_combat():
    player = make_player(locale="en", hp=100, body=10)
    apply_player_poison(player, duration=2)
    lines = tick_player_status(player, "en")
    assert player.hp < 100
    assert any("Toxin" in line for line in lines)


def test_antidote_cures_poison():
    player = make_player(locale="en")
    state = make_state()
    apply_player_poison(player, duration=3)
    player.inventory.append("antidote")
    result = dispatch("use antidote", player, state, [], [])
    assert EFFECT_POISON not in player.player_status
    assert any("flushes" in line.lower() or "沖刷" in line for line in result.lines)


def test_quickhack_applies_player_overheat():
    from combat.encounter import encounter_for_player

    player = make_player(locale="en")
    player.skills = ["quickhack"]
    player.ram = 8
    state = make_state()
    state.npc_rooms["thug"] = "alley"
    player.room_id = "alley"
    dispatch("attack thug", player, state, [], [])
    enc = encounter_for_player(state, player)
    assert enc is not None
    enc.player_cd = 0
    dispatch("quickhack overheat", player, state, [], [])
    assert EFFECT_OVERHEAT in player.player_status