from __future__ import annotations

from commands.registry import dispatch
from entities.npc import NPC
from tests.conftest import make_player, make_state
from world.clock import WorldClock
from world.schedule import npc_scheduled_room, shop_is_open
from world.tick import process_tick


def test_shop_is_open_during_hours():
    assert shop_is_open("ripperdoc", 12) is True
    assert shop_is_open("ripperdoc", 3) is False


def test_npc_scheduled_room_uses_period():
    npc = NPC(id="broker", schedule={"morning": "square", "afternoon": "alley"})
    assert npc_scheduled_room(npc, "afternoon", "square") == "alley"
    assert npc_scheduled_room(npc, "night", "square") == "square"


def test_go_blocks_closed_shop():
    player = make_player(room_id="square")
    state = make_state()
    state.clock = WorldClock(hour=3)
    result = dispatch("go west", player, state, [], [])
    assert player.room_id == "square"
    assert any("打烊" in line for line in result.lines)


def test_npc_schedule_moves_on_tick():
    state = make_state()
    state.clock = WorldClock(hour=14)
    state.npc_rooms["broker"] = "square"
    result = process_tick(state, state.time_config)
    assert state.npc_room("broker") == "alley"
    assert any(event.kind in {"npc_leave", "npc_enter"} for event in result.events)