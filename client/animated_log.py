from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

from client.cd_display import format_cooldown_line, parse_cooldown_line
from client.output_prefix import format_output_line

_MAX_LINES = 500


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

    def append(self, text: str, *, kind: str) -> None:
        plain = _strip_rich(text)
        cd = parse_cooldown_line(plain)
        entry = LogEntry(text=plain, kind=kind)
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

    def render(self) -> list[str]:
        lines: list[str] = []
        for entry in self.entries:
            text = entry.text
            if entry.has_cooldown:
                remaining = _cd_remaining(entry)
                if remaining > 0:
                    text = format_cooldown_line(entry.cd_prefix, remaining)
                else:
                    text = format_cooldown_line(entry.cd_prefix, 0)
            lines.append(
                format_output_line(
                    text,
                    kind=entry.kind,
                    frame=self.frame,
                    animate=entry.pending,
                )
            )
        return lines


def _cd_remaining(entry: LogEntry) -> int:
    elapsed = max(0, int(time.monotonic() - entry.cd_started_at))
    return max(0, entry.cd_seconds - elapsed)


def _strip_rich(text: str) -> str:
    return re.sub(r"\[/?[^\]]+\]", "", text)