from combat.encounter import Encounter
from commands.registry import dispatch
from tests.conftest import make_player, make_state


def _ctx():
    player = make_player(room_id="square")
    state = make_state()
    return player, state


def test_mod_smart_link_on_knife():
    player, state = _ctx()
    dispatch("take knife", player, state, [], [])
    dispatch("take mod_chip", player, state, [], [])
    dispatch("equip knife", player, state, [], [])
    result = dispatch("mod mod_chip", player, state, [], [])
    assert "mod_chip" not in player.inventory
    assert "smart_link" in player.weapon_mods.get("knife", [])
    assert any("智慧連結" in line for line in result.lines)
    assert result.refresh_sidebar

    encounter = Encounter(id="x", player_name=player.name, npc_id="thug", npc_hp=30)
    assert encounter.player_weapon_damage(player, state.world) == 7


def test_mod_requires_weapon():
    player, state = _ctx()
    dispatch("take mod_chip", player, state, [], [])
    result = dispatch("mod mod_chip", player, state, [], [])
    assert "mod_chip" in player.inventory
    assert any("武器" in line for line in result.lines)