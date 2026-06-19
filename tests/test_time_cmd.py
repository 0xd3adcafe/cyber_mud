from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_time_command():
    player, state = make_player(), make_state()
    result = dispatch("time", player, state, [], [])
    assert any("第1天" in line for line in result.lines)
    assert "time" in result.meta
    assert "period" in result.meta
    assert result.meta["period"] == "夜晚"