from __future__ import annotations

import asyncio

from textual.widgets import Select

from client.app import CyberMudApp


def test_auth_select_mounts_with_login_value():
    async def _run() -> None:
        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(80, 40)):
            select = app.query_one("#auth_mode", Select)
            assert select.value == "login"

    asyncio.run(_run())


def test_login_theme_select_mounts():
    async def _run() -> None:
        from client.themes import theme_ids

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(100, 40)):
            theme = app.query_one("#login_theme", Select)
            assert theme.value in theme_ids()

    asyncio.run(_run())


def test_credential_pin_section_hidden_without_store(monkeypatch):
    async def _run() -> None:
        from textual.widgets import Input

        monkeypatch.setattr("client.app.has_stored_credentials", lambda: False)
        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(80, 40)) as pilot:
            await pilot.pause()
            pin = app.query_one("#login_pin", Input)
            assert "credential-hidden" in pin.classes

    asyncio.run(_run())


def test_credential_pin_section_visible_with_store(monkeypatch):
    async def _run() -> None:
        from textual.widgets import Input

        monkeypatch.setattr("client.app.has_stored_credentials", lambda: True)
        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(80, 40)) as pilot:
            await pilot.pause()
            pin = app.query_one("#login_pin", Input)
            assert "credential-hidden" not in pin.classes

    asyncio.run(_run())


def test_login_inputs_visible_on_small_terminal():
    async def _run() -> None:
        from textual.widgets import Input

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            container = app.query_one("#login_container")
            name = app.query_one("#login_name", Input)
            password = app.query_one("#login_password", Input)
            bottom = container.region.y + container.region.height
            assert name.region.y + name.region.height <= bottom
            assert password.region.y + password.region.height <= bottom
            assert name.region.height >= 3
            assert password.region.height >= 3

    asyncio.run(_run())


def test_tab_complete_fills_verb():
    async def _run() -> None:
        from textual.widgets import Input

        from client.meta_handlers import apply_meta

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(100, 40)) as pilot:
            apply_meta(app.view, "auth", "1")
            app._set_auth_ui(True)
            await pilot.pause()
            prompt = app.query_one("#prompt", Input)
            await pilot.press("t")
            await pilot.pause()
            await pilot.press("tab")
            await pilot.pause()
            assert prompt.value == "take"

    asyncio.run(_run())


def test_tab_complete_fills_target():
    async def _run() -> None:
        from textual.widgets import Input

        from client.meta_handlers import apply_meta

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(100, 40)) as pilot:
            apply_meta(app.view, "auth", "1")
            apply_meta(app.view, "complete_room_items", "glowstick,knife")
            app._set_auth_ui(True)
            await pilot.pause()
            prompt = app.query_one("#prompt", Input)
            await pilot.press("t", "a", "k", "e", " ", "g")
            await pilot.pause()
            await pilot.press("tab")
            await pilot.pause()
            assert prompt.value == "take glowstick"

    asyncio.run(_run())


def test_game_layout_fills_terminal_after_auth():
    async def _run() -> None:
        from textual.widgets import Input, RichLog

        from client.meta_handlers import apply_meta

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(100, 40)) as pilot:
            apply_meta(app.view, "auth", "1")
            app._set_auth_ui(True)
            await pilot.pause()
            game = app.query_one("#game_container")
            main_row = app.query_one("#main_row")
            prompt_row = app.query_one("#prompt_row")
            prompt = app.query_one("#prompt", Input)
            log = app.query_one("#log", RichLog)
            assert game.size.height >= 30
            assert main_row.size.height > prompt_row.size.height * 2
            assert prompt.region.x < prompt_row.region.width
            assert prompt.size.width > 10
            assert log.can_focus is False
            assert prompt.has_focus
            await pilot.press("l", "o", "o", "k")
            await pilot.pause()
            assert prompt.value == "look"

    asyncio.run(_run())