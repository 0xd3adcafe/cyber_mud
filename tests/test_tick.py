from persistence.world_state import load_world_state, save_world_state
from world.clock import load_time_config
from world.loader import load_world
from world.tick import process_tick


def test_process_tick_advances_clock(world_state_path):
    world = load_world()
    config = load_time_config()
    state = load_world_state(world, config)
    before = state.clock.minute
    result = process_tick(state, config)
    assert result.time_changed is True
    assert state.clock.minute == before + config.minutes_per_tick
    assert state.tick_count == 1


def test_world_state_roundtrip(world_state_path):
    world = load_world()
    config = load_time_config()
    state = load_world_state(world, config)
    state.clock.advance(25)
    state.npc_rooms["broker"] = "alley"
    state.weather["watson"] = "acid_rain"
    state.tick_count = 42
    save_world_state(state)
    loaded = load_world_state(world, config)
    assert loaded.clock.day == state.clock.day
    assert loaded.clock.hour == state.clock.hour
    assert loaded.clock.minute == state.clock.minute
    assert loaded.room_items == state.room_items
    assert loaded.npc_rooms == state.npc_rooms
    assert loaded.weather == state.weather
    assert loaded.tick_count == state.tick_count