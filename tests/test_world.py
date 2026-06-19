from world.loader import load_world


def test_world_loads():
    world = load_world()
    assert world.start_room == "square"
    assert "square" in world.rooms
    assert world.rooms["square"].exits["north"] == "alley"


def test_factions_present():
    world = load_world()
    assert "arasaka" in world.factions