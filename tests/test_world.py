from world.loader import load_world


def test_world_loads():
    world = load_world()
    assert world.start_room == "square"
    assert "square" in world.rooms
    assert world.rooms["square"].exits["north"] == "alley"


def test_factions_present():
    world = load_world()
    assert "arasaka" in world.factions


def test_items_and_implants():
    world = load_world()
    knife = world.item("knife")
    assert knife is not None
    assert knife.weapon_damage == 5
    assert knife.value == 80
    jacket = world.item("jacket")
    assert jacket.defense == 2
    kit = world.item("cyber_arm_kit")
    assert kit.implant_id == "cyber_arm_v1"
    implant = world.implant("cyber_arm_v1")
    assert implant is not None
    assert implant.body == 1
    assert implant.humanity_cost == 5