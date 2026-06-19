from persistence.world_state import load_world_state, save_world_state
from world.clock import load_time_config
from world.loader import load_world
from world.weather import (
    default_weather,
    get_district_weather,
    load_weather_config,
    maybe_tick_weather,
    set_district_weather,
    weather_label,
)


def test_weather_config_loads():
    config = load_weather_config()
    assert "watson" in config.districts
    assert "tutorial" in config.districts
    assert "docks" in config.districts
    assert "acid_rain" in config.types
    assert "fog" in config.types
    assert "clear" in config.types
    assert "neon_haze" in config.types


def test_default_weather():
    config = load_weather_config()
    weather = default_weather(config)
    assert weather["watson"] == "neon_haze"
    assert weather["tutorial"] == "clear"
    assert weather["docks"] == "fog"


def test_get_set_district_weather():
    from tests.conftest import make_state

    state = make_state()
    set_district_weather(state, "watson", "acid_rain")
    assert get_district_weather(state, "watson") == "acid_rain"


def test_weather_label():
    config = load_weather_config()
    assert weather_label("acid_rain", "zh", config) == "酸雨"
    assert weather_label("acid_rain", "en", config) == "Acid Rain"


def test_maybe_tick_weather_on_interval():
    from tests.conftest import make_state

    state = make_state()
    config = load_weather_config()
    config.tick_every = 3

    state.tick_count = 2
    assert maybe_tick_weather(state, config) == []

    state.tick_count = 3
    changed = maybe_tick_weather(state, config)
    assert isinstance(changed, list)


def test_weather_persisted(world_state_path):
    world = load_world()
    config = load_time_config()
    state = load_world_state(world, config)
    state.weather["watson"] = "fog"
    save_world_state(state)
    loaded = load_world_state(world, config)
    assert loaded.weather["watson"] == "fog"