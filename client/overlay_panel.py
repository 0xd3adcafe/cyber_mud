from __future__ import annotations

from client.meta_handlers import ClientViewState
from shared.i18n import t

OVERLAY_TAB_NETRUN = "netrun"
OVERLAY_TAB_HELP = "help"

# Tab id constants (OverlayTab); values: "netrun" | "help"
OverlayTab = str

NETRUN_HUD_COMMANDS: tuple[str, ...] = (
    "connect",
    "breach",
    "exploit",
    "probe",
    "route",
    "cat",
    "cover",
    "exit",
)

_TRACE_BAR_WIDTH = 10
_TRACE_CRITICAL = 80


def _parse_trace(trace: str | int, *, max_trace: int = 100) -> int:
    try:
        value = int(trace)
    except (TypeError, ValueError):
        value = 0
    return max(0, min(max_trace, value))


def format_trace_bar(trace: str | int, max_trace: int = 100) -> str:
    """Block-style trace meter; critical tint at >= 80%."""
    value = _parse_trace(trace, max_trace=max_trace)
    filled = int(round(value / max_trace * _TRACE_BAR_WIDTH)) if max_trace else 0
    filled = max(0, min(_TRACE_BAR_WIDTH, filled))
    bar = ("█" * filled) + ("░" * (_TRACE_BAR_WIDTH - filled))
    if value >= _TRACE_CRITICAL:
        style = "bold red"
    elif value >= 50:
        style = "yellow"
    else:
        style = "cyan"
    return f"[{style}]{bar}[/] {value}%"


def _format_tab_label(label: str, *, active: bool, disabled: bool = False) -> str:
    if disabled:
        return f"[dim strike]{label}[/]"
    if active:
        return f"[bold underline magenta]{label}[/]"
    return f"[dim]{label}[/]"


def format_overlay_netrun_tab(active_tab: str, *, net_shell: bool) -> str:
    return _format_tab_label(
        "[⎈ NET]",
        active=active_tab == OVERLAY_TAB_NETRUN,
        disabled=not net_shell,
    )


def format_overlay_help_tab(active_tab: str) -> str:
    return _format_tab_label("[? Help]", active=active_tab == OVERLAY_TAB_HELP)


def format_overlay_trace_chip(trace: str | int, *, locale: str) -> str:
    trace_label = t(locale, "client.ui.overlay.trace")
    return f"{trace_label} {format_trace_bar(trace)}"


def format_overlay_tab_row(
    active_tab: str,
    net_shell: bool,
    locale: str,
    *,
    trace: str | int = 0,
) -> str:
    """Browser-style tab row: [⎈ NET] [? Help]; trace bar when NET tab active or in shell."""
    net_label = "[⎈ NET]"
    help_label = "[? Help]"
    net_tab = _format_tab_label(
        net_label,
        active=active_tab == OVERLAY_TAB_NETRUN,
        disabled=not net_shell,
    )
    help_tab = _format_tab_label(help_label, active=active_tab == OVERLAY_TAB_HELP)
    parts = [net_tab, help_tab]
    if active_tab == OVERLAY_TAB_NETRUN or net_shell:
        trace_label = t(locale, "client.ui.overlay.trace")
        parts.append(f"  [dim]│[/]  {trace_label} {format_trace_bar(trace)}")
    return "  ".join(parts)


def overlay_header_controls(locale: str) -> str:
    """Collapse hint for overlay chrome ([−] + Esc)."""
    collapse = t(locale, "client.ui.overlay.collapse")
    esc = t(locale, "client.ui.overlay.esc_close")
    return f"[dim]{collapse}[/]  [dim]· {esc}[/]"


def format_netrun_hud(state: ClientViewState, locale: str) -> str:
    """NETRUN overlay body: trace, link, sector nodes, English command cheat sheet."""
    trace_val = _parse_trace(state.net_trace)
    connected = t(locale, "net.status_no_link")
    nodes_display = (
        " · ".join(state.complete_net_nodes)
        if state.complete_net_nodes
        else t(locale, "net.status_no_nodes")
    )

    lines: list[str] = [
        f"[bold cyan]{t(locale, 'client.ui.overlay.trace')}[/]  {format_trace_bar(trace_val)}",
        (
            f"[bold cyan]{t(locale, 'client.ui.overlay.link')}[/]  "
            f"[bold]{connected}[/]"
        ),
        (
            f"[bold cyan]{t(locale, 'client.ui.overlay.nodes')}[/]  "
            f"{nodes_display}"
        ),
        "",
        f"[bold underline]{t(locale, 'client.ui.overlay.commands')}[/]",
    ]
    for cmd in NETRUN_HUD_COMMANDS:
        desc = t(locale, f"net.help_cmds.{cmd}")
        lines.append(f"  [bold cyan]{cmd:<10}[/] [dim]{desc}[/]")
    return "\n".join(lines)