from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_cat_requires_breach():
    player = make_player(room_id="square", locale="en", ram=6)
    state = make_state()
    dispatch("net", player, state, [], [])
    dispatch("connect terminal", player, state, [], [])
    result = dispatch("cat access.log", player, state, [], [])
    assert any("Breach" in line or "突破" in line for line in result.lines)


def test_cat_and_cover_after_breach():
    player = make_player(room_id="square", locale="en", ram=6, footprint=20)
    player.net_trace = 40
    state = make_state()
    dispatch("net", player, state, [], [])
    dispatch("hack terminal", player, state, [], [])
    result = dispatch("cat access.log", player, state, [], [])
    text = "\n".join(result.lines)
    assert "watson_grid_node" in text or "guest" in text.lower()
    before_trace = player.net_trace
    before_fp = player.footprint
    dispatch("cover", player, state, [], [])
    assert player.net_trace < before_trace
    assert player.footprint <= before_fp