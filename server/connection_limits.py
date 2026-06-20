from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.game import ClientSession, Game

MAX_CONNECTIONS_PER_IP = int(os.environ.get("CYBER_MUD_MAX_CONNECTIONS_PER_IP", "3"))
GUEST_IDLE_SECONDS = int(os.environ.get("CYBER_MUD_GUEST_IDLE_SECONDS", "600"))
AUTH_IDLE_SECONDS = int(os.environ.get("CYBER_MUD_AUTH_IDLE_SECONDS", "1800"))


def peer_ip(writer: object) -> str:
    peer = getattr(writer, "get_extra_info", lambda _name: None)("peername")
    if peer:
        return str(peer[0])
    return "unknown"


def count_connections_for_ip(game: Game, ip: str) -> int:
    return sum(1 for session in game.sessions if session.peer_ip == ip)


def can_accept_connection(game: Game, ip: str) -> bool:
    if ip == "unknown":
        return True
    return count_connections_for_ip(game, ip) < MAX_CONNECTIONS_PER_IP


def idle_timeout_seconds(session: ClientSession) -> int:
    if session.player.named:
        return AUTH_IDLE_SECONDS
    return GUEST_IDLE_SECONDS


def session_idle_seconds(session: ClientSession, *, now: float | None = None) -> float:
    current = time.monotonic() if now is None else now
    return current - session.last_activity_at


def is_idle(session: ClientSession, *, now: float | None = None) -> bool:
    return session_idle_seconds(session, now=now) >= idle_timeout_seconds(session)