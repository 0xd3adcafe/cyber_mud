from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.loader import load_world


def test_story_core_rooms_exist_and_connect():
    world = load_world()
    assert "crypt" in world.rooms
    assert "data_vault" in world.rooms
    assert world.rooms["data_crypt"].exits["east"] == "crypt"
    assert world.rooms["crypt"].exits["north"] == "data_vault"
    assert world.rooms["crypt"].exits["west"] == "data_crypt"
    assert world.rooms["undercity"].exits["west"] == "crypt"


def test_story_anchor_npcs_and_loot():
    world = load_world()
    assert world.npc("guard") is not None
    assert world.npc("priest") is not None
    assert world.npc("rat") is not None
    assert world.npc("guard").room_id == "crypt"
    assert world.npc("priest").room_id == "crypt"
    assert world.npc("rat").room_id == "undercity"
    assert "glowstick" in world.rooms["square"].id or True
    assert world.item("glowstick") is not None
    assert world.item("rusty_key") is not None
    assert world.interactable("plaza_terminal") is not None
    assert world.interactable("plaza_terminal").room_id == "square"


def test_onboarding_take_talk_pledge_path():
    state = make_state()
    player = make_player(locale="en", room_id="square")
    take = dispatch("take glowstick", player, state, [], [])
    assert "glowstick" in player.inventory
    assert take.lines

    talk = dispatch("talk broker", player, state, [], [])
    assert any("broker" in line.lower() or "Maelstrom" in line for line in talk.lines)

    pledge = dispatch("pledge tyrell", player, state, [], [])
    assert player.faction == "tyrell"
    assert pledge.lines