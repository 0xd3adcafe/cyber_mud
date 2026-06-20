from __future__ import annotations

from unittest.mock import patch

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.districts import grid_flavor_line, is_grid_cell
from world.loader import load_world
from world.quest_author import validate_quests
from world.quests import accept_quest, advance_quest_on_visit, quest_is_done
from world.reactions import ambient_tick_line


def test_quest_author_no_warnings():
    world = load_world()
    warnings = [issue for issue in validate_quests(world) if issue.severity == "warn"]
    assert not warnings


def test_hub_npcs_present():
    world = load_world()
    for npc_id, room_id in (
        ("tyrell_liaison", "tyrell_plaza"),
        ("zone_warden", "combat_zone_gate"),
        ("plaza_handler", "corpo_plaza"),
        ("gate_herbalist", "little_china_gate"),
    ):
        npc = world.npc(npc_id)
        assert npc is not None, npc_id
        assert npc.room_id == room_id
        assert npc.talk_key == npc_id


def test_population_uses_archetype_talk_keys():
    world = load_world()
    npc = world.npc("watson_street_runner_0_0")
    assert npc is not None
    assert npc.talk_key == "street_runner"
    thug = world.npc("watson_thug_0_3")
    assert thug is not None
    assert thug.talk_key == "street_thug"


def test_grid_net_nodes_and_interactables():
    world = load_world()
    for node_id, room_id in (
        ("watson_grid_node", "watson_1_0"),
        ("tyrell_grid_node", "tyrell_0_0"),
        ("docks_grid_node", "docks_0_0"),
        ("undercity_grid_node", "undercity_1_0"),
    ):
        node = world.net_node(node_id)
        assert node is not None, node_id
        assert node.room_id == room_id
    for interactable_id, room_id in (
        ("tyrell_plaza_scanner", "tyrell_plaza"),
        ("zone_gate_memorial", "combat_zone_gate"),
        ("watson_grid_terminal", "watson_0_0"),
    ):
        obj = world.interactable(interactable_id)
        assert obj is not None, interactable_id
        assert obj.room_id == room_id


def test_grid_loot_recipes_and_shop_stock():
    world = load_world()
    assert world.recipe("street_stim") is not None
    assert world.recipe("gutter_blade") is not None
    assert world.disassemble_recipe("combat_scrap") is not None
    kabuki = world.shop("kabuki_bazaar")
    docks = world.shop("docks_gray")
    assert "neon_patch" in kabuki.sells
    assert "smuggler_pack" in docks.sells


def test_grid_flavor_on_procedural_cells():
    world = load_world()
    room = world.room("watson_0_0")
    assert room is not None
    assert is_grid_cell(room)
    assert grid_flavor_line(room, "en")
    hub = world.room("tyrell_plaza")
    assert hub is not None
    assert not is_grid_cell(hub)
    assert grid_flavor_line(hub, "en") is None


def test_look_includes_grid_flavor():
    player = make_player(room_id="watson_0_0", locale="en")
    state = make_state()
    result = dispatch("look", player, state, [], [])
    assert any("Rain-slick" in line or "fixers" in line for line in result.lines)


def test_district_spotlight_npcs():
    world = load_world()
    for npc_id in (
        "watson_spotter",
        "tyrell_courier",
        "zone_medic",
        "kabuki_spotter",
        "china_vendor",
        "corpo_analyst",
        "docks_runner",
        "undercity_whisper",
    ):
        npc = world.npc(npc_id)
        assert npc is not None, npc_id
        assert npc.talk_key == npc_id


def test_ambient_covers_all_districts():
    state = make_state()
    player = make_player(locale="en")
    with patch("world.reactions.random.random", return_value=0.0):
        for district, room_id in (
            ("tyrell", "tyrell_2_2"),
            ("little_china", "little_china_1_1"),
            ("undercity", "undercity_2_0"),
            ("combat_zone", "combat_zone_2_1"),
        ):
            player.room_id = room_id
            line = ambient_tick_line(player, state, "night", "en")
            assert line, district


def test_district_quests_validate():
    world = load_world()
    for qid in ("watson_pulse", "docks_courier", "kabuki_whisper", "zone_sweep"):
        assert world.quest(qid) is not None


def test_hub_briefing_quest_flow():
    player = make_player(room_id="combat_zone_gate", street_cred=5, locale="en")
    state = make_state()
    state.npc_rooms["zone_warden"] = "combat_zone_gate"
    state.npc_rooms["tyrell_liaison"] = "tyrell_plaza"
    state.npc_rooms["broker"] = "square"
    player.quest_flags["broker_rumor"] = "done"
    accept_quest(player, state, "hub_briefing", "en")
    dispatch("talk warden", player, state, [], [])
    player.room_id = "tyrell_plaza"
    advance_quest_on_visit(player, state, "tyrell_plaza", "en")
    dispatch("talk liaison", player, state, [], [])
    player.room_id = "square"
    state.npc_rooms["broker"] = "square"
    dispatch("talk broker", player, state, [], [])
    assert player.quest_flags["hub_briefing"] == "ready"
    dispatch("talk broker", player, state, [], [])
    assert quest_is_done(player, "hub_briefing")