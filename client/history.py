from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from client.themes import settings_path

DEFAULT_MAX_ENTRIES = 200


def history_path() -> Path:
    return settings_path().parent / "command_history.json"


def load_command_history(*, max_entries: int = DEFAULT_MAX_ENTRIES) -> list[str]:
    path = history_path()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return []
    if not isinstance(raw, list):
        return []
    entries = [str(line) for line in raw if str(line).strip()]
    return entries[-max_entries:]


def save_command_history(entries: list[str]) -> None:
    path = history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@dataclass
class CommandHistory:
    entries: list[str] = field(default_factory=list)
    max_entries: int = DEFAULT_MAX_ENTRIES
    _index: int = -1
    _draft: str = ""

    @classmethod
    def load(cls, *, max_entries: int = DEFAULT_MAX_ENTRIES) -> CommandHistory:
        return cls(entries=load_command_history(max_entries=max_entries), max_entries=max_entries)

    def persist(self) -> None:
        save_command_history(self.entries)

    def add(self, command: str) -> None:
        text = command.strip()
        if not text:
            return
        if self.entries and self.entries[-1] == text:
            self.reset_browse()
            return
        self.entries.append(text)
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries :]
        self.persist()
        self.reset_browse()

    def reset_browse(self) -> None:
        self._index = -1
        self._draft = ""

    @property
    def is_browsing(self) -> bool:
        return self._index != -1

    def mark_edited(self) -> None:
        if self.is_browsing:
            self._index = -1
            self._draft = ""

    def begin_browse(self, current: str) -> None:
        if not self.is_browsing:
            self._draft = current

    def older(self) -> str | None:
        if not self.entries:
            return None
        if self._index == -1:
            self._index = len(self.entries) - 1
        elif self._index > 0:
            self._index -= 1
        return self.entries[self._index]

    def newer(self) -> str | None:
        if not self.entries or self._index == -1:
            return None
        if self._index < len(self.entries) - 1:
            self._index += 1
            return self.entries[self._index]
        draft = self._draft
        self.reset_browse()
        return draft

    def cancel_browse(self) -> str:
        draft = self._draft
        self.reset_browse()
        return draft