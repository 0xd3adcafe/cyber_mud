from __future__ import annotations

import asyncio

from shared.protocol import ENCODING


class ServerConnection:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    @property
    def connected(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    async def connect(self) -> None:
        self._reader, self._writer = await asyncio.open_connection(self.host, self.port)

    async def close(self) -> None:
        if self._writer is not None:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
        self._reader = None
        self._writer = None

    async def send_line(self, text: str) -> None:
        if self._writer is None:
            raise OSError("not connected")
        self._writer.write((text + "\n").encode(ENCODING))
        await self._writer.drain()

    async def read_line(self) -> str | None:
        if self._reader is None:
            return None
        data = await self._reader.readline()
        if not data:
            return None
        return data.decode(ENCODING).rstrip("\r\n")