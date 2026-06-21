from __future__ import annotations

from client.link_status import LinkSnapshot, classify_link
from client.meta_handlers import ClientViewState
from client.output_prefix import spinner_char
from client.ui_format import format_status_markup
from shared.i18n import t

_RELEVANT_LINK_STATES = frozenset({"waiting", "slow", "panel", "disconnected"})


def _format_link_chip(snapshot: LinkSnapshot, *, locale: str, frame: int = 0) -> str:
    state = classify_link(snapshot)
    spin = spinner_char(frame)
    if state == "waiting":
        return f"[cyan]{spin} {t(locale, 'client.link.waiting')}[/]"
    if state == "slow":
        rtt = (
            f" {int(snapshot.last_rtt_ms)}ms"
            if snapshot.last_rtt_ms is not None
            else ""
        )
        return f"[yellow]● {t(locale, 'client.link.slow')}{rtt}[/]"
    if state == "panel":
        return f"[cyan]{spin} {t(locale, 'client.link.panel')}[/]"
    if state == "disconnected":
        return f"[red]● {t(locale, 'client.link.disconnected')}[/]"
    return ""


def format_status_strip(
    state: ClientViewState,
    *,
    snapshot: LinkSnapshot,
    host: str,
    port: int,
    frame: int = 0,
) -> str:
    """Merged #info_bar + contextual #chrome_bar link chip (CU.1 prep)."""
    locale = state.locale or "en"
    base = format_status_markup(
        state,
        host=host,
        port=port,
        reconnecting=snapshot.reconnecting,
        spinner_frame=frame,
    )
    if snapshot.reconnecting:
        return base
    link_state = classify_link(snapshot)
    if link_state not in _RELEVANT_LINK_STATES:
        return base
    chip = _format_link_chip(snapshot, locale=locale, frame=frame)
    if not chip:
        return base
    return f"{base}  [dim]│[/]  {chip}"