from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_go_sets_presence_from_room():
    player = make_player(room_id="square")
    state = make_state()
    result = dispatch("go north", player, state, [], [])
    assert result.moved
    assert result.presence_from_room == "square"
    assert player.room_id == "alley"


def test_look_lists_peers_with_posture():
    player = make_player(name="V", room_id="square")
    peer = make_player(name="Alt", room_id="square")
    state = make_state()
    result = dispatch("look", player, state, [peer], [player, peer])
    assert any("Alt" in line for line in result.lines)


def test_say_sets_broadcast_key():
    player = make_player(name="V", room_id="square")
    state = make_state()
    result = dispatch("say hello", player, state, [], [player])
    assert result.broadcast_key == "say.broadcast"
    assert result.broadcast_kwargs["message"] == "hello"