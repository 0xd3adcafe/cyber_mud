from __future__ import annotations

import asyncio
from pathlib import Path

from server.code_reload import reload_application_code, snapshot_code_mtimes
from server.game import Game

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_GLOB = ("*.yaml",)


def _snapshot_data_mtimes() -> dict[Path, float]:
    mtimes: dict[Path, float] = {}
    for pattern in DATA_GLOB:
        for path in DATA_DIR.glob(pattern):
            if path.is_file():
                mtimes[path] = path.stat().st_mtime
    locale_dir = DATA_DIR / "locale"
    if locale_dir.is_dir():
        for path in locale_dir.glob("*.yaml"):
            mtimes[path] = path.stat().st_mtime
    return mtimes


async def start_dev_watcher(game: Game, *, interval: float = 1.0) -> None:
    data_mtimes = _snapshot_data_mtimes()
    code_mtimes = snapshot_code_mtimes()
    try:
        while True:
            await asyncio.sleep(interval)
            current_data = _snapshot_data_mtimes()
            if current_data != data_mtimes:
                data_mtimes = current_data
                game.reload_world_data()
                await game.notify_dev_reload("data")
            current_code = snapshot_code_mtimes()
            if current_code != code_mtimes:
                code_mtimes = current_code
                failures = reload_application_code()
                await game.notify_dev_reload("code", failures=failures)
    except asyncio.CancelledError:
        raise