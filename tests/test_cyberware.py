from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_install_to_slot():
    player = make_player(room_id="square")
    state = make_state()
    dispatch("take cyber_arm_kit", player, state, [], [])
    player.room_id = "ripper_clinic"
    dispatch("install cyber_arm_kit", player, state, [], [])
    assert player.cyberware.get("arms") == "cyber_arm_v1"
    assert player.body == 4


def test_cyberware_list():
    player = make_player(room_id="square")
    state = make_state()
    dispatch("take cyber_arm_kit", player, state, [], [])
    player.room_id = "ripper_clinic"
    dispatch("install cyber_arm_kit", player, state, [], [])
    result = dispatch("cyberware", player, state, [], [])
    text = "\n".join(result.lines)
    assert "手臂" in text
    assert "漩渦義肢臂" in text


def test_kerenzikov_requires_ripperdoc():
    player = make_player(room_id="square", gold=500)
    state = make_state()
    player.inventory.append("kerenzikov_kit")
    result = dispatch("install kerenzikov_kit", player, state, [], [])
    assert "kerenzikov" not in player.cyberware.values()
    assert any("診所" in line for line in result.lines)

    player.room_id = "ripper_clinic"
    dispatch("install kerenzikov_kit", player, state, [], [])
    assert player.cyberware.get("nervous") == "kerenzikov"
    assert player.reflex == 5


def test_uninstall_at_ripperdoc():
    player = make_player(room_id="square", gold=100)
    state = make_state()
    dispatch("take cyber_arm_kit", player, state, [], [])
    player.room_id = "ripper_clinic"
    dispatch("install cyber_arm_kit", player, state, [], [])
    dispatch("uninstall arms", player, state, [], [])
    assert "arms" not in player.cyberware
    assert player.body == 3