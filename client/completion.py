from __future__ import annotations

from typing import Callable

from textual import events
from textual.binding import Binding
from textual.suggester import Suggester
from textual.widgets import Input

from shared.completion import complete_input


def complete_from_view(view: object, value: str) -> str | None:
    return complete_input(
        value,
        room_items=tuple(view.complete_room_items),
        room_npcs=tuple(view.complete_npcs),
        room_exits=tuple(view.complete_exits),
        inventory=tuple(view.complete_inventory),
        net_shell=view.net_shell,
    )


class MudPrompt(Input):
    """Game prompt; Tab completes instead of moving focus (Textual default)."""

    BINDINGS = [
        *Input.BINDINGS,
        Binding("tab", "mud_complete", "補全", show=False),
        Binding("up", "history_older", "上一筆指令", show=False),
        Binding("down", "history_newer", "下一筆指令", show=False),
        Binding("ctrl+p", "history_older", show=False),
        Binding("ctrl+n", "history_newer", show=False),
        Binding("escape", "history_cancel", "還原草稿", show=False),
    ]

    def _command_history(self):
        app = self.app
        if hasattr(app, "_command_history"):
            return app._command_history
        return None

    def _apply_history_value(self, value: str) -> None:
        self.value = value
        self.cursor_position = len(value)

    def action_mud_complete(self) -> None:
        app = self.app
        if hasattr(app, "_apply_prompt_completion"):
            app._apply_prompt_completion(self)

    def action_history_older(self) -> None:
        history = self._command_history()
        if history is None:
            return
        history.begin_browse(self.value)
        entry = history.older()
        if entry is not None:
            self._apply_history_value(entry)

    def action_history_newer(self) -> None:
        history = self._command_history()
        if history is None:
            return
        entry = history.newer()
        if entry is not None:
            self._apply_history_value(entry)

    def action_history_cancel(self) -> None:
        history = self._command_history()
        if history is None or not history.is_browsing:
            return
        self._apply_history_value(history.cancel_browse())

    async def _on_key(self, event: events.Key) -> None:
        history = self._command_history()
        if history is not None and history.is_browsing and event.is_printable:
            history.mark_edited()
        await super()._on_key(event)


class MudSuggester(Suggester):
    def __init__(self, get_view: Callable[[], object]) -> None:
        super().__init__(case_sensitive=False)
        self._get_view = get_view

    async def get_suggestion(self, value: str) -> str | None:
        return complete_from_view(self._get_view(), value)