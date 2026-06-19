from __future__ import annotations

import asyncio

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.events import Resize
from textual.widgets import Footer, Header, Input, RichLog, Select, Static

from client.auth_ui import build_auth_command
from client.connection import ServerConnection
from client.login_art import render_login_art
from client.meta_handlers import (
    ClientViewState,
    active_prompt,
    apply_meta,
    classify_server_line,
    handle_panel_line,
    handle_ui_json,
    hint_text,
    is_local_command,
    is_netrun_exit_command,
    netrun_blocks_server_command,
    parse_local_command,
    parse_meta_payload,
    reconnect_delay,
    status_text,
)
from shared.protocol import ERR_PREFIX, META_PREFIX, MOTD_PREFIX, PANEL_PREFIX, SYS_PREFIX, UI_PREFIX


class CyberMudApp(App):
    TITLE = "cyber_mud"
    SUB_TITLE = "夜城神經連結"

    BINDINGS = [
        Binding("ctrl+c", "quit", "離開"),
        Binding("f2", "panel_pda", "PDA", show=True),
        Binding("f3", "panel_help", "說明", show=True),
        Binding("f4", "panel_map", "地圖", show=True),
        Binding("f5", "panel_equipment", "裝備", show=True),
        Binding("f6", "toggle_sidebar", "側欄", show=True),
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
        self._last_auth_line = ""
        self._local_prompt_override = ""
        self._auth_pending = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(id="login_container"):
            yield Static("", id="login_art")
            with Vertical(id="login_form"):
                yield Static("◈ 夜城神經連結", id="login_title")
                yield Select(
                    (("登入既有帳號", "login"), ("註冊新帳號", "register")),
                    id="auth_mode",
                    value="login",
                    allow_blank=False,
                )
                yield Input(placeholder="使用者名稱", id="login_name")
                yield Input(placeholder="密碼", id="login_password", password=True)
                yield Static("Enter 送出", id="login_hint")
                yield Static("", id="login_status")

        with Container(id="game_container", classes="game-hidden"):
            yield Static(self._status_line(), id="status")
            yield Static("", id="hint_bar")
            with Horizontal(id="main_row"):
                yield RichLog(id="log", highlight=True, markup=True)
                yield Static("", id="sidebar", classes="sidebar-hidden")
            with Horizontal(id="prompt_row"):
                yield Static(self._prompt_prefix(), id="prompt_prefix")
                yield Input(placeholder="輸入指令…", id="prompt")

        yield Footer()

    def _status_line(self) -> str:
        return status_text(self.view, host=self.host, port=self.port)

    def _prompt_prefix(self) -> str:
        return active_prompt(self.view, local_override=self._local_prompt_override)

    def _hint_line(self) -> str:
        return hint_text(self.view)

    def _login_art_rows(self) -> int:
        return max(6, self.size.height // 2)

    def _refresh_login_art(self) -> None:
        art = render_login_art(self._login_art_rows())
        self.query_one("#login_art", Static).update(art)

    def _set_login_status(self, text: str) -> None:
        self.query_one("#login_status", Static).update(text)

    def _set_auth_ui(self, authenticated: bool) -> None:
        self.view.authenticated = authenticated
        login = self.query_one("#login_container")
        game = self.query_one("#game_container")
        if authenticated:
            login.add_class("login-hidden")
            game.remove_class("game-hidden")
            self._update_status()
            self.query_one("#prompt", Input).focus()
        else:
            login.remove_class("login-hidden")
            game.add_class("game-hidden")
            self._refresh_login_art()
            self.query_one("#login_name", Input).focus()

    def _update_status(self) -> None:
        if not self.view.authenticated:
            return
        self.query_one("#status", Static).update(self._status_line())
        self.query_one("#hint_bar", Static).update(self._hint_line())
        self.query_one("#prompt_prefix", Static).update(self._prompt_prefix())

    def _render_sidebar(self) -> None:
        if not self.view.authenticated:
            return
        sidebar = self.query_one("#sidebar", Static)
        if not self.view.sidebar_open:
            sidebar.update("")
            sidebar.remove_class("sidebar-visible")
            sidebar.add_class("sidebar-hidden")
            return
        lines = list(self.view.sidebar_lines)
        if self.view.sidebar_ui:
            title = self.view.sidebar_ui.get("title", self.view.sidebar_panel)
            lines.insert(0, f"[bold]{title}[/]")
            for section in self.view.sidebar_ui.get("sections", []):
                if section.get("kind") == "row":
                    lines.append(f"{section.get('label', '')}: {section.get('value', '')}")
                elif section.get("kind") == "list":
                    if section.get("title"):
                        lines.append(str(section["title"]))
                    for item in section.get("items", []):
                        lines.append(f"  • {item}")
        if not lines:
            lines = [f"◈ {self.view.sidebar_panel}"]
        sidebar.update("\n".join(lines))
        sidebar.remove_class("sidebar-hidden")
        sidebar.add_class("sidebar-visible")

    def _apply_meta(self, payload: str) -> None:
        key, value = parse_meta_payload(payload)
        was_auth = self.view.authenticated
        apply_meta(self.view, key, value)
        if key == "auth" and value == "1" and not was_auth:
            self._auth_pending = False
            self._set_auth_ui(True)
            self.query_one("#login_password", Input).value = ""
        self._update_status()
        if key == "ui_panel_end":
            self._render_sidebar()
        if key == "refresh_sidebar" and value == "1" and self.view.sidebar_open:
            asyncio.create_task(self._refresh_panel())

    async def _refresh_panel(self) -> None:
        if not self.view.sidebar_panel or not self.conn.connected:
            return
        await self.conn.send_line(self.view.sidebar_panel)

    async def _send_panel_command(self, command: str) -> None:
        if not self.view.authenticated:
            return
        if not self.conn.connected:
            self.query_one("#log", RichLog).write(f"[red]{ERR_PREFIX}未連線[/]")
            return
        self.view.sidebar_panel = command
        await self.conn.send_line(command)

    async def action_panel_pda(self) -> None:
        await self._send_panel_command("pda")

    async def action_panel_help(self) -> None:
        await self._send_panel_command("help")

    async def action_panel_map(self) -> None:
        await self._send_panel_command("map")

    async def action_panel_equipment(self) -> None:
        await self._send_panel_command("equipment")

    async def action_toggle_sidebar(self) -> None:
        if not self.view.authenticated:
            return
        self.view.sidebar_open = not self.view.sidebar_open
        if self.view.sidebar_open and self.view.sidebar_panel:
            await self._refresh_panel()
        self._render_sidebar()

    def on_resize(self, event: Resize) -> None:
        if not self.view.authenticated:
            self._refresh_login_art()

    async def on_mount(self) -> None:
        self.stylesheet_path = None
        self._set_auth_ui(False)
        self._refresh_login_art()
        log = self.query_one("#log", RichLog)
        try:
            await self.conn.connect()
            self._reconnect_attempts = 0
            self._reader_task = asyncio.create_task(self._read_loop(log))
        except OSError as exc:
            self._set_login_status(f"無法連線：{exc}（請先執行 ./run.sh）")
            self._schedule_reconnect(log)

    def _schedule_reconnect(self, log: RichLog) -> None:
        if self._reconnect_task is not None and not self._reconnect_task.done():
            return
        if self._reconnect_attempts >= 5:
            msg = "重連失敗（已達 5 次）。"
            if self.view.authenticated:
                log.write(f"[red]{ERR_PREFIX}{msg}[/]")
            else:
                self._set_login_status(msg)
            return
        self._reconnect_attempts += 1
        delay = reconnect_delay(self._reconnect_attempts)
        msg = f"{delay:.0f}s 後重連（第 {self._reconnect_attempts} 次）…"
        if self.view.authenticated:
            log.write(f"[yellow]{SYS_PREFIX}{msg}[/]")
        else:
            self._set_login_status(msg)
        self._reconnect_task = asyncio.create_task(self._reconnect_after(delay, log))

    async def _reconnect_after(self, delay: float, log: RichLog) -> None:
        await asyncio.sleep(delay)
        try:
            await self.conn.connect()
            self._reconnect_attempts = 0
            if self.view.authenticated:
                log.write(f"[green]{SYS_PREFIX}神經連結已恢復。[/]")
            else:
                self._set_login_status("神經連結已恢復。")
                self._refresh_login_art()
            if self._reader_task is not None:
                self._reader_task.cancel()
                try:
                    await self._reader_task
                except asyncio.CancelledError:
                    pass
            self._reader_task = asyncio.create_task(self._read_loop(log))
            if self._last_auth_line and not self.view.authenticated:
                await self.conn.send_line(self._last_auth_line)
        except OSError as exc:
            msg = f"重連失敗：{exc}"
            if self.view.authenticated:
                log.write(f"[red]{ERR_PREFIX}{msg}[/]")
            else:
                self._set_login_status(msg)
            self._schedule_reconnect(log)

    async def _read_loop(self, log: RichLog) -> None:
        try:
            while self.conn.connected:
                line = await self.conn.read_line()
                if line is None:
                    if self.view.authenticated:
                        log.write(f"[yellow]{SYS_PREFIX}神經連結中斷。[/]")
                    else:
                        self._set_login_status("神經連結中斷。")
                    self._schedule_reconnect(log)
                    break
                kind = classify_server_line(line)
                if kind == "meta":
                    self._apply_meta(line[len(META_PREFIX):])
                    continue
                if not self.view.authenticated:
                    if kind == "panel" or kind == "ui":
                        continue
                    if line.startswith(MOTD_PREFIX):
                        self._set_login_status(line[len(MOTD_PREFIX):])
                    elif line.startswith(SYS_PREFIX):
                        self._set_login_status(line[len(SYS_PREFIX):])
                    elif line.startswith(ERR_PREFIX):
                        self._set_login_status(line[len(ERR_PREFIX):])
                    else:
                        self._set_login_status(line)
                        self._auth_pending = False
                    continue
                if kind == "panel":
                    handle_panel_line(self.view, line[len(PANEL_PREFIX):])
                    self._render_sidebar()
                    continue
                if kind == "ui":
                    handle_ui_json(self.view, line[len(UI_PREFIX):])
                    self._render_sidebar()
                    continue
                if line.startswith(MOTD_PREFIX):
                    log.write(f"[cyan]{line}[/]")
                elif line.startswith(SYS_PREFIX):
                    log.write(f"[yellow]{line}[/]")
                elif line.startswith(ERR_PREFIX):
                    log.write(f"[red]{line}[/]")
                else:
                    log.write(line)
        except asyncio.CancelledError:
            raise
        finally:
            await self.conn.close()

    async def _submit_login(self) -> None:
        if self._auth_pending or self.view.authenticated:
            return
        mode_widget = self.query_one("#auth_mode", Select)
        name_widget = self.query_one("#login_name", Input)
        pass_widget = self.query_one("#login_password", Input)
        mode = str(mode_widget.value or "login")
        name = name_widget.value.strip()
        password = pass_widget.value
        command = build_auth_command(mode, name, password)
        if command is None:
            self._set_login_status("請輸入名稱與密碼。")
            return
        if not self.conn.connected:
            self._set_login_status("未連線伺服器。")
            return
        self._auth_pending = True
        self._last_auth_line = command
        pass_widget.value = ""
        self._set_login_status("驗證中…")
        try:
            await self.conn.send_line(command)
        except OSError as exc:
            self._auth_pending = False
            self._set_login_status(f"傳送失敗：{exc}")

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
            await self.conn.close()
            self._reconnect_attempts = 0
            try:
                await self.conn.connect()
                if self.view.authenticated:
                    log.write(f"[green]{SYS_PREFIX}已重新連線。[/]")
                else:
                    self._set_login_status("已重新連線。")
                if self._reader_task is not None:
                    self._reader_task.cancel()
                self._reader_task = asyncio.create_task(self._read_loop(log))
                if self._last_auth_line and not self.view.authenticated:
                    await self.conn.send_line(self._last_auth_line)
            except OSError as exc:
                msg = f"重連失敗：{exc}"
                if self.view.authenticated:
                    log.write(f"[red]{ERR_PREFIX}{msg}[/]")
                else:
                    self._set_login_status(msg)
            return True
        if verb == "prompt":
            if args.startswith("set "):
                self._local_prompt_override = args[4:]
                self._update_status()
                log.write(f"[dim]本機提示符：{self._local_prompt_override}[/]")
            elif args == "show":
                log.write(f"[dim]本機提示符：{self._local_prompt_override or '(伺服器)'}[/]")
            else:
                log.write("[dim]用法：/prompt set <範本> | /prompt show[/]")
            return True
        return False

    @on(Input.Submitted, "#prompt")
    async def on_game_input(self, event: Input.Submitted) -> None:
        if not self.view.authenticated:
            return
        text = event.value.strip()
        event.input.value = ""
        if not text:
            return
        log = self.query_one("#log", RichLog)
        log.write(f"[dim]{self._prompt_prefix()}{text}[/]")
        if await self._handle_local_command(text, log):
            return
        if not self.conn.connected:
            log.write(f"[red]{ERR_PREFIX}未連線[/]")
            return
        if self.view.net_shell:
            if netrun_blocks_server_command(text):
                log.write(f"[yellow]{SYS_PREFIX}NETRUN 模式：請輸入 exit 或 /exit 離開駭入層。[/]")
                return
            if text.startswith("/") and is_netrun_exit_command(text):
                text = text[1:].strip().split()[0]
        try:
            await self.conn.send_line(text)
        except OSError as exc:
            log.write(f"[red]{ERR_PREFIX}傳送失敗：{exc}[/]")

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


CyberMudApp.CSS = """
#login_container {
    height: 1fr;
}
.login-hidden {
    display: none;
}
#login_art {
    height: 50%;
    width: 100%;
    content-align: center middle;
    text-align: center;
    color: $accent;
    background: $surface;
    overflow: hidden;
}
#login_form {
    height: 1fr;
    padding: 1 2;
    background: $panel;
}
#login_title {
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}
#login_hint {
    color: $text-muted;
    margin-top: 1;
}
#login_status {
    color: $warning;
    margin-top: 1;
    height: auto;
}
#auth_mode {
    margin-bottom: 1;
}
#login_name {
    margin-bottom: 1;
}
#game_container {
    height: 1fr;
}
.game-hidden {
    display: none;
}
#main_row {
    height: 1fr;
}
#log {
    width: 1fr;
}
#sidebar {
    width: 36;
    border: solid $accent;
    padding: 1;
    overflow-y: auto;
}
.sidebar-hidden {
    display: none;
}
.sidebar-visible {
    display: block;
}
#hint_bar {
    height: 1;
    background: $surface;
    color: $warning;
    padding: 0 1;
}
#status {
    height: 1;
    background: $primary-background;
    padding: 0 1;
}
"""