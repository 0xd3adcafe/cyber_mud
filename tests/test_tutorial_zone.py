from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.loader import default_room_items, load_world


def test_tutorial_zone_rooms_connected():
    world = load_world()
    hub = world.rooms["tutorial"]
    assert hub.exits["north"] == "tutorial_combat"
    assert hub.exits["east"] == "tutorial_net"
    assert hub.exits["south"] == "tutorial_armory"
    assert world.rooms["tutorial_combat"].exits["north"] == "tutorial_range"
    assert world.rooms["tutorial_range"].exits["south"] == "tutorial_combat"


def test_tutorial_armory_has_training_gear():
    items = default_room_items()["tutorial_armory"]
    assert "trainee_blade" in items
    assert "training_sidearm" in items
    assert "trainee_vest" in items
    assert "trainee_undersuit" in items
    assert "trainee_pants" in items
    assert "trainee_boots" in items
    assert "trainee_helmet" in items
    assert "practice_cyber_kit" in items


def test_tutorial_npcs_present():
    world = load_world()
    assert world.npc("instructor") is not None
    assert world.npc("sparring_bot") is not None
    assert world.npc("netcoach") is not None
    assert world.npc("quartermaster") is not None
    assert world.net_nodes["tutorial_terminal"].room_id == "tutorial_net"


def test_go_through_tutorial_hub():
    player = make_player(room_id="tutorial")
    state = make_state()

    result = dispatch("go south", player, state, [], [])

    assert player.room_id == "tutorial_armory"
    assert result.moved
    assert any("裝備庫" in line or "Armory" in line for line in result.lines)