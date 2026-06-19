from __future__ import annotations

import asyncio
from pathlib import Path

from server.game import Game

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WATCH_GLOB = ("*.yaml",)


def _snapshot_mtimes() -> dict[Path, float]:
    mtimes: dict[Path, float] = {}
    for pattern in WATCH_GLOB:
        for path in DATA_DIR.glob(pattern):
            if path.is_file():
                mtimes[path] = path.stat().st_mtime
    locale_dir = DATA_DIR / "locale"
    if locale_dir.is_dir():
        for path in locale_dir.glob("*.yaml"):
            mtimes[path] = path.stat().st_mtime
    return mtimes


async def start_dev_watcher(game: Game, *, interval: float = 1.0) -> None:
    mtimes = _snapshot_mtimes()
    try:
        while True:
            await asyncio.sleep(interval)
            current = _snapshot_mtimes()
            if current != mtimes:
                mtimes = current
                game.reload_world_data()
    except asyncio.CancelledError:
        raise