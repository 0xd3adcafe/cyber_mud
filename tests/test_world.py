from world.loader import load_world


def test_world_loads():
    world = load_world()
    assert world.start_room == "square"
    assert "square" in world.rooms
    assert world.rooms["square"].exits["north"] == "alley"


def test_factions_present():
    world = load_world()
    assert "arasaka" in world.factions
    assert "dedsec" in world.factions


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


def test_content_data_loaded():
    world = load_world()
    assert "quickhack" in world.skills
    assert "smart_link" in world.mods
    assert world.mods["smart_link"].weapon_damage == 2
    assert "broker_rumor" in world.quests
    assert "square_market" in world.shops
    assert world.shops["square_market"].open_hour == 8
    assert "glowstick" in world.shops["square_market"].sells
    assert world.shops["ripperdoc"].room_id == "ripper_clinic"
    assert world.shops["tutorial_supply"].npc_id == "quartermaster"
    assert "terminal" in world.net_nodes
    assert world.net_nodes["terminal"].room_id == "square"


def test_npc_quest_fields():
    world = load_world()
    broker = world.npc("broker")
    assert broker is not None
    assert broker.talk_key == "broker"
    assert broker.quest_id == "broker_rumor"
    thug = world.npc("thug")
    assert thug is not None
    assert thug.aggro == 8
    assert thug.quest_id == "broker_rumor"