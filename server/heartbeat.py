from __future__ import annotations

import asyncio
import sys
import time
from typing import TYPE_CHECKING

from shared.i18n import t
from shared.server_locale import server_locale

if TYPE_CHECKING:
    from server.game import Game

HEARTBEAT_PAD = 120


def _format_uptime(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h{minutes:02d}m"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


def format_heartbeat(game: Game, *, started_at: float, dev: bool = False, locale: str | None = None) -> str:
    loc = locale or server_locale()
    state = game.state
    clock = state.clock.format_clock(loc)
    period = state.clock.format_period(loc, state.time_config)
    sessions = len(game.sessions)
    players = len(game.all_named_players())
    combats = len(state.encounters)
    corpses = len(state.corpses)
    respawns = len(state.npc_respawns)
    uptime = _format_uptime(time.monotonic() - started_at)
    dev_tag = t(loc, "server.dev_tag") if dev else ""
    return t(
        loc,
        "server.heartbeat",
        tick=str(state.tick_count),
        clock=clock,
        period=period,
        players=str(players),
        sessions=str(sessions),
        combats=str(combats),
        corpses=str(corpses),
        respawns=str(respawns),
        uptime=uptime,
        dev=dev_tag,
    )


def write_heartbeat(line: str) -> None:
    sys.stdout.write(f"\r{line[:HEARTBEAT_PAD].ljust(HEARTBEAT_PAD)}")
    sys.stdout.flush()


def log_server_event(message: str) -> None:
    sys.stdout.write(f"\n{message}\n")
    sys.stdout.flush()


async def heartbeat_loop(
    game: Game,
    *,
    interval: float,
    started_at: float,
    dev: bool = False,
) -> None:
    try:
        while True:
            write_heartbeat(format_heartbeat(game, started_at=started_at, dev=dev))
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        sys.stdout.write("\n")
        sys.stdout.flush()
        raise