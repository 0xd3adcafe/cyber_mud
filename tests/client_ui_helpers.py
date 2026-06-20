from __future__ import annotations

import asyncio
from contextlib import suppress

from textual.dom import DOMNode
from textual.pilot import Pilot


class _FakeReader:
    def __init__(self) -> None:
        self._wait = asyncio.Event()

    async def readline(self) -> str | None:
        await self._wait.wait()
        return None


class _FakeWriter:
    def is_closing(self) -> bool:
        return False

    def close(self) -> None:
        return None

    async def wait_closed(self) -> None:
        return None

    def write(self, data: bytes) -> None:
        return None

    async def drain(self) -> None:
        return None


async def fake_connected(app) -> None:
    """Mark ServerConnection as connected without a live TCP socket (headless tests)."""
    if app._reconnect_task is not None and not app._reconnect_task.done():
        app._reconnect_task.cancel()
        with suppress(asyncio.CancelledError):
            await app._reconnect_task
        app._reconnect_task = None
    if app._reader_task is not None and not app._reader_task.done():
        app._reader_task.cancel()
        with suppress(asyncio.CancelledError):
            await app._reader_task
        app._reader_task = None
    app._reconnecting = False
    app.conn._reader = _FakeReader()
    app.conn._writer = _FakeWriter()


async def settle_layout(pilot: Pilot, *, rounds: int = 4, delay: float = 0.02) -> None:
    for _ in range(rounds):
        await pilot.pause(delay=delay)


async def wait_for_class(
    widget: DOMNode,
    class_name: str,
    pilot: Pilot,
    *,
    present: bool = True,
    attempts: int = 10,
    delay: float = 0.02,
) -> None:
    for _ in range(attempts):
        await settle_layout(pilot, rounds=1, delay=delay)
        if (class_name in widget.classes) == present:
            return
    assert (class_name in widget.classes) == present


def scroll_covers_log(scroll: DOMNode, log_wrap: DOMNode, *, margin: int = 8) -> bool:
    return scroll.region.width >= log_wrap.region.width - margin