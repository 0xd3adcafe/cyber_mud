from __future__ import annotations

from unittest.mock import patch

from commands.registry import dispatch
from shared.repeat import REPEAT_INTERVAL_SECONDS, parse_repeat
from tests.conftest import make_player, make_state


def test_parse_repeat_prefix():
    assert parse_repeat("10 punch thug") == (10, "punch thug")
    assert parse_repeat("punch thug") == (1, "punch thug")


def test_parse_repeat_dot_suffix():
    assert parse_repeat("punch.10 thug") == (10, "punch thug")
    assert parse_repeat("go.3 north") == (3, "go north")


def test_parse_repeat_caps_at_max():
    assert parse_repeat("500 punch")[0] == 99


def test_repeat_go_moves_multiple_times():
    player = make_player(room_id="square")
    state = make_state()

    with patch("commands.registry.time.sleep") as sleep:
        result = dispatch("3 go north", player, state, [], [])

    assert player.room_id == "alley"
    assert any("重複" in line for line in result.lines)
    assert sleep.call_count == 1
    sleep.assert_called_with(REPEAT_INTERVAL_SECONDS)


def test_repeat_waits_between_each_execution():
    player = make_player(room_id="square")
    state = make_state()

    with patch("commands.registry.time.sleep") as sleep:
        dispatch("4 say hi", player, state, [], [])

    assert sleep.call_count == 3
    sleep.assert_called_with(REPEAT_INTERVAL_SECONDS)


def test_repeat_blocked_command_runs_once():
    player = make_player()
    state = make_state()

    result = dispatch("3 help", player, state, [], [])

    assert not any("重複" in line for line in result.lines)
    assert any("help" in line.lower() or "指令" in line for line in result.lines)


def test_repeat_stops_when_combat_ends():
    player = make_player(room_id="alley", name="Vy")
    player.body = 50
    player.equipment["weapon_secondary"] = "knife"
    state = make_state()

    with patch("commands.registry.time.sleep"):
        result = dispatch("punch.20 thug", player, state, [], [])

    assert not player.in_combat
    assert any("重複結束" in line or "重複完成" in line for line in result.lines)


def test_single_command_does_not_sleep():
    player = make_player(room_id="square")
    state = make_state()

    with patch("commands.registry.time.sleep") as sleep:
        dispatch("go north", player, state, [], [])

    sleep.assert_not_called()