from __future__ import annotations

from world.loader import load_world


def test_world_scale_milestone():
    world = load_world()
    assert len(world.rooms) >= 200
    assert len(world.items) >= 30
    assert len(world.npcs) >= 19


def test_procedural_rooms_have_district_and_grid():
    world = load_world()
    for rid in ("watson_3_2", "tyrell_3_5", "combat_zone_3_0", "kabuki_2_3"):
        room = world.rooms[rid]
        assert room.district
        assert room.grid_x >= 0
        assert room.grid_y >= 0


def test_hub_grid_links():
    world = load_world()
    assert world.rooms["ripper_clinic"].exits["north"] == "watson_3_2"
    assert world.rooms["watson_3_2"].exits["south"] == "ripper_clinic"
    assert world.rooms["corpo_plaza"].exits["east"] == "tyrell_plaza"
    assert world.rooms["tyrell_plaza"].exits["south"] == "tyrell_3_5"
    assert world.rooms["docks"].exits["east"] == "combat_zone_gate"
    assert world.rooms["combat_zone_gate"].exits["south"] == "combat_zone_3_0"