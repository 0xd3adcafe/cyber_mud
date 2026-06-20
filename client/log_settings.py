from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from client.log_classifier import LOG_KINDS
from client.themes import _load_settings_dict, _write_settings_dict, settings_path

ALWAYS_VISIBLE_KINDS = frozenset({"echo", "sys", "err", "motd"})

HIDEABLE_KINDS: tuple[str, ...] = (
    "ambient",
    "social",
    "combat",
    "env",
    "quest",
    "progression",
    "text",
)

_KIND_ALIASES: dict[str, str] = {
    "movement": "env",
    "move": "env",
    "environment": "env",
    "gig": "quest",
    "gigs": "quest",
    "xp": "progression",
}


@dataclass
class LogDisplaySettings:
    compact: bool = False
    hidden_kinds: frozenset[str] = field(default_factory=frozenset)

    def is_hidden(self, kind: str) -> bool:
        if kind in ALWAYS_VISIBLE_KINDS:
            return False
        if kind == "env_move":
            return "env" in self.hidden_kinds
        return kind in self.hidden_kinds

    def hide_kind(self, kind: str) -> LogDisplaySettings:
        resolved = resolve_hideable_kind(kind)
        if resolved is None:
            return self
        return LogDisplaySettings(
            compact=self.compact,
            hidden_kinds=self.hidden_kinds | {resolved},
        )

    def show_kind(self, kind: str) -> LogDisplaySettings:
        resolved = resolve_hideable_kind(kind)
        if resolved is None:
            return self
        return LogDisplaySettings(
            compact=self.compact,
            hidden_kinds=self.hidden_kinds - {resolved},
        )

    def show_all_kinds(self) -> LogDisplaySettings:
        return LogDisplaySettings(compact=self.compact, hidden_kinds=frozenset())

    def set_compact(self, enabled: bool) -> LogDisplaySettings:
        return LogDisplaySettings(compact=enabled, hidden_kinds=self.hidden_kinds)

    def to_dict(self) -> dict[str, object]:
        return {
            "compact": self.compact,
            "hidden_kinds": sorted(self.hidden_kinds),
        }

    @classmethod
    def from_dict(cls, data: object) -> LogDisplaySettings:
        if not isinstance(data, dict):
            return cls()
        compact = bool(data.get("compact", False))
        raw_hidden = data.get("hidden_kinds", [])
        hidden: set[str] = set()
        if isinstance(raw_hidden, list):
            for item in raw_hidden:
                resolved = resolve_hideable_kind(str(item))
                if resolved is not None:
                    hidden.add(resolved)
        return cls(compact=compact, hidden_kinds=frozenset(hidden))


def resolve_hideable_kind(kind: str) -> str | None:
    normalized = kind.strip().lower()
    if not normalized:
        return None
    normalized = _KIND_ALIASES.get(normalized, normalized)
    if normalized not in HIDEABLE_KINDS:
        return None
    return normalized


def load_log_settings() -> LogDisplaySettings:
    data = _load_settings_dict()
    return LogDisplaySettings.from_dict(data.get("log"))


def save_log_settings(settings: LogDisplaySettings) -> None:
    payload = _load_settings_dict()
    payload["log"] = settings.to_dict()
    _write_settings_dict(payload)


def parse_log_command(args: str) -> tuple[str, str | None]:
    text = args.strip()
    if not text:
        return "status", None
    parts = text.split(maxsplit=2)
    verb = parts[0].lower()
    if verb == "compact":
        if len(parts) == 1:
            return "compact_toggle", None
        flag = parts[1].lower()
        if flag in {"on", "1", "true", "yes"}:
            return "compact_on", None
        if flag in {"off", "0", "false", "no"}:
            return "compact_off", None
        return "compact_toggle", None
    if verb == "hide" and len(parts) >= 2:
        return "hide", parts[1].lower()
    if verb == "show":
        if len(parts) >= 2 and parts[1].lower() == "all":
            return "show_all", None
        if len(parts) >= 2:
            return "show", parts[1].lower()
    if verb == "export":
        path = parts[1] if len(parts) >= 2 else None
        return "export", path
    return "unknown", text


def default_export_path() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return settings_path().parent / f"log_export_{stamp}.txt"


def export_log_text(lines: list[str]) -> str:
    body = "\n".join(lines)
    if body:
        return body + "\n"
    return ""


def strip_rich_markup(text: str) -> str:
    return re.sub(r"\[/?[^\]]+\]", "", text)


def hideable_kinds_label() -> str:
    return ", ".join(HIDEABLE_KINDS)


def valid_log_kinds() -> frozenset[str]:
    return LOG_KINDS