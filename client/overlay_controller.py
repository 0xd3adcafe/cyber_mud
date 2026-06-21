from __future__ import annotations

from client.meta_handlers import ClientViewState
from client.overlay_panel import OVERLAY_TAB_HELP, OVERLAY_TAB_NETRUN


def snapshot_sidebar(state: ClientViewState) -> None:
    state.sidebar_snapshot_open = state.sidebar_open
    state.sidebar_snapshot_stack = list(state.sidebar_stack)


def restore_sidebar(state: ClientViewState) -> None:
    state.sidebar_open = state.sidebar_snapshot_open
    state.sidebar_stack = list(state.sidebar_snapshot_stack)


def open_overlay(state: ClientViewState, *, tab: str) -> None:
    state.overlay_open = True
    state.overlay_collapsed = False
    state.overlay_active_tab = tab


def close_overlay(state: ClientViewState) -> None:
    state.overlay_open = False
    state.overlay_collapsed = False


def collapse_overlay(state: ClientViewState) -> None:
    state.overlay_collapsed = True


def expand_overlay(state: ClientViewState) -> None:
    state.overlay_collapsed = False
    state.overlay_open = True


def enter_netrun_session(state: ClientViewState) -> None:
    snapshot_sidebar(state)
    open_overlay(state, tab=OVERLAY_TAB_NETRUN)


def exit_netrun_session(state: ClientViewState) -> None:
    close_overlay(state)
    restore_sidebar(state)


def toggle_overlay_tab(state: ClientViewState, tab: str) -> None:
    if tab == OVERLAY_TAB_NETRUN and not state.net_shell:
        return
    open_overlay(state, tab=tab)