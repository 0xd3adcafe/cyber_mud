from __future__ import annotations

from commands.registry import dispatch, player_meta, CommandContext
from tests.conftest import make_player, make_state


def test_net_enters_shell():
    player = make_player(room_id="square")
    state = make_state()
    result = dispatch("net", player, state, [], [])
    assert player.net_shell
    assert any("NETRUN" in line for line in result.lines)
    assert result.meta.get("net_shell") == "1"
    assert result.meta.get("net_prompt")


def test_netrun_alias_enters_shell():
    player = make_player(room_id="square")
    state = make_state()
    dispatch("netrun", player, state, [], [])
    assert player.net_shell


def test_probe_lists_nodes_in_room():
    player = make_player(room_id="square")
    state = make_state()
    dispatch("net", player, state, [], [])
    result = dispatch("probe", player, state, [], [])
    assert any("核心終端" in line for line in result.lines)


def test_hack_targets_room_node():
    player = make_player(room_id="square")
    player.ram = 4
    state = make_state()
    dispatch("net", player, state, [], [])
    result = dispatch("hack terminal", player, state, [], [])
    assert player.ram == 3
    assert any("入侵成功" in line for line in result.lines)
    assert result.world_changed


def test_hack_missing_node():
    player = make_player(room_id="square")
    state = make_state()
    dispatch("net", player, state, [], [])
    result = dispatch("hack missing", player, state, [], [])
    assert any("沒有" in line for line in result.lines)


def test_exit_leaves_shell():
    player = make_player(room_id="square")
    state = make_state()
    dispatch("net", player, state, [], [])
    result = dispatch("exit", player, state, [], [])
    assert not player.net_shell
    assert "net_shell" not in result.meta or result.meta.get("net_shell") != "1"


def test_net_shell_blocks_mud_commands():
    player = make_player(room_id="square")
    state = make_state()
    dispatch("net", player, state, [], [])
    result = dispatch("go north", player, state, [], [])
    assert player.room_id == "square"
    assert any("NETRUN" in line for line in result.lines)


def test_status_shows_ram_and_nodes():
    player = make_player(room_id="square")
    state = make_state()
    dispatch("net", player, state, [], [])
    result = dispatch("status", player, state, [], [])
    assert any("RAM" in line for line in result.lines)