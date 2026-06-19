from __future__ import annotations

from commands.registry import CommandContext, dispatch, player_meta
from tests.conftest import make_player, make_state


def test_player_meta_clears_net_shell_on_exit():
    player = make_player(room_id="square")
    state = make_state()
    dispatch("net", player, state, [], [])
    assert player.net_shell

    dispatch("exit", player, state, [], [])
    assert not player.net_shell

    meta = player_meta(CommandContext(player, state, ""))
    assert meta.get("net_shell") == "0"