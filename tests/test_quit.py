from __future__ import annotations

import asyncio

from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_quit_logs_out_without_closing_session():
    player = make_player(named=True, name="Vy", inventory=["knife"])
    state = make_state()
    result = dispatch("quit", player, state, [], [])
    assert not result.quit_game
    assert not player.named
    assert player.inventory == []
    assert result.meta.get("auth") == "0"
    assert any("登出" in line for line in result.lines)


def test_quit_requires_auth_when_guest():
    player = make_player(named=False)
    state = make_state()
    result = dispatch("quit", player, state, [], [])
    assert not result.quit_game
    assert not player.named


def test_quit_returns_client_to_login_screen():
    async def _run() -> None:
        from client.app import CyberMudApp
        from client.meta_handlers import apply_meta

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(100, 40)) as pilot:
            apply_meta(app.view, "auth", "1")
            app._set_auth_ui(True)
            await pilot.pause()
            app._pending_logout = True
            app._return_to_login_screen(message="已登出。請重新登入。")
            await pilot.pause()
            assert not app.view.authenticated
            login = app.query_one("#login_container")
            assert "login-hidden" not in login.classes

    asyncio.run(_run())