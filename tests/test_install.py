from commands.registry import dispatch
from tests.conftest import make_player, make_state


def _ctx():
    player = make_player()
    state = make_state()
    return player, state


def test_install_cyber_arm():
    player, state = _ctx()
    dispatch("take cyber_arm_kit", player, state, [], [])
    assert player.body == 3
    assert player.humanity == 100
    result = dispatch("install cyber_arm_kit", player, state, [], [])
    assert "cyber_arm_v1" in player.implants
    assert "cyber_arm_kit" not in player.inventory
    assert player.body == 4
    assert player.humanity == 95
    assert any("安裝" in line for line in result.lines)
    assert result.refresh_sidebar


def test_install_already_installed():
    player, state = _ctx()
    dispatch("take cyber_arm_kit", player, state, [], [])
    dispatch("install cyber_arm_kit", player, state, [], [])
    player.inventory.append("cyber_arm_kit")
    result = dispatch("install cyber_arm_kit", player, state, [], [])
    assert any("已經" in line for line in result.lines)