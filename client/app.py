from __future__ import annotations

import asyncio
import time

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.events import Click, DescendantFocus, Resize
from textual.widgets import Checkbox, Footer, Header, Input, RichLog, Select, Static

from client.auth_ui import build_auth_command
from client.credentials import (
    clear_credentials,
    has_stored_credentials,
    save_credentials,
    unlock_credentials,
    validate_pin,
)
from client.connection import ServerConnection
from client.login_art import render_login_art
from client.help_overlay import format_help_overlay_content, help_overlay_header
from client.login_motd import banner_text, default_tips, parse_motd_line
from client.prompt_preview import (
    detect_prompt_edit,
    expand_prompt_from_view,
    format_prompt_preview,
    format_prompt_show_lines,
)
from shared.i18n import t
from shared.prompt_tokens import CP2077_TEMPLATES
from client.themes import (
    DEFAULT_THEME_ID,
    build_textual_theme,
    format_theme_list,
    load_theme_id,
    parse_theme_command,
    resolve_theme_id,
    save_theme_id,
    select_options,
    theme_ids,
    theme_label,
)
from client.animated_log import AnimatedLogBuffer
from commands.aliases import DEFAULT_ALIASES
from client.status_indicators import status_needs_animation
from client.completion import MudPrompt, MudSuggester, complete_cycle_from_view, complete_from_view
from client.history import CommandHistory
from client.link_status import format_link_status_bar, make_link_snapshot
from client.reconnect import reconnect_status_message, should_resend_auth
from client.output_prefix import classify_output_line, spinner_char
from client.tui_styles import APP_CSS
from client.ui_format import format_hotkey_bar, format_info_bar, format_sidebar_header
from client.meta_handlers import (
    HELP_OVERLAY_PANEL,
    ClientViewState,
    active_prompt,
    apply_meta,
    classify_server_line,
    format_sidebar_content,
    handle_panel_line,
    handle_ui_json,
    is_local_command,
    prepare_netrun_outbound,
    panels_to_refresh_on_equip,
    panels_to_refresh_on_move,
    parse_local_command,
    parse_meta_payload,
    prepare_sidebar_for_panel,
    reconnect_delay,
    resolve_panel_command,
    should_refresh_sidebar_on_room_change,
    sidebar_should_show,
    toggle_sidebar_panel,
)
from shared.protocol import ERR_PREFIX, META_PREFIX, MOTD_PREFIX, PANEL_PREFIX, SYS_PREFIX, UI_PREFIX
from shared.startup import StartupReport


