from __future__ import annotations

import time
from dataclasses import dataclass

from client.animated_log import AnimatedLogBuffer
from client.cd_display import format_combat_cd_label, remaining_seconds
from client.meta_handlers import ClientViewState
from client.output_prefix import spinner_char
from client.status_indicators import combat_active
from client.themes import focus_palette_for_theme
from shared.i18n import t

_ACCENT_ROWS = 4
_GRADIENT_CHARS = ("▁", "▂", "▃", "▄", "▅", "▆", "▇")


@dataclass
class FocusSnapshot:
    kind: str
    body: str
    status_key: str
    icon: str


class FocusTracker:
    def __init__(self) -> None:
        self._phase_key = ""
        self._started_at = 0.0

    def sync(self, phase_key: str) -> float:
        if phase_key != self._phase_key:
            self._phase_key = phase_key
            self._started_at = time.monotonic()
        if not phase_key:
            return 0.0
        return max(0.0, time.monotonic() - self._started_at)


def _pending_command_text(buffer: AnimatedLogBuffer) -> str:
    for entry in reversed(buffer.entries):
        if entry.pending and entry.kind == "echo":
            text = entry.text.strip()
            if text.startswith("❯"):
                text = text[1:].strip()
            return text
    return ""


def resolve_focus(
    state: ClientViewState,
    *,
    has_pending: bool,
    pending_text: str = "",
    locale: str = "zh",
) -> FocusSnapshot | None:
    if combat_active(state):
        body = state.combat_log or t(locale, "focus.combat_default")
        if state.combat_target:
            hp_bit = f" HP {state.combat_npc_hp}" if state.combat_npc_hp else ""
            body = f"{body}  vs {state.combat_target}{hp_bit}"
        synced = state.combat_cd_synced_at or time.monotonic()
        cd_label = format_combat_cd_label(
            remaining_seconds(state.combat_player_cd, synced),
            remaining_seconds(state.combat_npc_cd, synced),
        )
        if cd_label:
            body = f"{body}  {cd_label}"
        return FocusSnapshot(kind="combat", body=body, status_key="combat_status", icon="⚔")
    if has_pending:
        body = pending_text or "…"
        return FocusSnapshot(kind="command", body=body, status_key="command_status", icon="")
    if state.hint or state.quest:
        parts: list[str] = []
        if state.quest:
            parts.append(state.quest)
        if state.hint:
            parts.append(state.hint)
        return FocusSnapshot(kind="quest", body=" — ".join(parts), status_key="quest_status", icon="◆")
    return None


def focus_phase_key(snapshot: FocusSnapshot | None) -> str:
    if snapshot is None:
        return ""
    return f"{snapshot.kind}:{snapshot.body}"


def flowing_accent_markup(*, frame: int, theme_id: str) -> str:
    palette = focus_palette_for_theme(theme_id)
    stops = palette.gradient
    rows: list[str] = []
    for row in range(_ACCENT_ROWS):
        color_idx = (frame + row) % len(stops)
        char_idx = (frame + row) % len(_GRADIENT_CHARS)
        color = stops[color_idx]
        char = _GRADIENT_CHARS[char_idx]
        rows.append(f"[{color}]{char}[/]")
    return "\n".join(rows)


def _icon_markup(snapshot: FocusSnapshot, *, theme_id: str, frame: int) -> str:
    palette = focus_palette_for_theme(theme_id)
    if snapshot.kind == "quest":
        color = palette.quest_color
        icon = palette.quest_icon
    elif snapshot.kind == "combat":
        color = palette.combat_color
        icon = palette.combat_icon
    else:
        color = palette.command_color
        icon = spinner_char(frame)
    return f"[bold {color}]{icon}[/]"


def format_focus_content(snapshot: FocusSnapshot, *, theme_id: str, frame: int) -> str:
    palette = focus_palette_for_theme(theme_id)
    icon = _icon_markup(snapshot, theme_id=theme_id, frame=frame)
    if snapshot.kind == "combat":
        body_style = palette.combat_color
    elif snapshot.kind == "quest":
        body_style = palette.quest_color
    else:
        body_style = palette.command_color
    return f"{icon}  [bold {body_style}]{snapshot.body}[/]"


def format_focus_status(
    snapshot: FocusSnapshot,
    *,
    theme_id: str,
    locale: str,
    elapsed: float,
) -> str:
    palette = focus_palette_for_theme(theme_id)
    label = t(locale, f"focus.{snapshot.status_key}")
    seconds = f"{elapsed:.1f}s"
    return (
        f"[{palette.status_muted}]{label}…[/]"
        f"  [bold {palette.status_color}]{seconds}[/]"
    )


def focus_block_visible(
    state: ClientViewState,
    *,
    has_pending: bool,
    locale: str = "zh",
) -> bool:
    return resolve_focus(state, has_pending=has_pending, locale=locale) is not None


def render_focus_block(
    state: ClientViewState,
    *,
    theme_id: str,
    locale: str,
    frame: int,
    buffer: AnimatedLogBuffer,
    tracker: FocusTracker,
) -> tuple[str, str, str] | None:
    has_pending = buffer.has_pending()
    pending_text = _pending_command_text(buffer)
    snapshot = resolve_focus(state, has_pending=has_pending, pending_text=pending_text, locale=locale)
    if snapshot is None:
        return None
    elapsed = tracker.sync(focus_phase_key(snapshot))
    accent = flowing_accent_markup(frame=frame, theme_id=theme_id)
    content = format_focus_content(snapshot, theme_id=theme_id, frame=frame)
    status = format_focus_status(snapshot, theme_id=theme_id, locale=locale, elapsed=elapsed)
    return accent, content, status