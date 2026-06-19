from commands.registry import dispatch
from tests.conftest import make_player, make_state


def _ctx():
    player = make_player()
    state = make_state()
    return player, state


def test_equip_knife():
    player, state = _ctx()
    dispatch("take knife", player, state, [], [])
    result = dispatch("equip knife", player, state, [], [])
    assert player.equipment.get("weapon") == "knife"
    assert "knife" not in player.inventory
    assert any("戰術折刀" in line for line in result.lines)
    assert result.refresh_sidebar


def test_unequip_knife():
    player, state = _ctx()
    dispatch("take knife", player, state, [], [])
    dispatch("equip knife", player, state, [], [])
    result = dispatch("unequip knife", player, state, [], [])
    assert "weapon" not in player.equipment
    assert "knife" in player.inventory
    assert any("卸下" in line for line in result.lines)


def test_equipment_panel():
    player, state = _ctx()
    dispatch("take knife", player, state, [], [])
    dispatch("equip knife", player, state, [], [])
    result = dispatch("equipment", player, state, [], [])
    assert result.panel == "equipment"
    assert result.ui_json
    assert any("裝備" in line for line in result.lines)


def test_eq_alias():
    player, state = _ctx()
    result = dispatch("eq", player, state, [], [])
    assert result.panel == "equipment"