class CyberMudApp(App):
    TITLE = "cyber_mud"
    SUB_TITLE = "夜城神經連結"
    MAX_RECONNECT_ATTEMPTS = 5

    BINDINGS = [
        Binding("ctrl+c", "quit", "離開"),
        Binding("tab", "tab_complete", "補全", show=False),
        Binding("f2", "panel_pda", "PDA", show=True),
        Binding("f3", "panel_help", "說明", show=True),
        Binding("f4", "panel_map", "地圖", show=True),
        Binding("f5", "panel_equipment", "裝備", show=True),
        Binding("f6", "toggle_sidebar", "收合側欄", show=True),
        Binding("f7", "panel_gigs", "委託", show=True),
        Binding("escape", "close_help_overlay", "關閉說明", show=False),
    ]

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.conn = ServerConnection(host, port)
        self.view = ClientViewState()
        self._reader_task: asyncio.Task | None = None
        self._reconnect_task: asyncio.Task | None = None
        self._reconnect_attempts = 0
        self._needs_reauth = False
        self._reconnecting = False
        self._last_auth_line = ""
        self._local_prompt_override = ""
        self._auth_pending = False
        self._theme_id = DEFAULT_THEME_ID
        self._log_buffer = AnimatedLogBuffer()
        self._command_history = CommandHistory.load()
        self._pending_credential_save: tuple[str, str, str, str] | None = None
        self._startup_hint = ""
        self._pending_logout = False
        self._sidebar_refresh_lock = asyncio.Lock()
        self._panel_fetch_event: asyncio.Event | None = None
        self._panel_fetching = False
        self._panel_fetch_generation = 0
        self._help_overlay_open = False
        self._help_fetch_event: asyncio.Event | None = None
        self._help_fetching = False
        self._help_fetch_generation = 0
        self._cmd_sent_at = 0.0
        self._last_recv_at = 0.0
        self._completion_cycle_key = ""
        self._completion_cycle_index = 0
        self._last_rtt_ms: float | None = None
        self._login_locale = "zh"
        self._login_motd_tips: list[str] = []
        self._login_motd_index = 0
        self._login_motd_frame = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(id="login_container"):
            yield Static("", id="login_art", markup=False)
            with VerticalScroll(id="login_form_scroll"):
                with Vertical(id="login_form"):
                    yield Static(
                        "[bold]◈ 夜城神經連結[/]\n[dim]NEURAL LINK · cyber_mud[/]",
                        id="login_title",
                    )
                    yield Static("[dim]視覺主題[/]", id="login_theme_label")
                    yield Select(
                        select_options(),
                        id="login_theme",
                        value=DEFAULT_THEME_ID,
                        allow_blank=False,
                    )
                    yield Static(
                        "[dim]快速登入（PIN）[/]",
                        id="login_pin_label",
                        classes="credential-hidden",
                    )
                    yield Input(
                        placeholder="4–6 位 PIN",
                        id="login_pin",
                        password=True,
                        classes="credential-hidden",
                    )
                    yield Static("[dim]帳號模式[/]", id="auth_mode_label")
                    yield Select(
                        (("登入既有帳號", "login"), ("註冊新帳號", "register")),
                        id="auth_mode",
                        value="login",
                        allow_blank=False,
                    )
                    yield Static("[dim]使用者名稱[/]", id="login_name_label")
                    yield Input(placeholder="runner_id", id="login_name")
                    yield Static("[dim]密碼[/]", id="login_password_label")
                    yield Input(placeholder="••••••••", id="login_password", password=True)
                    yield Checkbox("記住帳號（PIN 保護）", id="remember_credentials", value=False)
                    yield Static(
                        "[dim]設定 PIN[/]",
                        id="login_pin_setup_label",
                        classes="credential-hidden",
                    )
                    yield Input(
                        placeholder="新 PIN",
                        id="login_pin_setup",
                        password=True,
                        classes="credential-hidden",
                    )
                    yield Static(
                        "[dim]確認 PIN[/]",
                        id="login_pin_confirm_label",
                        classes="credential-hidden",
                    )
                    yield Input(
                        placeholder="再輸入一次",
                        id="login_pin_confirm",
                        password=True,
                        classes="credential-hidden",
                    )
                    yield Static("[dim]Enter 送出 · Ctrl+C 離開[/]", id="login_hint")
                    yield Static("", id="login_status")

        with Container(id="game_container", classes="game-hidden"):
            with Vertical(id="top_dock"):
                yield Static(self._info_bar(), id="info_bar")
                yield Static(self._chrome_bar(), id="chrome_bar")
            with Horizontal(id="main_row"):
                with Container(id="scrollback_wrap"):
                    yield RichLog(id="log", highlight=True, markup=True)
                    with Vertical(id="help_dropdown", classes="help-dropdown-hidden"):
                        yield Static(help_overlay_header(), id="help_dropdown_header")
                        with VerticalScroll(id="help_dropdown_scroll"):
                            yield Static("", id="help_dropdown_content")
                with Vertical(id="sidebar_wrap", classes="sidebar-hidden"):
                    yield Static("", id="sidebar_header")
                    yield VerticalScroll(
                        Static("", id="sidebar_content"),
                        id="sidebar",
                    )
            with Vertical(id="bottom_dock"):
                with Horizontal(id="prompt_dock"):
                    yield Static("❙", id="prompt_accent")
                    with Horizontal(id="prompt_row"):
                        yield Static(self._prompt_prefix(), id="prompt_prefix")
                        yield MudPrompt(
                            placeholder="指令 · Tab 補全 · ↑↓ 歷史 · Esc 還原 · Enter 送出",
                            id="prompt",
                            suggester=MudSuggester(lambda: self.view),
                        )
                yield Static("", id="prompt_preview", classes="preview-hidden")
                yield Static(format_hotkey_bar(), id="hotkey_bar")

        yield Footer()

    def _info_bar(self) -> str:
        return format_info_bar(
            self.view,
            host=self.host,
            port=self.port,
            reconnecting=self._reconnecting,
            spinner_frame=self._log_buffer.frame,
        )

    def _needs_ui_animation(self) -> bool:
        return self._log_buffer.has_pending() or status_needs_animation(self.view)

    def _link_status_bar(self) -> str:
        return format_link_status_bar(
            make_link_snapshot(
                connected=self.conn.connected,
                reconnecting=self._reconnecting,
                command_pending=self._log_buffer.has_pending(),
                panel_fetching=self._panel_fetching or self._help_fetching,
                auth_pending=self._auth_pending,
                last_rtt_ms=self._last_rtt_ms,
                last_recv_at=self._last_recv_at,
                last_send_at=self._cmd_sent_at,
            ),
            frame=self._log_buffer.frame,
            host=self.host,
            port=self.port,
        )

    def _chrome_bar(self) -> str:
        return self._link_status_bar()

    def _update_chrome_bar(self) -> None:
        if not self.view.authenticated:
            return
        try:
            self.query_one("#chrome_bar", Static).update(self._chrome_bar())
        except Exception:
            pass

    def _refresh_game_layout(self) -> None:
        if not self.view.authenticated:
            return
        self.query_one("#game_container").refresh(layout=True)

    def _update_link_status_bar(self) -> None:
        self._update_chrome_bar()

    def _note_outbound(self) -> None:
        self._cmd_sent_at = time.monotonic()

    def _note_inbound(self) -> None:
        now = time.monotonic()
        if self._log_buffer.has_pending() and self._cmd_sent_at > 0:
            self._last_rtt_ms = (now - self._cmd_sent_at) * 1000.0
        self._last_recv_at = now
        self._update_link_status_bar()

    def _append_log(self, log: RichLog, text: str, *, kind: str | None = None) -> None:
        resolved = kind or classify_output_line(text)
        self._log_buffer.append(text, kind=resolved)
        line = self._log_buffer.render_entry()
        if line is not None:
            log.write(line)
        else:
            self._refresh_log_display(log, scroll_end=True)

    def _refresh_log_display(self, log: RichLog, *, preserve_scroll: bool = False, scroll_end: bool = False) -> None:
        y = log.scroll_y if preserve_scroll else None
        auto = log.auto_scroll
        log.auto_scroll = scroll_end
        log.clear()
        for line in self._log_buffer.render():
            log.write(line)
        if preserve_scroll and y is not None:
            log.scroll_y = y
        log.auto_scroll = auto

    def _update_spinner_accent(self) -> None:
        if not self.view.authenticated:
            return
        accent = spinner_char(self._log_buffer.frame) if self._log_buffer.has_pending() else "❙"
        try:
            self.query_one("#prompt_accent", Static).update(accent)
        except Exception:
            pass

    def _complete_command_if_pending(self, log: RichLog) -> None:
        if self._log_buffer.complete_pending():
            self._refresh_log_display(log, preserve_scroll=True)
            self._update_spinner_accent()
            self._update_link_status_bar()

    def _advance_ui_frame(self) -> None:
        self._log_buffer.frame += 1

    def _on_spinner_tick(self) -> None:
        if not self.view.authenticated:
            return
        if self._needs_ui_animation():
            self._advance_ui_frame()
        self._update_spinner_accent()
        if status_needs_animation(self.view) and self._log_buffer.frame % 2 == 0:
            try:
                self.query_one("#info_bar", Static).update(self._info_bar())
            except Exception:
                pass
        self._update_link_status_bar()

    def _on_cd_tick(self) -> None:
        if not self.view.authenticated:
            return
        changed = self._log_buffer.tick_cooldowns()
        if changed:
            self._refresh_log_display(self.query_one("#log", RichLog), preserve_scroll=True)
        if self.view.in_combat or status_needs_animation(self.view):
            self.query_one("#info_bar", Static).update(self._info_bar())

    def _prompt_prefix(self) -> str:
        return active_prompt(self.view, local_override=self._local_prompt_override)

    def _update_prompt_preview(self, text: str) -> None:
        preview = self.query_one("#prompt_preview", Static)
        ctx = detect_prompt_edit(text)
        if ctx is None:
            preview.add_class("preview-hidden")
            preview.update("")
            return
        expanded = expand_prompt_from_view(ctx.template, self.view)
        preview.remove_class("preview-hidden")
        preview.update(format_prompt_preview(ctx.template, expanded))

    def _clear_prompt_preview(self) -> None:
        preview = self.query_one("#prompt_preview", Static)
        preview.add_class("preview-hidden")
        preview.update("")

    def _login_art_rows(self) -> int:
        try:
            widget = self.query_one("#login_art", Static)
            if widget.size.height > 0:
                return max(6, widget.size.height)
        except Exception:
            pass
        # Header + footer consume two rows; login_art is 50% of the remainder.
        return max(6, (self.size.height - 2) // 2)

    def _login_art_width(self) -> int:
        try:
            widget = self.query_one("#login_art", Static)
            if widget.size.width > 0:
                return max(40, widget.size.width)
        except Exception:
            pass
        return max(40, self.size.width)

    def _register_themes(self) -> None:
        for theme_id in theme_ids():
            self.register_theme(build_textual_theme(theme_id))

    def _apply_theme(self, theme_id: str, *, persist: bool = True) -> None:
        resolved = resolve_theme_id(theme_id) or DEFAULT_THEME_ID
        self._theme_id = resolved
        self.theme = resolved
        self._log_buffer.set_theme_id(resolved)
        if persist:
            save_theme_id(resolved)
        if not self.view.authenticated:
            self._refresh_login_art()
        else:
            try:
                log = self.query_one("#log", RichLog)
                self._refresh_log_display(log, preserve_scroll=True)
            except Exception:
                pass

    def _refresh_login_art(self) -> None:
        art = render_login_art(
            self._login_art_rows(),
            max_width=self._login_art_width(),
            theme_id=self._theme_id,
        )
        art_widget = self.query_one("#login_art", Static)
        art_widget._render_markup = False
        art_widget.update(art)

    def _set_login_status(self, text: str) -> None:
        self.query_one("#login_status", Static).update(text)

    def _reset_login_motd(self) -> None:
        self._login_motd_tips = default_tips(self._login_locale)
        self._login_motd_index = 0
        self._login_motd_frame = 0
        self._refresh_login_banner()

    def _refresh_login_banner(self) -> None:
        text = banner_text(
            locale=self._login_locale,
            tips=self._login_motd_tips,
            tip_index=self._login_motd_index,
            frame=self._login_motd_frame,
        )
        self.query_one("#login_title", Static).update(text)

    def _add_login_motd_tip(self, line: str) -> None:
        title = t(self._login_locale, "motd.title")
        tip = parse_motd_line(line, title=title if title != "motd.title" else "")
        if not tip:
            return
        if tip not in self._login_motd_tips:
            self._login_motd_tips.append(tip)
        self._refresh_login_banner()

    def _on_login_motd_tick(self) -> None:
        if self.view.authenticated:
            return
        self._login_motd_frame += 1
        if self._login_motd_tips and self._login_motd_frame % 6 == 0:
            self._login_motd_index = (self._login_motd_index + 1) % len(self._login_motd_tips)
        self._refresh_login_banner()

    def _set_login_hint(self, text: str) -> None:
        self.query_one("#login_hint", Static).update(text)

    def _set_login_form_active(self, active: bool) -> None:
        self.query_one("#login_name", Input).disabled = not active
        self.query_one("#login_password", Input).disabled = not active
        self.query_one("#login_theme", Select).disabled = not active
        self.query_one("#auth_mode", Select).disabled = not active
        self.query_one("#login_pin", Input).disabled = not active
        self.query_one("#remember_credentials", Checkbox).disabled = not active
        self.query_one("#login_pin_setup", Input).disabled = not active
        self.query_one("#login_pin_confirm", Input).disabled = not active

    def _credential_widget_ids(self) -> tuple[str, ...]:
        return (
            "#login_pin_label",
            "#login_pin",
            "#login_pin_setup_label",
            "#login_pin_setup",
            "#login_pin_confirm_label",
            "#login_pin_confirm",
        )

    def _set_credential_section_visible(self, widget_id: str, visible: bool) -> None:
        widget = self.query_one(widget_id)
        if visible:
            widget.remove_class("credential-hidden")
        else:
            widget.add_class("credential-hidden")

    def _refresh_credential_ui(self) -> None:
        stored = has_stored_credentials()
        remember = self.query_one("#remember_credentials", Checkbox).value
        self._set_credential_section_visible("#login_pin_label", stored)
        self._set_credential_section_visible("#login_pin", stored)
        show_setup = remember
        self._set_credential_section_visible("#login_pin_setup_label", show_setup)
        self._set_credential_section_visible("#login_pin_setup", show_setup)
        self._set_credential_section_visible("#login_pin_confirm_label", show_setup)
        self._set_credential_section_visible("#login_pin_confirm", show_setup)
        base = self._startup_hint or "Enter 送出 · Ctrl+C 離開"
        if stored:
            self._set_login_hint(f"{base} · PIN 快速登入 · F7 清除記憶")
        else:
            self._set_login_hint(base)

    def _focus_login_entry(self) -> None:
        if has_stored_credentials():
            self.query_one("#login_pin", Input).focus()
        else:
            self.query_one("#login_name", Input).focus()

    def _clear_pin_fields(self) -> None:
        self.query_one("#login_pin", Input).value = ""
        self.query_one("#login_pin_setup", Input).value = ""
        self.query_one("#login_pin_confirm", Input).value = ""

    def _is_server_quit_command(self, text: str) -> bool:
        parts = text.strip().split(maxsplit=1)
        if not parts:
            return False
        verb = parts[0].lower()
        if verb in ("quit", "q"):
            return True
        return DEFAULT_ALIASES.get(verb) == "quit"

    def _return_to_login_screen(self, *, message: str = "") -> None:
        self._cancel_reconnect_task()
        self._reconnecting = False
        self._reconnect_attempts = 0
        self._needs_reauth = False
        self._last_auth_line = ""
        self._auth_pending = False
        self._pending_logout = False
        self.view = ClientViewState()
        self._log_buffer = AnimatedLogBuffer()
        self._log_buffer.set_theme_id(self._theme_id)
        log = self.query_one("#log", RichLog)
        log.clear()
        self._set_auth_ui(False)
        if message:
            self._set_login_status(message)
        self._refresh_credential_ui()

    def _persist_credentials_if_pending(self) -> None:
        pending = self._pending_credential_save
        if pending is None:
            return
        name, password, mode, pin = pending
        err = save_credentials(username=name, password=password, mode=mode, pin=pin)
        self._pending_credential_save = None
        if err:
            self._set_login_status(f"帳號已登入，但儲存失敗：{err}")
            return
        self._refresh_credential_ui()

    def _focus_game_prompt(self) -> None:
        if not self.view.authenticated:
            return
        prompt = self.query_one("#prompt", MudPrompt)
        prompt.disabled = False
        self.set_focus(prompt)

    def _set_auth_ui(self, authenticated: bool) -> None:
        self.view.authenticated = authenticated
        login = self.query_one("#login_container")
        game = self.query_one("#game_container")
        if authenticated:
            login.add_class("login-hidden")
            game.remove_class("game-hidden")
            self._set_login_form_active(False)
            if self.conn.connected and self._last_recv_at <= 0:
                self._last_recv_at = time.monotonic()
            self._update_status()
            self._update_spinner_accent()
            self.call_after_refresh(self._update_status)
            self.call_after_refresh(self._refresh_game_layout)
            self.call_after_refresh(self._focus_game_prompt)
        else:
            login.remove_class("login-hidden")
            game.add_class("game-hidden")
            self._set_login_form_active(True)
            self._reset_login_motd()
            self._refresh_login_art()
            self._refresh_credential_ui()
            self._focus_login_entry()

    def _update_status(self) -> None:
        if not self.view.authenticated:
            return
        self.query_one("#info_bar", Static).update(self._info_bar())
        self.query_one("#hotkey_bar", Static).update(format_hotkey_bar())
        self.query_one("#prompt_prefix", Static).update(self._prompt_prefix())
        self._update_chrome_bar()

    def _configure_game_focus_targets(self) -> None:
        log = self.query_one("#log", RichLog)
        log.can_focus = False
        for widget_id in ("#sidebar", "#sidebar_content", "#sidebar_header"):
            try:
                self.query_one(widget_id).can_focus = False
            except Exception:
                pass

    def _render_sidebar(self) -> None:
        if not self.view.authenticated:
            return
        wrap = self.query_one("#sidebar_wrap", Vertical)
        content = self.query_one("#sidebar_content", Static)
        header = self.query_one("#sidebar_header", Static)
        if not sidebar_should_show(self.view):
            content.update("")
            header.update("")
            wrap.remove_class("sidebar-visible")
            wrap.add_class("sidebar-hidden")
            return
        header.update(format_sidebar_header(self.view))
        content.update(format_sidebar_content(self.view))
        wrap.remove_class("sidebar-hidden")
        wrap.add_class("sidebar-visible")
        self.call_after_refresh(self._focus_game_prompt)

    def _configure_help_overlay_focus(self) -> None:
        try:
            self.query_one("#help_dropdown_scroll").can_focus = False
        except Exception:
            pass

    def _render_help_overlay(self) -> None:
        dropdown = self.query_one("#help_dropdown", Vertical)
        header = self.query_one("#help_dropdown_header", Static)
        content = self.query_one("#help_dropdown_content", Static)
        if not self._help_overlay_open:
            dropdown.add_class("help-dropdown-hidden")
            content.update("")
            return
        dropdown.remove_class("help-dropdown-hidden")
        header.update(help_overlay_header())
        panel = self.view.sidebar_panels.get(HELP_OVERLAY_PANEL)
        content.update(format_help_overlay_content(panel))
        self.call_after_refresh(self._focus_game_prompt)

    def _cancel_help_fetch(self) -> None:
        self._help_fetch_generation += 1
        if self._help_fetch_event is not None:
            self._help_fetch_event.set()
        self._help_fetching = False
        self._help_fetch_event = None

    def _schedule_help_fetch(self) -> None:
        asyncio.create_task(self._fetch_help())

    async def _fetch_help(self) -> None:
        generation = self._help_fetch_generation
        if generation != self._help_fetch_generation or not self.conn.connected:
            return
        event = asyncio.Event()
        self._help_fetch_event = event
        self._help_fetching = True
        self._update_link_status_bar()
        try:
            apply_meta(self.view, "ui_panel", HELP_OVERLAY_PANEL)
            self._note_outbound()
            await self.conn.send_line("help")
            await asyncio.wait_for(event.wait(), timeout=15.0)
        except asyncio.TimeoutError:
            pass
        finally:
            if generation != self._help_fetch_generation:
                return
            self._help_fetching = False
            if self._help_fetch_event is event:
                self._help_fetch_event = None
            self._update_link_status_bar()

    def _open_help_overlay(self) -> None:
        if "help" in self.view.sidebar_stack:
            self.view.sidebar_stack.remove("help")
        self._help_overlay_open = True
        apply_meta(self.view, "ui_panel", HELP_OVERLAY_PANEL)
        self._render_help_overlay()
        self._schedule_help_fetch()

    def _close_help_overlay(self) -> None:
        if not self._help_overlay_open:
            return
        self._cancel_help_fetch()
        self._help_overlay_open = False
        self.view.pending_panel = ""
        if "help" in self.view.sidebar_stack:
            self.view.sidebar_stack.remove("help")
        self._render_help_overlay()

    def _toggle_help_overlay(self) -> None:
        if self._help_overlay_open:
            self._close_help_overlay()
        else:
            self._open_help_overlay()

    def _help_panel_active(self) -> bool:
        return self._help_overlay_open or self.view.pending_panel == HELP_OVERLAY_PANEL

    def _cancel_panel_fetch(self) -> None:
        self._panel_fetch_generation += 1
        if self._panel_fetch_event is not None:
            self._panel_fetch_event.set()
        self._panel_fetching = False
        self._panel_fetch_event = None

    def _schedule_panel_fetch(self, panel_id: str) -> None:
        asyncio.create_task(self._fetch_panel(panel_id))

    async def _fetch_panel(self, panel_id: str) -> None:
        generation = self._panel_fetch_generation
        async with self._sidebar_refresh_lock:
            if generation != self._panel_fetch_generation or not self.conn.connected:
                return
            event = asyncio.Event()
            self._panel_fetch_event = event
            self._panel_fetching = True
            self._update_link_status_bar()
            try:
                self._note_outbound()
                await self.conn.send_line(panel_id)
                await asyncio.wait_for(event.wait(), timeout=15.0)
            except asyncio.TimeoutError:
                pass
            finally:
                if generation != self._panel_fetch_generation:
                    return
                self._panel_fetching = False
                if self._panel_fetch_event is event:
                    self._panel_fetch_event = None
                self._update_link_status_bar()

    def _send_panel_command(self, command: str) -> None:
        if not self.view.authenticated:
            return
        if command == HELP_OVERLAY_PANEL:
            self._toggle_help_overlay()
            return
        if not self.conn.connected:
            self._append_log(
                self.query_one("#log", RichLog),
                f"{ERR_PREFIX}未連線",
                kind="err",
            )
            return
        if command in self.view.sidebar_stack:
            toggle_sidebar_panel(self.view, command)
            self._render_sidebar()
            return
        if (
            self.view.pending_panel == command
            and command not in self.view.sidebar_stack
            and self._panel_fetching
        ):
            self._cancel_panel_fetch()
            self.view.pending_panel = ""
            if not self.view.sidebar_stack:
                self.view.sidebar_open = False
            self._render_sidebar()
            self._update_link_status_bar()
            return
        if not toggle_sidebar_panel(self.view, command):
            self._render_sidebar()
            return
        self.view.pending_panel = command
        self._render_sidebar()
        self._schedule_panel_fetch(command)

    def _apply_meta(self, payload: str) -> None:
        key, value = parse_meta_payload(payload)
        was_auth = self.view.authenticated
        old_room_id = self.view.room_id
        apply_meta(self.view, key, value)
        if key == "room_id" and should_refresh_sidebar_on_room_change(
            self.view,
            old_room_id=old_room_id,
            new_room_id=value,
        ):
            asyncio.create_task(self._refresh_sidebar_panels(panels_to_refresh_on_move(self.view)))
        if key == "auth" and value == "1":
            self._auth_pending = False
            self._needs_reauth = False
            self._reconnecting = False
            self._last_recv_at = time.monotonic()
            if not was_auth:
                self._set_auth_ui(True)
                self.query_one("#login_password", Input).value = ""
                self._clear_pin_fields()
                self._persist_credentials_if_pending()
            else:
                self._update_status()
                if self.view.sidebar_open and self.view.sidebar_stack:
                    asyncio.create_task(self._refresh_sidebar_panels(list(self.view.sidebar_stack)))
        elif key == "auth" and value == "0" and was_auth:
            self._return_to_login_screen()
        self._update_status()
        if key == "ui_panel_end":
            if self._help_panel_active():
                if HELP_OVERLAY_PANEL in self.view.sidebar_stack:
                    self.view.sidebar_stack.remove(HELP_OVERLAY_PANEL)
                self._render_help_overlay()
                if self._help_fetch_event is not None:
                    self._help_fetch_event.set()
            else:
                self._render_sidebar()
            if self._panel_fetch_event is not None:
                self._panel_fetch_event.set()
        if key in ("quest", "hint") and self.view.sidebar_open and "gigs" in self.view.sidebar_stack:
            asyncio.create_task(self._refresh_sidebar_panels(["gigs"]))
        if key == "refresh_sidebar" and value == "1" and self.view.sidebar_open:
            asyncio.create_task(self._refresh_sidebar_panels(panels_to_refresh_on_equip(self.view)))

    async def _refresh_sidebar_panels(self, panel_ids: list[str]) -> None:
        if not panel_ids or not self.conn.connected:
            return
        for panel_id in panel_ids:
            if panel_id in self.view.sidebar_stack:
                await self._fetch_panel(panel_id)

    async def action_focus_prompt(self) -> None:
        self._focus_game_prompt()

    def _apply_prompt_completion(self, prompt: Input) -> bool:
        if prompt.cursor_at_end and prompt._suggestion:
            prompt.action_cursor_right()
            return True
        current = prompt.value
        if current != self._completion_cycle_key:
            self._completion_cycle_key = current
            self._completion_cycle_index = 0
        suggestion, next_index = complete_cycle_from_view(
            self.view,
            current,
            self._completion_cycle_index,
        )
        if suggestion and suggestion != current:
            prompt.value = suggestion
            prompt.cursor_position = len(prompt.value)
            self._completion_cycle_key = current
            self._completion_cycle_index = next_index
            return True
        fallback = complete_from_view(self.view, current)
        if fallback and fallback != current:
            prompt.value = fallback
            prompt.cursor_position = len(prompt.value)
            return True
        return False

    async def action_tab_complete(self) -> None:
        if not self.view.authenticated:
            return
        prompt = self.query_one("#prompt", MudPrompt)
        if prompt.has_focus:
            self._apply_prompt_completion(prompt)
            return
        self._focus_game_prompt()

    async def action_panel_pda(self) -> None:
        self._send_panel_command("pda")

    async def action_panel_help(self) -> None:
        self._toggle_help_overlay()

    async def action_close_help_overlay(self) -> None:
        if self.view.authenticated and self._help_overlay_open:
            self._close_help_overlay()

    async def action_panel_map(self) -> None:
        self._send_panel_command("map")

    async def action_panel_equipment(self) -> None:
        self._send_panel_command("equipment")

    async def action_panel_gigs(self) -> None:
        if not self.view.authenticated:
            self.action_clear_credentials()
            return
        self._send_panel_command("gigs")

    async def action_toggle_sidebar(self) -> None:
        if not self.view.authenticated:
            return
        self._close_help_overlay()
        self._cancel_panel_fetch()
        self.view.sidebar_open = False
        self.view.sidebar_stack.clear()
        self.view.pending_panel = ""
        self._update_link_status_bar()
        self._render_sidebar()

    def on_resize(self, event: Resize) -> None:
        if not self.view.authenticated:
            self._refresh_login_art()
        else:
            self._refresh_game_layout()

    @on(Click, "#prompt_dock")
    @on(Click, "#prompt_row")
    def on_prompt_row_click(self, event: Click) -> None:
        if self.view.authenticated:
            event.stop()
            self._focus_game_prompt()

    @on(Click, "#sidebar_wrap")
    @on(Click, "#sidebar")
    def on_sidebar_click(self, event: Click) -> None:
        if self.view.authenticated:
            event.stop()
            self._focus_game_prompt()

    def on_descendant_focus(self, event: DescendantFocus) -> None:
        dock = self.query_one("#prompt_dock", Horizontal)
        if self.view.authenticated and event.widget.id == "prompt":
            dock.add_class("prompt-focused")
        elif event.widget.id != "prompt":
            dock.remove_class("prompt-focused")
        if self.view.authenticated and event.widget.id in (
            "log",
            "sidebar",
            "sidebar_content",
            "sidebar_header",
        ):
            self.call_after_refresh(self._focus_game_prompt)

    @on(Select.Changed, "#login_theme")
    def on_login_theme_changed(self, event: Select.Changed) -> None:
        if event.value:
            self._apply_theme(str(event.value))

    async def on_mount(self) -> None:
        startup = StartupReport()
        self.stylesheet_path = None
        with startup.measure("主題"):
            self._register_themes()
            saved_theme = load_theme_id()
            self._apply_theme(saved_theme, persist=False)
            try:
                self.query_one("#login_theme", Select).value = saved_theme
            except Exception:
                pass
        self._set_auth_ui(False)
        with startup.measure("登入畫面"):
            self._refresh_credential_ui()
        for widget_id in (
            "#login_title",
            "#login_hint",
            "#login_status",
            "#prompt_preview",
            "#help_dropdown_header",
            "#help_dropdown_content",
            "#info_bar",
            "#chrome_bar",
            "#hotkey_bar",
            "#sidebar_header",
            "#sidebar_content",
        ):
            try:
                self.query_one(widget_id, Static).markup = True
            except Exception:
                pass
        log = self.query_one("#log", RichLog)
        self._configure_game_focus_targets()
        self._configure_help_overlay_focus()
        self.set_interval(0.2, self._on_spinner_tick)
        self.set_interval(1.0, self._on_cd_tick)
        self.set_interval(0.5, self._on_login_motd_tick)
        self._reset_login_motd()
        try:
            with startup.measure("連線"):
                await self.conn.connect()
            self._reconnect_attempts = 0
            self._reader_task = asyncio.create_task(self._read_loop(log))
            self._startup_hint = startup.format_status()
            self._refresh_credential_ui()
        except OSError as exc:
            self._startup_hint = startup.format_status()
            self._refresh_credential_ui()
            self._set_login_status(f"無法連線：{exc}（請先執行 ./run.sh）")
            self._schedule_reconnect(log)

    def _mark_disconnected(self, *, was_authenticated: bool) -> None:
        if was_authenticated:
            self._needs_reauth = True
        self._reconnecting = True
        self._update_status()

    def _cancel_reconnect_task(self) -> None:
        if self._reconnect_task is not None and not self._reconnect_task.done():
            self._reconnect_task.cancel()

    async def _restart_reader(self, log: RichLog) -> None:
        if self._reader_task is not None:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
        self._reader_task = asyncio.create_task(self._read_loop(log))

    async def _resend_auth_if_needed(self, log: RichLog) -> None:
        if not should_resend_auth(
            needs_reauth=self._needs_reauth,
            authenticated=self.view.authenticated,
            last_auth_line=self._last_auth_line,
        ):
            return
        if self._needs_reauth and self.view.authenticated and not self._last_auth_line:
            self._needs_reauth = False
            self._reconnecting = False
            self._set_auth_ui(False)
            self._set_login_status("連線已恢復，請重新登入。")
            return
        self._auth_pending = True
        try:
            await self.conn.send_line(self._last_auth_line)
        except OSError as exc:
            self._auth_pending = False
            msg = f"重新登入失敗：{exc}"
            if self.view.authenticated:
                self._append_log(log, f"{ERR_PREFIX}{msg}", kind="err")
            else:
                self._set_login_status(msg)

    async def _perform_reconnect(self, log: RichLog, *, reset_attempts: bool) -> bool:
        if reset_attempts:
            self._cancel_reconnect_task()
            self._reconnect_attempts = 0
        self._reconnecting = True
        self._update_status()
        await self.conn.close()
        try:
            await self.conn.connect()
            self._reconnect_attempts = 0
            self._reconnecting = False
            if self.view.authenticated:
                self._append_log(log, f"{SYS_PREFIX}神經連結已恢復。", kind="sys")
            else:
                self._set_login_status("神經連結已恢復。")
                self._refresh_login_art()
            await self._restart_reader(log)
            await self._resend_auth_if_needed(log)
            self._update_status()
            return True
        except OSError as exc:
            msg = f"重連失敗：{exc}"
            if self.view.authenticated:
                self._append_log(log, f"{ERR_PREFIX}{msg}", kind="err")
            else:
                self._set_login_status(msg)
            self._schedule_reconnect(log)
            return False

    def _schedule_reconnect(self, log: RichLog) -> None:
        if self._reconnect_task is not None and not self._reconnect_task.done():
            return
        self._reconnect_attempts += 1
        delay = reconnect_delay(self._reconnect_attempts)
        msg = reconnect_status_message(
            attempt=self._reconnect_attempts,
            delay=delay,
            max_attempts=self.MAX_RECONNECT_ATTEMPTS,
        )
        if msg is None or self._reconnect_attempts > self.MAX_RECONNECT_ATTEMPTS:
            fail = "重連失敗（已達 5 次）。輸入 /reconnect 再試。"
            if self.view.authenticated:
                self._append_log(log, f"{ERR_PREFIX}{fail}", kind="err")
            else:
                self._set_login_status(fail)
            self._reconnecting = False
            self._update_status()
            return
        self._reconnecting = True
        self._update_status()
        if self.view.authenticated:
            self._append_log(log, f"{SYS_PREFIX}{msg}", kind="sys")
        else:
            self._set_login_status(msg)
        self._reconnect_task = asyncio.create_task(self._reconnect_after(delay, log))

    async def _reconnect_after(self, delay: float, log: RichLog) -> None:
        await asyncio.sleep(delay)
        await self._perform_reconnect(log, reset_attempts=False)

    async def _read_loop(self, log: RichLog) -> None:
        try:
            while self.conn.connected:
                line = await self.conn.read_line()
                if line is not None:
                    self._note_inbound()
                if line is None:
                    if self._pending_logout:
                        self._return_to_login_screen()
                        break
                    was_authenticated = self.view.authenticated
                    if self.view.authenticated:
                        self._append_log(log, f"{SYS_PREFIX}神經連結中斷。", kind="sys")
                    else:
                        self._set_login_status("神經連結中斷。")
                    self._mark_disconnected(was_authenticated=was_authenticated)
                    self._schedule_reconnect(log)
                    break
                kind = classify_server_line(line)
                if kind == "meta":
                    self._apply_meta(line[len(META_PREFIX):])
                    self._complete_command_if_pending(log)
                    continue
                if not self.view.authenticated:
                    if kind == "panel" or kind == "ui":
                        continue
                    if line.startswith(MOTD_PREFIX):
                        self._add_login_motd_tip(line[len(MOTD_PREFIX):])
                    elif line.startswith(SYS_PREFIX):
                        self._set_login_status(line[len(SYS_PREFIX):])
                    elif line.startswith(ERR_PREFIX):
                        self._set_login_status(line[len(ERR_PREFIX):])
                        self._auth_pending = False
                        self._pending_credential_save = None
                    else:
                        self._set_login_status(line)
                        self._auth_pending = False
                    continue
                if kind == "panel":
                    handle_panel_line(self.view, line[len(PANEL_PREFIX):])
                    if self._help_panel_active():
                        self._render_help_overlay()
                    else:
                        self._render_sidebar()
                    self._complete_command_if_pending(log)
                    continue
                if kind == "ui":
                    handle_ui_json(self.view, line[len(UI_PREFIX):])
                    if self._help_panel_active():
                        self._render_help_overlay()
                    else:
                        self._render_sidebar()
                    self._complete_command_if_pending(log)
                    continue
                if self._pending_logout and self.view.authenticated:
                    self._return_to_login_screen(message=line)
                    self._complete_command_if_pending(log)
                    continue
                self._append_log(log, line)
                self._complete_command_if_pending(log)
        except asyncio.CancelledError:
            raise
        finally:
            await self.conn.close()

    async def _submit_login(self, *, from_pin_unlock: bool = False) -> None:
        if self._auth_pending or self.view.authenticated:
            return
        mode_widget = self.query_one("#auth_mode", Select)
        name_widget = self.query_one("#login_name", Input)
        pass_widget = self.query_one("#login_password", Input)
        remember_widget = self.query_one("#remember_credentials", Checkbox)
        mode = str(mode_widget.value or "login")
        name = name_widget.value.strip()
        password = pass_widget.value
        if remember_widget.value and not from_pin_unlock:
            pin_setup = self.query_one("#login_pin_setup", Input).value
            pin_confirm = self.query_one("#login_pin_confirm", Input).value
            pin_err = validate_pin(pin_setup)
            if pin_err:
                self._set_login_status(pin_err)
                return
            if pin_setup != pin_confirm:
                self._set_login_status("PIN 確認不一致。")
                return
            self._pending_credential_save = (name, password, mode, pin_setup)
        else:
            self._pending_credential_save = None
        command = build_auth_command(mode, name, password)
        if command is None:
            self._pending_credential_save = None
            self._set_login_status("請輸入名稱與密碼。")
            return
        if not self.conn.connected:
            self._pending_credential_save = None
            self._set_login_status("未連線伺服器。")
            return
        self._auth_pending = True
        self._last_auth_line = command
        pass_widget.value = ""
        self._set_login_status("驗證中…")
        try:
            self._note_outbound()
            await self.conn.send_line(command)
        except OSError as exc:
            self._auth_pending = False
            self._pending_credential_save = None
            self._set_login_status(f"傳送失敗：{exc}")

    async def _submit_pin_unlock(self) -> None:
        if self._auth_pending or self.view.authenticated or not has_stored_credentials():
            return
        pin_widget = self.query_one("#login_pin", Input)
        pin = pin_widget.value
        pin_err = validate_pin(pin)
        if pin_err:
            self._set_login_status(pin_err)
            return
        creds = unlock_credentials(pin)
        if creds is None:
            self._set_login_status("PIN 錯誤。")
            return
        self.query_one("#auth_mode", Select).value = creds.mode
        self.query_one("#login_name", Input).value = creds.username
        self.query_one("#login_password", Input).value = creds.password
        pin_widget.value = ""
        await self._submit_login(from_pin_unlock=True)

    @on(Checkbox.Changed, "#remember_credentials")
    def on_remember_credentials_changed(self, event: Checkbox.Changed) -> None:
        if event.value:
            self._refresh_credential_ui()
            self.query_one("#login_pin_setup", Input).focus()
        else:
            self._pending_credential_save = None
            self._clear_pin_fields()
            self._refresh_credential_ui()

    def action_clear_credentials(self) -> None:
        if self.view.authenticated:
            return
        if not has_stored_credentials():
            self._set_login_status("沒有已儲存的帳號。")
            return
        clear_credentials()
        self._pending_credential_save = None
        self._clear_pin_fields()
        self.query_one("#remember_credentials", Checkbox).value = False
        self._refresh_credential_ui()
        self._set_login_status("已清除儲存帳號。")
        self.query_one("#login_name", Input).focus()

    @on(Input.Submitted, "#login_pin")
    async def on_login_pin_submitted(self, event: Input.Submitted) -> None:
        await self._submit_pin_unlock()

    @on(Input.Submitted, "#login_name")
    async def on_login_name_submitted(self, event: Input.Submitted) -> None:
        self.query_one("#login_password", Input).focus()

    @on(Input.Submitted, "#login_password")
    async def on_login_password_submitted(self, event: Input.Submitted) -> None:
        await self._submit_login()

    async def _handle_local_command(self, text: str, log: RichLog) -> bool:
        if not is_local_command(text):
            return False
        verb, args = parse_local_command(text)
        if verb == "quit":
            await self.action_quit()
            return True
        if verb == "reconnect":
            await self._perform_reconnect(log, reset_attempts=True)
            return True
        if verb == "prompt":
            if args.startswith("set "):
                self._local_prompt_override = args[4:]
                self._update_status()
                expanded = expand_prompt_from_view(self._local_prompt_override, self.view)
                self._append_log(log, f"本機提示符：{expanded}", kind="text")
            elif args.startswith("template "):
                name = args[9:].strip()
                template = CP2077_TEMPLATES.get(name)
                if template is None:
                    names = ", ".join(sorted(CP2077_TEMPLATES))
                    self._append_log(log, f"未知範本：{name}。可用：{names}", kind="text")
                else:
                    self._local_prompt_override = template
                    self._update_status()
                    expanded = expand_prompt_from_view(template, self.view)
                    self._append_log(log, f"已套用範本 {name}：{expanded}", kind="text")
            elif args == "reset":
                self._local_prompt_override = ""
                self._update_status()
                self._append_log(log, "本機提示符已重設（使用伺服器範本）。", kind="text")
            elif args == "show":
                for line in format_prompt_show_lines(self.view, local_override=self._local_prompt_override):
                    self._append_log(log, line, kind="text")
            else:
                self._append_log(
                    log,
                    "用法：/prompt set <範本> | /prompt template <名稱> | /prompt show | /prompt reset",
                    kind="text",
                )
            self._clear_prompt_preview()
            return True
        if verb == "theme":
            action, theme_id = parse_theme_command(args)
            if action == "list":
                self._append_log(log, format_theme_list(), kind="text")
            elif action == "set" and theme_id:
                self._apply_theme(theme_id)
                self._append_log(log, f"主題：{theme_label(theme_id)} ({theme_id})", kind="text")
            else:
                self._append_log(log, f"用法：/theme <id> | /theme list\n{format_theme_list()}", kind="text")
            return True
        return False

    @on(Input.Changed, "#prompt")
    def on_prompt_changed(self, event: Input.Changed) -> None:
        if not self.view.authenticated:
            return
        self._update_prompt_preview(event.value)

    @on(Input.Submitted, "#prompt")
    async def on_game_input(self, event: Input.Submitted) -> None:
        if not self.view.authenticated:
            return
        text = event.value.strip()
        event.input.value = ""
        self._clear_prompt_preview()
        self._command_history.reset_browse()
        if not text:
            return
        self._command_history.add(text)
        log = self.query_one("#log", RichLog)
        self._append_log(log, f"[dim]{self._prompt_prefix()}[/]{text}", kind="echo")
        if await self._handle_local_command(text, log):
            self._complete_command_if_pending(log)
            return
        if not self.conn.connected:
            self._append_log(log, f"{ERR_PREFIX}未連線", kind="err")
            self._complete_command_if_pending(log)
            return
        if self.view.net_shell:
            text, blocked = prepare_netrun_outbound(text)
            if blocked:
                self._append_log(
                    log,
                    f"{SYS_PREFIX}NETRUN 模式：可用 hack、probe、look、scan、talk、status、exit、help。",
                    kind="sys",
                )
                self._complete_command_if_pending(log)
                return
        if self._is_server_quit_command(text):
            self._pending_logout = True
        panel_id = resolve_panel_command(text)
        if panel_id == HELP_OVERLAY_PANEL:
            self._toggle_help_overlay()
            if self._help_overlay_open:
                self._log_buffer.mark_last_pending()
                self._update_spinner_accent()
                self._refresh_log_display(log, preserve_scroll=True)
            self._complete_command_if_pending(log)
            return
        if panel_id:
            prepare_sidebar_for_panel(self.view, panel_id)
            self.view.pending_panel = panel_id
            self._render_sidebar()
        self._log_buffer.mark_last_pending()
        self._update_spinner_accent()
        self._refresh_log_display(log, preserve_scroll=True)
        try:
            self._note_outbound()
            await self.conn.send_line(text)
        except OSError as exc:
            self._append_log(log, f"{ERR_PREFIX}傳送失敗：{exc}", kind="err")
            self._complete_command_if_pending(log)

    async def on_unmount(self) -> None:
        if self._reader_task is not None:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
        if self._reconnect_task is not None:
            self._reconnect_task.cancel()
        await self.conn.close()


CyberMudApp.CSS = APP_CSS