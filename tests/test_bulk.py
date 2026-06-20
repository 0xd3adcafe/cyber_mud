from commands.bulk_helpers import is_bulk, resolve_equip_targets, resolve_take_targets
from commands.registry import CommandContext, dispatch
from tests.conftest import make_player, make_state


def _ctx():
    player = make_player()
    state = make_state()
    return player, state


def test_is_bulk_markers():
    assert is_bulk("all")
    assert is_bulk("全部")
    assert is_bulk("*")
    assert not is_bulk("knife")


def test_take_all():
    player, state = _ctx()
    result = dispatch("take all", player, state, [], [])
    assert len(player.inventory) >= 3
    assert not state.room_items.get("square")
    assert any("撿起" in line for line in result.lines)


def test_drop_all():
    player, state = _ctx()
    dispatch("take all", player, state, [], [])
    result = dispatch("drop 全部", player, state, [], [])
    assert not player.inventory
    assert len(state.room_items["square"]) >= 3
    assert result.refresh_sidebar


def test_equip_all():
    player, state = _ctx()
    dispatch("take knife", player, state, [], [])
    dispatch("take jacket", player, state, [], [])
    result = dispatch("equip *", player, state, [], [])
    assert player.equipment.get("weapon_secondary") == "knife"
    assert player.equipment.get("outer_torso") == "jacket"
    assert any("裝備" in line for line in result.lines)


def test_resolve_take_targets_bulk():
    player, state = _ctx()
    ctx = CommandContext(player, state, "all")
    result = resolve_take_targets(ctx, "all")
    assert result.ok
    assert "knife" in result.value
    assert "jacket" in result.value