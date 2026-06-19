from persistence.world_state import load_world_state, save_world_state
from world.clock import load_time_config
from world.loader import load_world
from world.tick import process_tick


def test_process_tick_advances_clock(world_state_path):
    world = load_world()
    config = load_time_config()
    state = load_world_state(world, config)
    before = state.clock.minute
    assert process_tick(state, config) is True
    assert state.clock.minute == before + config.minutes_per_tick


def test_world_state_roundtrip(world_state_path):
    world = load_world()
    config = load_time_config()
    state = load_world_state(world, config)
    state.clock.advance(25)
    save_world_state(state)
    loaded = load_world_state(world, config)
    assert loaded.clock.day == state.clock.day
    assert loaded.clock.hour == state.clock.hour
    assert loaded.clock.minute == state.clock.minute
    assert loaded.room_items == state.room_items