from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_recall_to_tutorial():
    player = make_player(room_id="alley")
    state = make_state()
    result = dispatch("recall", player, state, [], [])
    assert player.room_id == "tutorial"
    assert result.moved
    assert any("訓練場" in line for line in result.lines)


def test_recall_blocked_in_combat():
    player = make_player(room_id="alley")
    state = make_state()
    dispatch("attack thug", player, state, [], [])
    result = dispatch("recall", player, state, [], [])
    assert player.room_id == "alley"
    assert any("戰鬥中" in line for line in result.lines)