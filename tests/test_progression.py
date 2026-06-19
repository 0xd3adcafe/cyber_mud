from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.loader import load_world
from world.progression import award_xp, xp_to_next_level


def test_award_xp_levels_up():
    player = make_player()
    lines = award_xp(player, xp_to_next_level(1), "zh")
    assert player.level == 2
    assert player.perk_points == 1
    assert player.attribute_points == 1
    assert any("升級" in line for line in lines)


def test_stats_command():
    player = make_player()
    state = make_state()
    player.level = 3
    player.xp = 40
    player.skills = ["quickhack"]
    result = dispatch("stats", player, state, [], [])
    text = "\n".join(result.lines)
    assert "等級" in text
    assert "快速破解" in text


def test_improve_body():
    player = make_player()
    state = make_state()
    player.attribute_points = 1
    before = player.body
    result = dispatch("improve body", player, state, [], [])
    assert player.body == before + 1
    assert player.attribute_points == 0
    assert any("肉體" in line for line in result.lines)


def test_talent_learn():
    player = make_player()
    state = make_state()
    player.level = 2
    player.perk_points = 1
    result = dispatch("talent iron_skin", player, state, [], [])
    assert "iron_skin" in player.perks
    assert player.perk_points == 0
    assert player.max_hp == 110
    assert any("強化皮层" in line for line in result.lines)


def test_learn_breach_requires_level():
    player = make_player(room_id="square")
    player.gold = 500
    state = make_state()
    result = dispatch("learn breach_protocol", player, state, [], [])
    assert "breach_protocol" not in player.skills
    assert any("等級" in line for line in result.lines)


def test_combat_victory_grants_xp():
    from combat.actions import _finish_victory
    from combat.encounter import start_encounter
    from world.progression import npc_xp_reward

    player = make_player(room_id="alley")
    state = make_state()
    encounter = start_encounter(state, player, "thug")
    assert encounter is not None
    npc = state.world.npc("thug")
    expected = npc_xp_reward(npc)
    assert expected > 0
    _finish_victory(state, player, encounter, [])
    assert player.xp == expected
    assert not player.in_combat


def test_world_loads_talents():
    world = load_world()
    assert "iron_skin" in world.talents
    assert world.skills["breach_protocol"].level_req == 3