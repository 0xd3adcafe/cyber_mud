from __future__ import annotations

from commands.registry import dispatch
from persistence.save import load_player, player_exists
from tests.conftest import make_player, make_state


def _ctx(*, named: bool = False, name: str = "旅人"):
    return make_player(named=named, name=name), make_state()


def test_unauthenticated_gate():
    player, state = _ctx()
    result = dispatch("look", player, state, [], [])
    assert any("登入" in line or "註冊" in line for line in result.lines)
    assert not player.named


def test_register_and_persist(save_dir):
    player, state = _ctx()
    result = dispatch("register TestRunner secret123", player, state, [], [])
    assert result.auth_event
    assert player.named
    assert player.name == "TestRunner"
    assert player_exists("TestRunner")
    loaded = load_player("TestRunner")
    assert loaded is not None
    assert loaded.room_id == "square"
    assert loaded.inventory == []


def test_login_after_register(save_dir):
    player, state = _ctx()
    dispatch("register TestRunner secret123", player, state, [], [])

    player2, state2 = _ctx()
    result = dispatch("login TestRunner secret123", player2, state2, [], [])
    assert result.auth_event
    assert player2.named
    assert player2.name == "TestRunner"


def test_login_bad_password(save_dir):
    player, state = _ctx()
    dispatch("register TestRunner secret123", player, state, [], [])

    player2, state2 = _ctx()
    result = dispatch("login TestRunner wrong", player2, state2, [], [])
    assert any("帳號" in line or "密碼" in line for line in result.lines)
    assert not player2.named


def test_register_name_taken(save_dir):
    player, state = _ctx()
    dispatch("register TestRunner secret123", player, state, [], [])

    player2, state2 = _ctx()
    result = dispatch("register TestRunner otherpass", player2, state2, [], [])
    assert any("已被使用" in line for line in result.lines)
    assert not player2.named