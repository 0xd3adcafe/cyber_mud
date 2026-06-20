from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.loader import load_world
from world.proficiencies import (
    PROFICIENCY_MAX,
    award_proficiency_xp,
    proficiency_damage_bonus,
    proficiency_for_strike,
    proficiency_for_weapon_type,
    xp_to_next_proficiency,
)


def test_proficiency_levels_through_use():
    player = make_player(locale="en")
    world = load_world()
    need = xp_to_next_proficiency(0)
    lines = award_proficiency_xp(player, "handguns", need, "en", proficiencies=world.proficiencies)
    assert player.proficiency_levels["handguns"] == 1
    assert lines and "Handguns" in lines[0]


def test_weapon_type_mapping():
    assert proficiency_for_weapon_type("handgun") == "handguns"
    assert proficiency_for_weapon_type("assault_rifle") == "assault"
    assert proficiency_for_weapon_type("shotgun") == "annihilation"
    assert proficiency_for_weapon_type("katana") == "blades"


def test_strike_mapping_unarmed():
    player = make_player(locale="en")
    state = make_state()
    assert proficiency_for_strike(player, state.world, style_id="punch") == "street_brawler"
    assert proficiency_for_strike(player, state.world, style_id="backstab") == "stealth"


def test_proficiency_damage_bonus_scales():
    player = make_player(locale="en")
    player.proficiency_levels["blades"] = 25
    assert proficiency_damage_bonus(player, "blades") == 5


def test_proficiency_caps_at_max():
    player = make_player(locale="en")
    world = load_world()
    player.proficiency_levels["crafting"] = PROFICIENCY_MAX
    lines = award_proficiency_xp(player, "crafting", 100, "en", proficiencies=world.proficiencies)
    assert not lines
    assert player.proficiency_levels["crafting"] == PROFICIENCY_MAX


def test_stats_shows_proficiencies():
    player = make_player(locale="en")
    state = make_state()
    player.proficiency_levels["athletics"] = 3
    result = dispatch("stats", player, state, [], [])
    text = "\n".join(result.lines)
    assert "Proficiencies" in text or "熟練度" in text
    assert "Athletics" in text or "運動" in text


def test_go_grants_athletics_xp():
    player = make_player(room_id="square", locale="en")
    state = make_state()
    room = state.world.room("square")
    assert room is not None
    direction = next(iter(room.exits))
    before = player.proficiency_xp.get("athletics", 0)
    dispatch(f"go {direction}", player, state, [], [])
    assert player.proficiency_xp.get("athletics", 0) >= before + 4