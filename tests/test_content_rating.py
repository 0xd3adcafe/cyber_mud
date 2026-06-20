from __future__ import annotations

from commands.registry import dispatch
from persistence.save import load_player, save_player
from tests.conftest import make_player, make_state
from world.mature import is_mature, set_content_rating


def test_player_defaults_teen():
    player = make_player(locale="en")
    assert player.content_rating == "teen"
    assert not is_mature(player)


def test_settings_mature_on_off():
    state = make_state()
    player = make_player(locale="en", room_id="square")
    result = dispatch("settings mature on", player, state, [], [player])
    assert any("enabled" in line.lower() or "mature" in line.lower() for line in result.lines)
    assert is_mature(player)

    result = dispatch("settings mature off", player, state, [], [player])
    assert not is_mature(player)


def test_mature_command_refused_for_teen():
    state = make_state()
    player = make_player(locale="en", room_id="square")
    result = dispatch("flirt kabuki_host", player, state, [], [player])
    assert any("18+" in line or "mature" in line.lower() for line in result.lines)


def test_mature_room_blocked(save_dir):
    state = make_state()
    player = make_player(locale="en", room_id="alley")
    result = dispatch("go west", player, state, [], [player])
    assert player.room_id == "alley"
    assert any("18+" in line or "mature" in line.lower() for line in result.lines)


def test_register_with_mature_flag(save_dir):
    state = make_state()
    player = make_player(locale="en", named=False, name="Guest")
    result = dispatch("register GoreTest s3cret mature", player, state, [], [player])
    assert player.named
    assert is_mature(player)
    loaded = load_player("GoreTest")
    assert loaded is not None
    assert loaded.content_rating == "mature"


def test_content_rating_persists(save_dir):
    player = make_player(locale="en", name="Persist", content_rating="mature")
    save_player(player)
    loaded = load_player("Persist")
    assert loaded is not None
    assert loaded.content_rating == "mature"