from __future__ import annotations

import asyncio

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, RichLog, Static

from client.connection import ServerConnection
from client.meta_handlers import (
    ClientViewState,
    apply_meta,
    classify_server_line,
    handle_panel_line,
    handle_ui_json,
    hint_text,
    is_local_command,
    parse_local_command,
    parse_meta_payload,
    reconnect_delay,
    status_text,
)
from shared.protocol import ERR_PREFIX, META_PREFIX, MOTD_PREFIX, PANEL_PREFIX, SYS_PREFIX, UI_PREFIX


PANEL_COMMANDS = {
    "f2": "pda",
    "f3": "help",
    "f4": "map",
    "f5": "equipment",
}


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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
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
        if self._local_prompt_override:
            return self._local_prompt_override
        prompt = self.view.prompt_mud.strip()
        return prompt if prompt else "> "

    def _hint_line(self) -> str:
        return hint_text(self.view)

    def _update_status(self) -> None:
        self.query_one("#status", Static).update(self._status_line())
        self.query_one("#hint_bar", Static).update(self._hint_line())
        self.query_one("#prompt_prefix", Static).update(self._prompt_prefix())

    def _render_sidebar(self) -> None:
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
        apply_meta(self.view, key, value)
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
        self.view.sidebar_open = not self.view.sidebar_open
        if self.view.sidebar_open and self.view.sidebar_panel:
            await self._refresh_panel()
        self._render_sidebar()

    async def on_mount(self) -> None:
        self.stylesheet_path = None
        log = self.query_one("#log", RichLog)
        try:
            await self.conn.connect()
            self._reconnect_attempts = 0
            self._reader_task = asyncio.create_task(self._read_loop(log))
        except OSError as exc:
            log.write(f"[bold red]{ERR_PREFIX}無法連線：{exc}[/]")
            log.write("[dim]請先執行 ./run.sh 啟動伺服器。[/]")
            self._schedule_reconnect(log)

    def _schedule_reconnect(self, log: RichLog) -> None:
        if self._reconnect_task is not None and not self._reconnect_task.done():
            return
        if self._reconnect_attempts >= 5:
            log.write(f"[red]{ERR_PREFIX}重連失敗（已達 5 次）。[/]")
            return
        self._reconnect_attempts += 1
        delay = reconnect_delay(self._reconnect_attempts)
        log.write(f"[yellow]{SYS_PREFIX}{delay:.0f}s 後重連（第 {self._reconnect_attempts} 次）…[/]")
        self._reconnect_task = asyncio.create_task(self._reconnect_after(delay, log))

    async def _reconnect_after(self, delay: float, log: RichLog) -> None:
        await asyncio.sleep(delay)
        try:
            await self.conn.connect()
            self._reconnect_attempts = 0
            log.write(f"[green]{SYS_PREFIX}神經連結已恢復。[/]")
            if self._reader_task is not None:
                self._reader_task.cancel()
                try:
                    await self._reader_task
                except asyncio.CancelledError:
                    pass
            self._reader_task = asyncio.create_task(self._read_loop(log))
            if self._last_auth_line:
                await self.conn.send_line(self._last_auth_line)
        except OSError as exc:
            log.write(f"[red]{ERR_PREFIX}重連失敗：{exc}[/]")
            self._schedule_reconnect(log)

    async def _read_loop(self, log: RichLog) -> None:
        try:
            while self.conn.connected:
                line = await self.conn.read_line()
                if line is None:
                    log.write(f"[yellow]{SYS_PREFIX}神經連結中斷。[/]")
                    self._schedule_reconnect(log)
                    break
                kind = classify_server_line(line)
                if kind == "meta":
                    self._apply_meta(line[len(META_PREFIX):])
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
                log.write(f"[green]{SYS_PREFIX}已重新連線。[/]")
                if self._reader_task is not None:
                    self._reader_task.cancel()
                self._reader_task = asyncio.create_task(self._read_loop(log))
                if self._last_auth_line:
                    await self.conn.send_line(self._last_auth_line)
            except OSError as exc:
                log.write(f"[red]{ERR_PREFIX}重連失敗：{exc}[/]")
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
    async def on_input(self, event: Input.Submitted) -> None:
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
        if text.lower().startswith(("login ", "register ")):
            self._last_auth_line = text
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