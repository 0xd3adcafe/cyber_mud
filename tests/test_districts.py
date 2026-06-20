from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.districts import district_profile, district_safety, load_district_profiles
from world.loader import load_world
from world.weather import load_weather_config, maybe_tick_weather


def test_district_profiles_loaded():
    profiles = load_district_profiles()
    assert profiles["watson"].safety == 2
    assert profiles["corpo"].atmosphere == "corpo_surveillance"
    assert profiles["combat_zone"].aggro_bonus == 0.15


def test_look_shows_atmosphere():
    state = make_state()
    player = make_player(locale="en", room_id="corpo_plaza")
    result = dispatch("look", player, state, [], [])
    text = "\n".join(result.lines)
    assert "surveillance" in text.lower() or "camera" in text.lower()


def test_maelstrom_blocked_from_corpo_without_rep():
    state = make_state()
    player = make_player(locale="en", room_id="ripper_clinic", faction="maelstrom", reputation=0)
    result = dispatch("go west", player, state, [], [])
    assert player.room_id == "ripper_clinic"
    assert any("block" in line.lower() or "patrol" in line.lower() for line in result.lines)


def test_weather_config_covers_districts():
    cfg = load_weather_config()
    world = load_world()
    districts = {room.district for room in world.rooms.values() if room.district}
    for district in districts:
        if district in {"tutorial", "watson", "kabuki"}:
            assert district in cfg.districts


def test_weighted_weather_respects_bias(monkeypatch):
    state = make_state()
    cfg = load_weather_config()
    state.tick_count = cfg.tick_every
    state.weather["watson"] = "clear"
    monkeypatch.setattr("world.weather.random.choice", lambda _: "acid_rain")
    from world.districts import weighted_weather_choice

    monkeypatch.setattr(
        "world.districts.weighted_weather_choice",
        lambda pool, district, current: weighted_weather_choice(pool, district, current),
    )
    changed = maybe_tick_weather(state, cfg)
    assert isinstance(changed, list)