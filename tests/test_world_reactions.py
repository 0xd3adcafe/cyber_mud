from __future__ import annotations

from unittest.mock import patch

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.reactions import (
    ambient_tick_line,
    broker_talk_extra,
    reputation_from_pledge,
    shift_reputation,
)
from world.tick import process_tick


def test_shift_reputation_clamps_and_reports():
    player = make_player(locale="en", reputation=0)
    lines = shift_reputation(player, 5, "en")
    assert player.reputation == 5
    assert lines and "5" in lines[0]


def test_pledge_adds_reputation():
    player = make_player(locale="en")
    state = make_state()
    result = dispatch("pledge tyrell", player, state, [], [])
    assert player.faction == "tyrell"
    assert player.reputation == reputation_from_pledge("tyrell")
    assert any("rep" in line.lower() or "聲望" in line for line in result.lines)


def test_broker_talk_high_rep():
    player = make_player(locale="en", reputation=25)
    extra = broker_talk_extra(player, "broker", "en")
    assert extra and "doors" in extra.lower()


def test_ambient_tick_can_emit_district_line():
    player = make_player(room_id="docks", locale="en")
    state = make_state()
    with patch("world.reactions.random.random", return_value=0.0):
        line = ambient_tick_line(player, state, "night", "en")
    assert line and "crane" in line.lower()


def test_tick_emits_ambient_event():
    player = make_player(room_id="square", locale="en", named=True)
    state = make_state()
    with patch("world.reactions.random.random", return_value=0.0):
        result = process_tick(state, state.time_config, players=[player])
    assert any(event.kind == "ambient_tick" for event in result.events)