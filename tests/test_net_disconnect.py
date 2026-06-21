from commands.registry import dispatch
from combat.encounter import start_encounter
from tests.conftest import make_player, make_state


def test_combat_start_disconnects_netrun():
    player = make_player(room_id="alley", locale="en")
    player.net_shell = True
    player.net_connected_node = "alley_node"
    state = make_state()
    start_encounter(state, player, "thug")
    assert not player.net_shell
    assert not player.net_connected_node
    assert player.in_combat


def test_go_disconnects_netrun():
    player = make_player(room_id="square", locale="en")
    state = make_state()
    dispatch("net", player, state, [], [])
    dispatch("go west", player, state, [], [])
    assert not player.net_shell
    assert player.room_id == "ripper_clinic"