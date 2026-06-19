from __future__ import annotations

import json
from dataclasses import dataclass, field

from shared.protocol import META_PREFIX, PANEL_PREFIX, UI_PREFIX


@dataclass
class ClientViewState:
    room: str = "—"
    hp: str = "—"
    gold: str = "—"
    time: str = "—"
    period: str = "—"
    weather: str = ""
    hint: str = ""
    combat_log: str = ""
    prompt_mud: str = "> "
    net_shell: bool = False
    net_prompt: str = "ghost@netrun-kali> "
    sidebar_open: bool = False
    sidebar_panel: str = ""
    sidebar_lines: list[str] = field(default_factory=list)
    sidebar_ui: dict | None = None
    pending_panel: str = ""
    stream_panel: str = ""
    refresh_sidebar: bool = False


def parse_meta_payload(payload: str) -> tuple[str, str]:
    key, _, value = payload.partition("=")
    return key, value


def apply_meta(state: ClientViewState, key: str, value: str) -> None:
    if key == "room":
        state.room = value
    elif key == "hp":
        state.hp = value
    elif key == "gold":
        state.gold = value
    elif key == "time":
        state.time = value
    elif key == "period":
        state.period = value
    elif key == "weather":
        state.weather = value
    elif key == "hint":
        state.hint = value
    elif key == "combat_log":
        state.combat_log = value
    elif key == "prompt_mud":
        state.prompt_mud = value
    elif key == "net_shell":
        state.net_shell = value == "1"
    elif key == "net_prompt":
        state.net_prompt = value
    elif key == "ui_panel":
        state.pending_panel = value
        state.sidebar_lines = []
        state.sidebar_ui = None
    elif key == "ui_panel_end":
        if state.pending_panel:
            state.stream_panel = state.pending_panel
            state.sidebar_panel = state.pending_panel
            state.sidebar_open = True
        state.pending_panel = ""
    elif key == "refresh_sidebar":
        state.refresh_sidebar = value == "1"


def handle_panel_line(state: ClientViewState, line: str) -> None:
    if state.pending_panel:
        state.sidebar_lines.append(line)


def handle_ui_json(state: ClientViewState, payload: str) -> None:
    try:
        state.sidebar_ui = json.loads(payload)
    except json.JSONDecodeError:
        state.sidebar_ui = None


def classify_server_line(line: str) -> str:
    if line.startswith(META_PREFIX):
        return "meta"
    if line.startswith(PANEL_PREFIX):
        return "panel"
    if line.startswith(UI_PREFIX):
        return "ui"
    return "text"


def status_text(state: ClientViewState, *, host: str, port: int) -> str:
    weather = f"  │  {state.weather}" if state.weather else ""
    return (
        f"  房間 {state.room}  │  HP {state.hp}  │  ${state.gold}"
        f"  │  {state.time} {state.period}{weather}  │  {host}:{port}"
    )


def hint_text(state: ClientViewState) -> str:
    if state.combat_log:
        return state.combat_log
    return state.hint


LOCAL_COMMANDS = frozenset({"reconnect", "prompt", "quit"})
NETRUN_SERVER_COMMANDS = frozenset({"exit", "quit", "help", "disconnect", "logout"})


def active_prompt(state: ClientViewState, *, local_override: str = "") -> str:
    if local_override:
        return local_override
    if state.net_shell:
        prompt = state.net_prompt
        return prompt if prompt.strip() else "ghost@netrun-kali> "
    prompt = state.prompt_mud.strip()
    return prompt if prompt else "> "


def is_netrun_exit_command(text: str) -> bool:
    body = text[1:].strip() if text.startswith("/") else text.strip()
    if not body:
        return False
    verb = body.split(maxsplit=1)[0].lower()
    return verb in NETRUN_SERVER_COMMANDS


def netrun_blocks_server_command(text: str) -> bool:
    if not text or text.startswith("/"):
        return False
    verb = text.split(maxsplit=1)[0].lower()
    return verb not in NETRUN_SERVER_COMMANDS


def is_local_command(text: str) -> bool:
    if not text.startswith("/"):
        return False
    verb = text[1:].split()[0].lower()
    if verb == "exit":
        return False
    return verb in LOCAL_COMMANDS


def parse_local_command(text: str) -> tuple[str, str]:
    body = text[1:].strip()
    parts = body.split(maxsplit=1)
    verb = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    return verb, args


def reconnect_delay(attempt: int, *, base: float = 1.0, maximum: float = 30.0) -> float:
    return min(maximum, base * (2 ** max(0, attempt - 1)))