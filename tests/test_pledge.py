from commands.registry import dispatch, player_meta, CommandContext
from tests.conftest import make_player, make_state


def _ctx():
    return make_player(), make_state()


def test_pledge_arasaka():
    player, state = _ctx()
    result = dispatch("pledge arasaka", player, state, [], [])
    assert player.faction == "arasaka"
    assert any("荒坂" in line for line in result.lines)
    meta = player_meta(CommandContext(player, state, ""))
    assert meta["faction"] == "荒坂公司"


def test_pledge_chinese_name():
    player, state = _ctx()
    dispatch("pledge 荒坂", player, state, [], [])
    assert player.faction == "arasaka"


def test_pledge_unknown():
    player, state = _ctx()
    result = dispatch("pledge nomad", player, state, [], [])
    assert player.faction == ""
    assert any("未知派系" in line for line in result.lines)