from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.help_tutorial import format_help_tutorial, tutorial_room_ids
from world.loader import load_world


def test_tutorial_room_ids():
    world = load_world()
    ids = tutorial_room_ids(world)
    assert "tutorial" in ids
    assert "tutorial_combat" in ids
    assert "tutorial_canteen" in ids


def test_help_tutorial_command():
    player = make_player(locale="en")
    state = make_state()
    result = dispatch("help tutorial", player, state, [], [])
    text = "\n".join(result.lines)
    assert "Training" in text or "tutorial" in text.lower()
    assert "look" in text
    assert "tutorial_combat" in text or "Combat" in text


def test_help_tutorial_zh():
    ctx = type("Ctx", (), {"player": make_player(locale="zh"), "state": make_state(), "args": ""})()
    lines = format_help_tutorial(ctx)
    text = "\n".join(lines)
    assert "訓練" in text
    assert "look" in text