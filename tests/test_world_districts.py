from __future__ import annotations

from world.loader import load_world


def test_kabuki_little_china_corpo_rooms():
    world = load_world()
    assert "kabuki_bazaar" in world.rooms
    assert "kabuki_vip" in world.rooms
    assert "little_china_gate" in world.rooms
    assert "shrine" in world.rooms
    assert "data_crypt" in world.rooms
    assert "corpo_lobby" in world.rooms
    assert "corpo_plaza" in world.rooms

    assert world.rooms["kabuki_bazaar"].district == "kabuki"
    assert world.rooms["little_china_gate"].district == "little_china"
    assert world.rooms["corpo_plaza"].district == "corpo"


def test_district_connectivity():
    world = load_world()
    assert world.rooms["alley"].exits["west"] == "kabuki_lounge"
    assert world.rooms["alley"].exits["east"] == "little_china_gate"
    assert world.rooms["kabuki_lounge"].exits["north"] == "kabuki_vip"
    assert world.rooms["shrine"].exits["down"] == "data_crypt"
    assert world.rooms["data_crypt"].exits["north"] == "undercity"
    assert world.rooms["ripper_clinic"].exits["west"] == "corpo_lobby"


def test_new_npcs_and_shop():
    world = load_world()
    assert world.npc("bazaar_fixer") is not None
    assert world.npc("shrine_keeper") is not None
    assert world.npc("corp_guard") is not None
    assert world.npc("kabuki_dancer") is not None
    assert "kabuki_bazaar" in world.shops
    assert world.item("lantern") is not None
    assert "crypt_core" in world.net_nodes