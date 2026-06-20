from __future__ import annotations

from commands.registry import CommandContext, dispatch
from tests.conftest import make_player, make_state
from world.life import POSTURE_SITTING, POSTURE_SLEEPING, POSTURE_STANDING, load_life_config
from world.status_effects import EFFECT_BLEED
from world.vitals import apply_hp_regen, calc_hp_regen


def test_sit_and_stand():
    state = make_state()
    player = make_player(locale="en", hp=80)
    ctx = CommandContext(player, state, "")

    result = dispatch("sit", player, state, [], [])
    assert player.posture == POSTURE_SITTING
    assert any("sit" in line.lower() or "down" in line.lower() for line in result.lines)

    result = dispatch("stand", player, state, [], [])
    assert player.posture == POSTURE_STANDING
    assert result.lines


def test_sleep_blocked_in_combat():
    state = make_state()
    player = make_player(locale="en", room_id="watson_flat", home_room_id="watson_flat")
    player.in_combat = True
    result = dispatch("sleep", player, state, [], [])
    assert player.posture == POSTURE_STANDING
    assert any("combat" in line.lower() for line in result.lines)


def test_sleep_at_home():
    state = make_state()
    player = make_player(locale="en", room_id="watson_flat", home_room_id="watson_flat")
    result = dispatch("sleep", player, state, [], [])
    assert player.posture == POSTURE_SLEEPING
    assert "posture" in result.meta


def test_sleep_refused_with_bleed():
    state = make_state()
    player = make_player(locale="en", room_id="watson_flat", home_room_id="watson_flat", content_rating="mature")
    player.player_status[EFFECT_BLEED] = 2
    result = dispatch("sleep", player, state, [], [])
    assert player.posture != POSTURE_SLEEPING


def test_rest_hp_regen_multiplier():
    load_life_config.cache_clear() if hasattr(load_life_config, "cache_clear") else None
    state = make_state()
    player = make_player(locale="en", hp=50, max_hp=100)
    player.posture = POSTURE_SITTING
    player.room_id = "watson_flat"
    player.home_room_id = "watson_flat"
    base = calc_hp_regen(player, "noon", state=None)
    boosted = calc_hp_regen(player, "noon", state=state)
    assert boosted >= base


def test_interact_bench_sits():
    state = make_state()
    player = make_player(locale="en", room_id="tutorial_canteen")
    result = dispatch("interact canteen_bench", player, state, [], [])
    assert player.posture == POSTURE_SITTING
    assert player.life_anchor


def test_go_wakes_player():
    state = make_state()
    player = make_player(locale="en", room_id="square")
    player.posture = POSTURE_SLEEPING
    dispatch("go west", player, state, [], [])
    assert player.posture == POSTURE_STANDING


def test_look_self_shows_life():
    state = make_state()
    player = make_player(locale="en", posture="sitting", fatigue=12)
    result = dispatch("look me", player, state, [], [])
    assert any("Fatigue" in line or "fatigue" in line.lower() for line in result.lines)


def test_help_includes_life_category():
    state = make_state()
    player = make_player(locale="en")
    result = dispatch("help", player, state, [], [])
    text = "\n".join(result.lines)
    assert "sit" in text
    assert "sleep" in text


def test_say_wakes_from_sleep():
    state = make_state()
    player = make_player(locale="en", room_id="square", posture=POSTURE_SLEEPING)
    result = dispatch("say hello", player, state, [], [])
    assert player.posture == POSTURE_STANDING
    assert len(result.lines) >= 2