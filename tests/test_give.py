from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_give_item_to_peer():
    giver = make_player(name="V")
    receiver = make_player(name="Alt")
    state = make_state()
    dispatch("take glowstick", giver, state, [], [])
    result = dispatch("give glowstick Alt", giver, state, [receiver], [giver, receiver])
    assert "glowstick" not in giver.inventory
    assert "glowstick" in receiver.inventory
    assert any("交給" in line for line in result.lines)
    assert result.broadcast_key == "give.broadcast"


def test_give_missing_player():
    giver = make_player(name="V")
    state = make_state()
    dispatch("take glowstick", giver, state, [], [])
    result = dispatch("give glowstick Nobody", giver, state, [], [giver])
    assert any("沒有玩家" in line for line in result.lines)