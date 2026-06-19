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
    assert player.equipment.get("weapon_secondary") == "knife"
    assert "knife" not in player.inventory
    assert any("戰術折刀" in line for line in result.lines)
    assert result.refresh_sidebar


def test_unequip_knife():
    player, state = _ctx()
    dispatch("take knife", player, state, [], [])
    dispatch("equip knife", player, state, [], [])
    result = dispatch("unequip knife", player, state, [], [])
    assert "weapon_secondary" not in player.equipment
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


def test_cp2077_body_slots():
    player = make_player(room_id="tutorial_armory")
    state = make_state()
    for item_id in ("trainee_undersuit", "trainee_vest", "trainee_pants", "trainee_boots"):
        dispatch(f"take {item_id}", player, state, [], [])
        dispatch(f"equip {item_id}", player, state, [], [])
    assert player.equipment.get("inner_torso") == "trainee_undersuit"
    assert player.equipment.get("outer_torso") == "trainee_vest"
    assert player.equipment.get("legs") == "trainee_pants"
    assert player.equipment.get("feet") == "trainee_boots"


def test_handgun_weapon_type():
    from world.loader import load_world

    world = load_world()
    pistol = world.item("liberty_pistol")
    assert pistol.weapon_type == "handgun"
    assert pistol.weapon_class == "power"
    assert pistol.weapon_mode == "secondary"


def test_dual_wield_loadout():
    player = make_player(room_id="square")
    state = make_state()
    dispatch("take knife", player, state, [], [])
    dispatch("take liberty_pistol", player, state, [], [])
    dispatch("equip liberty_pistol", player, state, [], [])
    dispatch("equip knife", player, state, [], [])
    assert player.equipment.get("weapon_secondary") == "liberty_pistol"
    assert player.equipment.get("weapon_primary") == "knife"
    result = dispatch("equipment", player, state, [], [])
    assert any("雙持" in line for line in result.lines)


def test_two_handed_clears_secondary():
    player = make_player(room_id="tutorial_range")
    state = make_state()
    dispatch("take training_sidearm", player, state, [], [])
    dispatch("take training_carbine", player, state, [], [])
    dispatch("equip training_sidearm", player, state, [], [])
    dispatch("equip training_carbine", player, state, [], [])
    assert player.equipment.get("weapon_primary") == "training_carbine"
    assert "weapon_secondary" not in player.equipment
    assert "training_sidearm" in player.inventory
    result = dispatch("equipment", player, state, [], [])
    assert any("雙手" in line for line in result.lines)