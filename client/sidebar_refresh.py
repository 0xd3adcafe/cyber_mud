from __future__ import annotations

from client.meta_handlers import HELP_OVERLAY_PANEL

SIDEBAR_POLL_INTERVAL = 15.0
SIDEBAR_DEBOUNCE_INTERVAL = 2.0

PDA_PATCH_META_KEYS = frozenset(
    {
        "hp",
        "ram",
        "gold",
        "level",
        "xp",
        "posture",
        "fatigue",
        "time",
        "period",
    }
)


def panels_to_fetch(pending: set[str], stack: list[str]) -> list[str]:
    if not pending or not stack:
        return []
    return [panel_id for panel_id in stack if panel_id in pending and panel_id != HELP_OVERLAY_PANEL]


def stack_panels_for_poll(stack: list[str]) -> list[str]:
    return [panel_id for panel_id in stack if panel_id != HELP_OVERLAY_PANEL]