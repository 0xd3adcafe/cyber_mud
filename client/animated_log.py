from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

from client.cd_display import format_cooldown_line, parse_cooldown_line
from client.env_format import format_environment_line, reset_environment_state
from client.log_classifier import classify_log_line
from client.log_settings import LogDisplaySettings
from client.log_styles import format_log_line
from client.themes import DEFAULT_THEME_ID, resolve_theme_id

_MAX_LINES = 500
_BLOCK_SEPARATOR = "[dim]───[/]"
_ENV_HEADER_MARK = "◈"


@dataclass
class LogEntry:
    text: str
    kind: str
    pending: bool = False
    cd_prefix: str = ""
    cd_seconds: int = 0
    cd_started_at: float = 0.0

    @property
    def has_cooldown(self) -> bool:
        return self.cd_seconds > 0 and bool(self.cd_prefix)


@dataclass
class AnimatedLogBuffer:
    entries: list[LogEntry] = field(default_factory=list)
    frame: int = 0
    theme_id: str = DEFAULT_THEME_ID
    display: LogDisplaySettings = field(default_factory=LogDisplaySettings)
    _env_state: dict[str, str] = field(default_factory=dict)

    def set_theme_id(self, theme_id: str) -> None:
        self.theme_id = resolve_theme_id(theme_id) or DEFAULT_THEME_ID

    def set_display(self, display: LogDisplaySettings) -> None:
        self.display = display

    def clear(self) -> None:
        self.entries.clear()
        self._env_state.clear()
        self.frame = 0

    def append(self, text: str, *, kind: str) -> None:
        resolved = classify_log_line(text, kind=kind)
        if resolved == "echo":
            reset_environment_state(self._env_state)
        plain = _strip_rich(text)
        cd = parse_cooldown_line(plain)
        if cd is not None:
            resolved = "combat"
        entry = LogEntry(text=plain, kind=resolved)
        if cd is not None:
            prefix, seconds = cd
            entry.cd_prefix = prefix
            entry.cd_seconds = seconds
            entry.cd_started_at = time.monotonic()
        self.entries.append(entry)
        if len(self.entries) > _MAX_LINES:
            self.entries = self.entries[-_MAX_LINES:]

    def mark_last_pending(self) -> None:
        if not self.entries:
            return
        self.entries[-1].pending = True

    def has_pending(self) -> bool:
        return any(entry.pending for entry in self.entries)

    def complete_pending(self) -> bool:
        for entry in reversed(self.entries):
            if entry.pending:
                entry.pending = False
                return True
        return False

    def advance_frame(self) -> bool:
        if not self.has_pending():
            return False
        self.frame += 1
        return True

    def tick_cooldowns(self) -> bool:
        changed = False
        for entry in self.entries:
            if not entry.has_cooldown:
                continue
            remaining = _cd_remaining(entry)
            if remaining <= 0:
                entry.cd_seconds = 0
                changed = True
                continue
            changed = True
        return changed

    def _format_entry(self, entry: LogEntry) -> str:
        text = entry.text
        if entry.kind in ("text", "env", "env_move") and text.strip():
            text = format_environment_line(text, self._env_state, theme_id=self.theme_id) or text
        if entry.has_cooldown:
            remaining = _cd_remaining(entry)
            if remaining > 0:
                text = format_cooldown_line(entry.cd_prefix, remaining)
            else:
                text = format_cooldown_line(entry.cd_prefix, 0)
        return format_log_line(
            text,
            kind=entry.kind,
            frame=self.frame,
            animate=entry.pending,
            theme_id=self.theme_id,
            compact=self.display.compact,
        )

    def render_entry(self, index: int = -1) -> str | None:
        if not self.entries:
            return None
        return self._format_entry(self.entries[index])

    def render(self) -> list[str]:
        lines: list[str] = []
        prev: LogEntry | None = None
        for entry in self.entries:
            if self.display.is_hidden(entry.kind):
                continue
            if _needs_block_separator(prev, entry, compact=self.display.compact):
                lines.append(_BLOCK_SEPARATOR)
            lines.append(self._format_entry(entry))
            prev = entry
        return lines

    def plain_lines(self) -> list[str]:
        from client.cd_display import format_cooldown_line
        from client.log_settings import strip_rich_markup

        lines: list[str] = []
        for entry in self.entries:
            if self.display.is_hidden(entry.kind):
                continue
            text = strip_rich_markup(entry.text)
            if entry.has_cooldown:
                remaining = _cd_remaining(entry)
                if remaining > 0:
                    text = format_cooldown_line(entry.cd_prefix, remaining)
                else:
                    text = format_cooldown_line(entry.cd_prefix, 0)
            lines.append(text)
        return lines


def _needs_block_separator(
    prev: LogEntry | None,
    entry: LogEntry,
    *,
    compact: bool = False,
) -> bool:
    if compact or prev is None:
        return False
    text = entry.text.strip()
    if entry.kind == "env" and text.startswith(_ENV_HEADER_MARK):
        if prev.kind == "env_move":
            return True
        return prev.kind not in ("env",)
    if entry.kind == "combat":
        return prev.kind != "combat"
    return False


def _cd_remaining(entry: LogEntry) -> int:
    elapsed = max(0, int(time.monotonic() - entry.cd_started_at))
    return max(0, entry.cd_seconds - elapsed)


def _strip_rich(text: str) -> str:
    return re.sub(r"\[/?[^\]]+\]", "", text)