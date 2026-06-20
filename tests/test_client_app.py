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


def test_login_banner_rotates_tips():
    async def _run() -> None:
        from textual.widgets import Static

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(80, 40)) as pilot:
            await pilot.pause()
            title = app.query_one("#login_title", Static)
            first = str(title.render())
            app._login_motd_index = 1
            app._refresh_login_banner()
            second = str(title.render())
            assert first != second

    asyncio.run(_run())


def test_prompt_preview_shows_while_editing():
    async def _run() -> None:
        from textual.widgets import Input, Static

        from client.meta_handlers import apply_meta

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(100, 40)) as pilot:
            apply_meta(app.view, "auth", "1")
            apply_meta(app.view, "hp", "80/100")
            apply_meta(app.view, "name", "V")
            app._set_auth_ui(True)
            await pilot.pause()
            prompt = app.query_one("#prompt", Input)
            preview = app.query_one("#prompt_preview", Static)
            assert "preview-hidden" in preview.classes
            prompt.value = "/prompt set [%h] %n>"
            app._update_prompt_preview(prompt.value)
            assert "preview-hidden" not in preview.classes
            rendered = str(preview.render())
            assert "80/100" in rendered
            assert "V>" in rendered

    asyncio.run(_run())


def test_login_inputs_visible_on_small_terminal():
    async def _run() -> None:
        from textual.widgets import Input

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            scroll = app.query_one("#login_form_scroll")
            name = app.query_one("#login_name", Input)
            password = app.query_one("#login_password", Input)
            assert scroll.region.height > 0
            assert name.region.height >= 3
            assert password.region.height >= 3
            assert not name.disabled
            assert not password.disabled

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
            await pilot.press("t", "a", "k")
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


def test_stacked_sidebar_does_not_capture_focus():
    async def _run() -> None:
        from textual.containers import VerticalScroll
        from textual.widgets import Input

        from client.meta_handlers import apply_meta, handle_ui_json

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(100, 40)) as pilot:
            apply_meta(app.view, "auth", "1")
            app._set_auth_ui(True)
            await pilot.pause()
            app._configure_game_focus_targets()
            app.view.sidebar_open = True
            apply_meta(app.view, "ui_panel", "pda")
            handle_ui_json(
                app.view,
                '{"panel":"pda","sections":[{"kind":"row","label":"HP","value":"100/100"}]}',
            )
            apply_meta(app.view, "ui_panel_end", "1")
            apply_meta(app.view, "ui_panel", "map")
            handle_ui_json(
                app.view,
                '{"panel":"map","sections":[{"kind":"text","lines":["[@] square"," ■ "]}]}',
            )
            apply_meta(app.view, "ui_panel_end", "1")
            app._render_sidebar()
            await pilot.pause()
            sidebar = app.query_one("#sidebar", VerticalScroll)
            assert sidebar.can_focus is False
            prompt = app.query_one("#prompt", Input)
            app._focus_game_prompt()
            await pilot.pause()
            assert prompt.has_focus

    asyncio.run(_run())


def test_f6_closes_sidebar_and_ignores_late_panel_end():
    async def _run() -> None:
        from textual.containers import Vertical

        from client.meta_handlers import apply_meta, handle_ui_json

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(100, 40)) as pilot:
            apply_meta(app.view, "auth", "1")
            app._set_auth_ui(True)
            await pilot.pause()
            app.view.sidebar_open = True
            app.view.sidebar_stack = ["pda"]
            apply_meta(app.view, "ui_panel", "pda")
            handle_ui_json(
                app.view,
                '{"panel":"pda","sections":[{"kind":"row","label":"HP","value":"100/100"}]}',
            )
            apply_meta(app.view, "ui_panel_end", "1")
            app._render_sidebar()
            await pilot.pause()
            wrap = app.query_one("#sidebar_wrap", Vertical)
            assert "sidebar-visible" in wrap.classes

            await app.action_toggle_sidebar()
            await pilot.pause()
            assert not app.view.sidebar_open
            assert app.view.sidebar_stack == []
            assert "sidebar-hidden" in wrap.classes

            apply_meta(app.view, "ui_panel_end", "1")
            app._render_sidebar()
            await pilot.pause()
            assert not app.view.sidebar_open
            assert "sidebar-hidden" in wrap.classes

    asyncio.run(_run())


def test_chrome_bar_link_status_after_auth():
    async def _run() -> None:
        from textual.widgets import Static

        from client.meta_handlers import apply_meta

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(120, 30)) as pilot:
            apply_meta(app.view, "auth", "1")
            app._set_auth_ui(True)
            await pilot.pause()
            await pilot.pause()
            chrome = app.query_one("#chrome_bar", Static)
            assert chrome.region.height >= 1
            assert chrome.size.height >= 1
            rendered = str(chrome.render())
            assert "Link" in rendered
            assert "127.0.0.1:4000" in rendered
            assert "Hotkeys" not in rendered

    asyncio.run(_run())


