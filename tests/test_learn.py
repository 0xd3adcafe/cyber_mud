from commands.registry import dispatch
from tests.conftest import make_player, make_state


def _ctx(*, gold: int = 500):
    player = make_player(room_id="square")
    player.gold = gold
    state = make_state()
    state.npc_rooms["broker"] = "square"
    return player, state


def test_learn_quickhack_from_broker():
    player, state = _ctx()
    result = dispatch("learn quickhack", player, state, [], [])
    assert "quickhack" in player.skills
    assert player.gold == 350
    assert any("快速破解" in line for line in result.lines)
    assert result.refresh_sidebar


def test_learn_no_gold():
    player, state = _ctx(gold=10)
    result = dispatch("learn quickhack", player, state, [], [])
    assert "quickhack" not in player.skills
    assert any("金錢不足" in line for line in result.lines)


def test_learn_broker_not_here():
    player, state = _ctx()
    state.npc_rooms["broker"] = "alley"
    result = dispatch("learn quickhack", player, state, [], [])
    assert "quickhack" not in player.skills
    assert any("沒有" in line for line in result.lines)