from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.loader import default_room_items, load_world

TUTORIAL_ROOMS = {
    "tutorial",
    "tutorial_briefing",
    "tutorial_combat",
    "tutorial_course",
    "tutorial_net",
    "tutorial_medbay",
    "tutorial_armory",
    "tutorial_canteen",
    "tutorial_range",
}

TUTORIAL_NPCS = {
    "instructor",
    "sparring_bot",
    "netcoach",
    "quartermaster",
    "rookie_fixer",
    "canteen_tech",
    "range_officer",
    "clinic_tutor",
    "course_guide",
    "patrol_dummy",
}


def test_tutorial_zone_rooms_connected():
    world = load_world()
    hub = world.rooms["tutorial"]
    assert hub.exits["up"] == "tutorial_briefing"
    assert hub.exits["north"] == "tutorial_combat"
    assert hub.exits["east"] == "tutorial_net"
    assert hub.exits["south"] == "tutorial_armory"
    assert world.rooms["tutorial_briefing"].exits["down"] == "tutorial"
    assert world.rooms["tutorial_combat"].exits["north"] == "tutorial_range"
    assert world.rooms["tutorial_combat"].exits["east"] == "tutorial_course"
    assert world.rooms["tutorial_course"].exits["west"] == "tutorial_combat"
    assert world.rooms["tutorial_net"].exits["north"] == "tutorial_medbay"
    assert world.rooms["tutorial_medbay"].exits["south"] == "tutorial_net"
    assert world.rooms["tutorial_armory"].exits["west"] == "tutorial_canteen"
    assert world.rooms["tutorial_canteen"].exits["east"] == "tutorial_armory"
    assert world.rooms["tutorial_range"].exits["south"] == "tutorial_combat"


def test_tutorial_district_has_nine_rooms():
    world = load_world()
    tutorial_rooms = [rid for rid, room in world.rooms.items() if room.district == "tutorial"]
    assert set(tutorial_rooms) == TUTORIAL_ROOMS


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


def test_tutorial_new_areas_have_items():
    items = default_room_items()
    assert "trainee_ration" in items["tutorial_canteen"]
    assert "trainee_flask" in items["tutorial_canteen"]
    assert "training_smartgun" in items["tutorial_range"]
    assert "field_manual" in items["tutorial_briefing"]
    assert "trauma_kit" in items["tutorial_medbay"]


def test_tutorial_npcs_present():
    world = load_world()
    for npc_id in TUTORIAL_NPCS:
        assert world.npc(npc_id) is not None
    assert world.npc("instructor").room_id == "tutorial"
    assert world.npc("rookie_fixer").room_id == "tutorial_briefing"
    assert world.npc("canteen_tech").room_id == "tutorial_canteen"
    assert world.npc("range_officer").room_id == "tutorial_range"
    assert world.npc("clinic_tutor").room_id == "tutorial_medbay"
    assert world.npc("course_guide").room_id == "tutorial_course"
    assert world.npc("patrol_dummy").room_id == "tutorial_course"
    assert world.net_nodes["tutorial_terminal"].room_id == "tutorial_net"


def test_tutorial_interactables_present():
    world = load_world()
    assert world.interactable("tutorial_holo_board") is not None
    assert world.interactable("tutorial_locker") is not None
    assert world.interactable("tutorial_scan_post") is not None
    assert world.interactable("tutorial_med_console") is not None


def test_go_through_tutorial_hub():
    player = make_player(room_id="tutorial")
    state = make_state()

    result = dispatch("go south", player, state, [], [])

    assert player.room_id == "tutorial_armory"
    assert result.moved
    assert any("裝備庫" in line or "Armory" in line for line in result.lines)


def test_go_tutorial_expansion_paths():
    player = make_player(room_id="tutorial")
    state = make_state()

    dispatch("go up", player, state, [], [])
    assert player.room_id == "tutorial_briefing"

    dispatch("go down", player, state, [], [])
    dispatch("go north", player, state, [], [])
    dispatch("go east", player, state, [], [])
    assert player.room_id == "tutorial_course"

    dispatch("go west", player, state, [], [])
    dispatch("go south", player, state, [], [])
    dispatch("go south", player, state, [], [])
    dispatch("go west", player, state, [], [])
    assert player.room_id == "tutorial_canteen"


def test_tutorial_locker_gives_ration_once():
    player = make_player(room_id="tutorial_canteen")
    state = make_state()
    result = dispatch("interact tutorial_locker", player, state, [], [])
    assert "trainee_ration" in player.inventory
    assert player.interact_flags.get("tutorial_locker") == "done"
    assert any("口糧" in line or "ration" in line.lower() for line in result.lines)

    again = dispatch("interact tutorial_locker", player, state, [], [])
    assert player.inventory.count("trainee_ration") == 1
    assert any("已" in line or "already" in line.lower() for line in again.lines)


def test_talk_rookie_fixer():
    player = make_player(room_id="tutorial_briefing")
    state = make_state()
    result = dispatch("talk rookie_fixer", player, state, [], [])
    assert any("gigs" in line for line in result.lines)