def test_prompt_placeholder_follows_locale():
    async def _run() -> None:
        from client.completion import MudPrompt
        from client.meta_handlers import apply_meta

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(100, 30)) as pilot:
            apply_meta(app.view, "auth", "1")
            app._set_auth_ui(True)
            await pilot.pause()
            prompt = app.query_one("#prompt", MudPrompt)
            assert "command" in prompt.placeholder
            apply_meta(app.view, "locale", "zh")
            app._apply_meta("locale=zh")
            await pilot.pause()
            assert "指令" in prompt.placeholder

    asyncio.run(_run())


def test_hotkey_bar_below_prompt_after_auth():
    async def _run() -> None:
        from textual.widgets import Static

        from client.meta_handlers import apply_meta

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(120, 30)) as pilot:
            apply_meta(app.view, "auth", "1")
            app._set_auth_ui(True)
            app._refresh_game_layout()
            await pilot.pause()
            await pilot.pause()
            info = app.query_one("#info_bar", Static)
            prompt = app.query_one("#prompt_dock")
            hotkey = app.query_one("#hotkey_bar", Static)
            chrome = app.query_one("#chrome_bar", Static)
            main = app.query_one("#main_row")
            assert chrome.region.width > 0
            assert chrome.region.height >= 1
            assert chrome.size.height >= 1
            assert hotkey.region.height >= 1
            assert hotkey.size.height >= 1
            assert chrome.region.y == info.region.y + info.region.height
            assert hotkey.region.y == prompt.region.y + prompt.region.height
            assert main.region.y == chrome.region.y + chrome.region.height
            rendered = str(hotkey.render())
            assert "Hotkeys" in rendered
            assert "F2" in rendered
            assert "/reconnect" in rendered

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


def test_typed_map_command_opens_sidebar():
    async def _run() -> None:
        from textual.containers import Vertical

        from client.meta_handlers import apply_meta, handle_ui_json, prepare_sidebar_for_panel

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(120, 30)) as pilot:
            apply_meta(app.view, "auth", "1")
            app._set_auth_ui(True)
            await pilot.pause()
            prepare_sidebar_for_panel(app.view, "map")
            app.view.pending_panel = "map"
            app._render_sidebar()
            await pilot.pause()
            wrap = app.query_one("#sidebar_wrap", Vertical)
            assert "sidebar-visible" in wrap.classes
            apply_meta(app.view, "ui_panel", "map")
            handle_ui_json(
                app.view,
                '{"panel":"map","sections":[{"kind":"text","lines":["[@] square"]}]}',
            )
            apply_meta(app.view, "ui_panel_end", "1")
            app._apply_meta("ui_panel_end=1")
            await pilot.pause()
            assert "map" in app.view.sidebar_stack
            assert "sidebar-visible" in wrap.classes

    asyncio.run(_run())


def test_panel_fetch_actions_do_not_block():
    async def _run() -> None:
        import time

        from client.meta_handlers import apply_meta

        app = CyberMudApp("127.0.0.1", 4000)
        scheduled: list[str] = []
        help_scheduled = 0

        def _capture_schedule(panel_id: str) -> None:
            scheduled.append(panel_id)

        def _capture_help() -> None:
            nonlocal help_scheduled
            help_scheduled += 1

        async with app.run_test(size=(120, 30)) as pilot:
            apply_meta(app.view, "auth", "1")
            app._set_auth_ui(True)
            app._schedule_panel_fetch = _capture_schedule
            app._schedule_help_fetch = _capture_help
            await pilot.pause()
            t0 = time.monotonic()
            await app.action_panel_pda()
            await app.action_panel_map()
            await app.action_panel_help()
            elapsed = time.monotonic() - t0
            assert elapsed < 0.5
            assert scheduled == ["pda", "map"]
            assert help_scheduled == 1

    asyncio.run(_run())


def test_help_overlay_covers_log_not_sidebar():
    async def _run() -> None:
        from textual.containers import Container, Vertical, VerticalScroll
        from textual.widgets import Static

        from client.meta_handlers import apply_meta, handle_ui_json

        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(120, 30)) as pilot:
            apply_meta(app.view, "auth", "1")
            app._set_auth_ui(True)
            await pilot.pause()
            wrap = app.query_one("#sidebar_wrap", Vertical)
            dropdown = app.query_one("#help_dropdown", Vertical)
            assert "help-dropdown-hidden" in dropdown.classes
            assert "sidebar-hidden" in wrap.classes

            app._open_help_overlay()
            await pilot.pause()
            assert "help-dropdown-hidden" not in dropdown.classes
            assert "sidebar-hidden" in wrap.classes

            apply_meta(app.view, "ui_panel", "help")
            handle_ui_json(
                app.view,
                '{"panel":"help","sections":[{"kind":"list","items":["look — 察看","go — 移動"]}]}',
            )
            apply_meta(app.view, "ui_panel_end", "1")
            app._render_help_overlay()
            await pilot.pause()
            content = app.query_one("#help_dropdown_content", Static)
            rendered = str(content.render())
            assert "look" in rendered
            assert "help" not in app.view.sidebar_stack

            scroll = app.query_one("#help_dropdown_scroll", VerticalScroll)
            log_wrap = app.query_one("#scrollback_wrap", Container)
            assert scroll.region.width >= log_wrap.region.width - 4

    asyncio.run(_run())