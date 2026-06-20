from __future__ import annotations

from pathlib import Path

from world.loader import POPULATION_PATH, load_world


def test_world_scale_milestone():
    world = load_world()
    assert len(world.rooms) >= 200
    assert len(world.items) >= 45
    assert len(world.npcs) >= 109


def test_world_population_overlay_present():
    assert POPULATION_PATH.exists()
    world = load_world()
    assert "watson_street_runner_0_0" in world.npcs
    assert "gutter_blade" in world.items


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


def test_expand_population_tool_targets():
    from tools.expand_world_population import build_population
    import yaml

    raw = yaml.safe_load(Path("data/world.yaml").read_text(encoding="utf-8"))
    payload = build_population(raw)
    assert len(payload["npcs"]) == 86
    assert len(payload["items"]) == 13