from commands.registry import dispatch
from tests.conftest import make_player, make_state


def _ctx(room_id: str = "square"):
    return make_player(room_id=room_id), make_state()


def test_look_square():
    player, state = _ctx()
    result = dispatch("look", player, state, [], [])
    assert any("霓虹廣場" in line for line in result.lines)


def test_go_north():
    player, state = _ctx()
    result = dispatch("go north", player, state, [], [])
    assert player.room_id == "alley"
    assert result.moved


def test_alias_l():
    player, state = _ctx()
    result = dispatch("l", player, state, [], [])
    assert any("霓虹廣場" in line for line in result.lines)