from unittest.mock import patch

from commands.registry import dispatch
from persistence.world_state import default_npc_rooms
from tests.conftest import make_player, make_state
from world.loader import load_world
from world.tick import IDLE_EVERY, PATROL_EVERY, process_tick


def test_default_npc_rooms():
    world = load_world()
    rooms = default_npc_rooms(world)
    assert rooms["broker"] == "square"
    assert rooms["thug"] == "alley"


def test_npcs_in_room_uses_dynamic_positions():
    state = make_state()
    assert "broker" in state.npcs_in_room("square")
    state.npc_rooms["broker"] = "alley"
    assert "broker" not in state.npcs_in_room("square")
    assert "broker" in state.npcs_in_room("alley")


def test_look_uses_npc_rooms_not_static_room_id():
    player = make_player(room_id="square")
    state = make_state()
    state.npc_rooms["broker"] = "alley"
    result = dispatch("look", player, state, [], [])
    text = "\n".join(result.lines)
    assert "情報經紀人" not in text

    player.room_id = "alley"
    result = dispatch("look", player, state, [], [])
    text = "\n".join(result.lines)
    assert "情報經紀人" in text


def test_patrol_movement_on_tick():
    state = make_state()
    broker = state.world.npc("broker")
    assert broker is not None
    saved_schedule = dict(broker.schedule)
    broker.schedule.clear()
    try:
        state.tick_count = PATROL_EVERY - 1
        with patch("world.tick.random.random", return_value=0.1):
            result = process_tick(state, state.time_config)
        assert state.npc_rooms["broker"] == "alley"
        kinds = [e.kind for e in result.events]
        assert "npc_leave" in kinds
        assert "npc_enter" in kinds
    finally:
        broker.schedule.clear()
        broker.schedule.update(saved_schedule)


def test_idle_message_on_tick():
    state = make_state()
    state.tick_count = IDLE_EVERY - 1
    with patch("world.tick.random.random", return_value=0.1):
        result = process_tick(state, state.time_config)
    idle_events = [e for e in result.events if e.kind == "npc_idle"]
    assert idle_events
    assert idle_events[0].idle_msg_zh


def test_broker_npc_fields():
    world = load_world()
    broker = world.npc("broker")
    assert broker is not None
    assert broker.hp == 50
    assert broker.hostile is False
    assert broker.patrol == ["square", "alley"]


def test_thug_npc_fields():
    world = load_world()
    thug = world.npc("thug")
    assert thug is not None
    assert thug.hp == 30
    assert thug.hostile is True