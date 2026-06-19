from __future__ import annotations

import asyncio

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Input, RichLog, Static

from client.connection import ServerConnection
from shared.protocol import ERR_PREFIX, META_PREFIX, MOTD_PREFIX, SYS_PREFIX


class CyberMudApp(App):
    TITLE = "cyber_mud"
    SUB_TITLE = "夜城神經連結"

    BINDINGS = [
        Binding("ctrl+c", "quit", "離開"),
    ]

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.conn = ServerConnection(host, port)
        self._reader_task: asyncio.Task | None = None
        self._room = "—"
        self._hp = "—"
        self._gold = "—"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(self._status_text(), id="status")
        yield RichLog(id="log", highlight=True, markup=True)
        with Horizontal(id="prompt_row"):
            yield Static("> ", id="prompt_prefix")
            yield Input(placeholder="輸入指令…", id="prompt")
        yield Footer()

    def _status_text(self) -> str:
        return f"  房間 {self._room}  │  HP {self._hp}  │  ${self._gold}  │  {self.host}:{self.port}"

    def _update_status(self) -> None:
        self.query_one("#status", Static).update(self._status_text())

    def _apply_meta(self, payload: str) -> None:
        key, _, value = payload.partition("=")
        if key == "room":
            self._room = value
        elif key == "hp":
            self._hp = value
        elif key == "gold":
            self._gold = value
        self._update_status()

    async def on_mount(self) -> None:
        log = self.query_one("#log", RichLog)
        try:
            await self.conn.connect()
            self._reader_task = asyncio.create_task(self._read_loop(log))
        except OSError as exc:
            log.write(f"[bold red]{ERR_PREFIX}無法連線：{exc}[/]")
            log.write("[dim]請先執行 ./run.sh 啟動伺服器。[/]")

    async def _read_loop(self, log: RichLog) -> None:
        try:
            while self.conn.connected:
                line = await self.conn.read_line()
                if line is None:
                    log.write(f"[yellow]{SYS_PREFIX}神經連結中斷。[/]")
                    break
                if line.startswith(META_PREFIX):
                    self._apply_meta(line[len(META_PREFIX):])
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

    @on(Input.Submitted, "#prompt")
    async def on_input(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        event.input.value = ""
        if not text:
            return
        log = self.query_one("#log", RichLog)
        log.write(f"[dim]> {text}[/]")
        if not self.conn.connected:
            log.write(f"[red]{ERR_PREFIX}未連線[/]")
            return
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
        await self.conn.close()