from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_connect_breach_exploit_pipeline():
    player = make_player(room_id="square", locale="en", ram=8)
    state = make_state()
    dispatch("net", player, state, [], [])
    r1 = dispatch("connect terminal", player, state, [], [])
    assert player.net_connected_node == "terminal"
    assert any("Connected" in line or "連線" in line for line in r1.lines)
    r2 = dispatch("breach terminal", player, state, [], [])
    assert "terminal" in player.net_breached_nodes
    r3 = dispatch("exploit terminal", player, state, [], [])
    assert any("Exploit" in line or "入侵成功" in line for line in r3.lines)


def test_hack_auto_pipeline_compat():
    player = make_player(room_id="square", ram=4)
    state = make_state()
    dispatch("net", player, state, [], [])
    result = dispatch("hack terminal", player, state, [], [])
    assert any("入侵成功" in line or "Exploit" in line for line in result.lines)
    assert player.ram < 4