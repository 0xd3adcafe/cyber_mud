from __future__ import annotations

import time
from dataclasses import dataclass

from client.output_prefix import spinner_char

SLOW_RTT_MS = 800.0
STALE_RECV_S = 12.0
WAITING_SEND_S = 2.0


@dataclass(frozen=True)
class LinkSnapshot:
    connected: bool
    reconnecting: bool
    command_pending: bool
    panel_fetching: bool
    auth_pending: bool = False
    last_rtt_ms: float | None = None
    last_recv_at: float = 0.0
    last_send_at: float = 0.0
    now: float = 0.0


def _age_seconds(snapshot: LinkSnapshot, ts: float) -> float | None:
    if ts <= 0:
        return None
    return max(0.0, snapshot.now - ts)


def classify_link(snapshot: LinkSnapshot) -> str:
    if snapshot.reconnecting:
        return "reconnecting"
    if not snapshot.connected:
        return "disconnected"
    if snapshot.panel_fetching:
        return "panel"
    if snapshot.command_pending or snapshot.auth_pending:
        recv_age = _age_seconds(snapshot, snapshot.last_recv_at)
        send_age = _age_seconds(snapshot, snapshot.last_send_at)
        if snapshot.last_rtt_ms is not None and snapshot.last_rtt_ms >= SLOW_RTT_MS:
            return "slow"
        if send_age is not None and send_age >= WAITING_SEND_S:
            if recv_age is None or recv_age > send_age:
                return "slow"
        return "waiting"
    recv_age = _age_seconds(snapshot, snapshot.last_recv_at)
    if recv_age is not None and recv_age >= STALE_RECV_S:
        return "idle"
    return "ok"


def _format_age(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    if seconds < 1.0:
        return f"{int(seconds * 1000)}ms前"
    if seconds < 60.0:
        return f"{seconds:.1f}s前"
    return f"{int(seconds // 60)}m前"


def _endpoint_label(host: str, port: int) -> str:
    if not host:
        return ""
    if port:
        return f"{host}:{port}"
    return host


def format_link_status_bar(
    snapshot: LinkSnapshot,
    *,
    frame: int = 0,
    host: str = "",
    port: int = 0,
) -> str:
    state = classify_link(snapshot)
    recv_age = _age_seconds(snapshot, snapshot.last_recv_at)
    send_age = _age_seconds(snapshot, snapshot.last_send_at)
    spin = spinner_char(frame)
    header = "[bold cyan]連線[/]"
    endpoint = _endpoint_label(host, port)
    endpoint_part = f"  [dim]│[/]  [dim]{endpoint}[/]" if endpoint else ""

    if state == "reconnecting":
        return f"{header}  [yellow]{spin}[/] [yellow]重連中…[/]  [dim]│[/]  [dim]等待伺服器恢復[/]"
    if state == "disconnected":
        return f"{header}  [red]●[/] [red]未連線[/]  [dim]│[/]  [dim]/reconnect 手動重連[/]"
    if state == "panel":
        return (
            f"{header}  [cyan]{spin}[/] [cyan]載入側欄…[/]"
            f"  [dim]│[/]  [dim]已送 {_format_age(send_age)}[/]"
        )
    if state == "waiting":
        rtt = f"  [dim]│[/]  [cyan]{int(snapshot.last_rtt_ms)}ms[/]" if snapshot.last_rtt_ms else ""
        return (
            f"{header}  [cyan]{spin}[/] [cyan]等待回應…[/]"
            f"{rtt}  [dim]│[/]  [dim]已送 {_format_age(send_age)}[/]"
        )
    if state == "slow":
        rtt = f"{int(snapshot.last_rtt_ms)}ms" if snapshot.last_rtt_ms else "偏慢"
        return (
            f"{header}  [yellow]●[/] [yellow]回應偏慢[/]"
            f"  [dim]│[/]  [yellow]{rtt}[/]"
            f"  [dim]│[/]  [dim]已送 {_format_age(send_age)}[/]"
        )
    if state == "idle":
        return (
            f"{header}  [green]●[/] [green]正常[/]"
            f"{endpoint_part}"
            f"  [dim]│[/]  [dim]{_format_age(recv_age)}[/]"
        )
    rtt_part = ""
    if snapshot.last_rtt_ms is not None:
        rtt_part = f"  [dim]│[/]  [cyan]{int(snapshot.last_rtt_ms)}ms[/]"
    return (
        f"{header}  [green]●[/] [green]順暢[/]"
        f"{endpoint_part}"
        f"{rtt_part}"
    )


def make_link_snapshot(
    *,
    connected: bool,
    reconnecting: bool,
    command_pending: bool,
    panel_fetching: bool,
    auth_pending: bool = False,
    last_rtt_ms: float | None = None,
    last_recv_at: float = 0.0,
    last_send_at: float = 0.0,
) -> LinkSnapshot:
    return LinkSnapshot(
        connected=connected,
        reconnecting=reconnecting,
        command_pending=command_pending,
        panel_fetching=panel_fetching,
        auth_pending=auth_pending,
        last_rtt_ms=last_rtt_ms,
        last_recv_at=last_recv_at,
        last_send_at=last_send_at,
        now=time.monotonic(),
    )