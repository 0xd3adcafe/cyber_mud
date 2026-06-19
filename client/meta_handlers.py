from __future__ import annotations

import json
from dataclasses import dataclass, field

from shared.completion import parse_csv_meta
from shared.protocol import META_PREFIX, PANEL_PREFIX, UI_PREFIX

SIDEBAR_PANEL_ORDER: tuple[str, ...] = ("pda", "map", "equipment", "help")
_SIDEBAR_AUTO_REFRESH_ON_MOVE = frozenset({"map"})
_SIDEBAR_REFRESH_ON_EQUIP = frozenset({"pda", "equipment"})


@dataclass
class SidebarPanel:
    lines: list[str] = field(default_factory=list)
    ui: dict | None = None


@dataclass
class ClientViewState:
    authenticated: bool = False
    room: str = "—"
    room_id: str = ""
    hp: str = "—"
    ram: str = "—"
    gold: str = "—"
    quest: str = ""
    combat_target: str = ""
    combat_npc_hp: str = ""
    time: str = "—"
    period: str = "—"
    weather: str = ""
    hint: str = ""
    combat_log: str = ""
    in_combat: bool = False
    combat_player_cd: int = 0
    combat_npc_cd: int = 0
    combat_cd_synced_at: float = 0.0
    prompt_mud: str = "> "
    net_shell: bool = False
    net_prompt: str = "ghost@netrun-kali> "
    sidebar_open: bool = False
    sidebar_stack: list[str] = field(default_factory=list)
    sidebar_panels: dict[str, SidebarPanel] = field(default_factory=dict)
    pending_panel: str = ""
    refresh_sidebar: bool = False
    complete_room_items: list[str] = field(default_factory=list)
    complete_npcs: list[str] = field(default_factory=list)
    complete_exits: list[str] = field(default_factory=list)
    complete_inventory: list[str] = field(default_factory=list)
    complete_equipped: list[str] = field(default_factory=list)


def parse_meta_payload(payload: str) -> tuple[str, str]:
    key, _, value = payload.partition("=")
    return key, value


def apply_meta(state: ClientViewState, key: str, value: str) -> None:
    if key == "auth":
        state.authenticated = value == "1"
    elif key == "room":
        state.room = value
    elif key == "room_id":
        state.room_id = value
    elif key == "hp":
        state.hp = value
    elif key == "ram":
        state.ram = value
    elif key == "quest":
        state.quest = value
    elif key == "combat_target":
        state.combat_target = value
    elif key == "combat_npc_hp":
        state.combat_npc_hp = value
    elif key == "gold":
        state.gold = value
    elif key == "time":
        state.time = value
    elif key == "period":
        state.period = value
    elif key == "weather":
        state.weather = value
    elif key == "hint":
        state.hint = value if value else ""
    elif key == "combat_log":
        state.combat_log = value
    elif key == "combat":
        state.in_combat = value == "1"
        if value != "1":
            state.combat_player_cd = 0
            state.combat_npc_cd = 0
            state.combat_log = ""
            state.combat_target = ""
            state.combat_npc_hp = ""
    elif key == "combat_cd":
        from client.cd_display import parse_combat_cd_meta
        import time

        player_secs, npc_secs = parse_combat_cd_meta(value)
        state.combat_player_cd = player_secs
        state.combat_npc_cd = npc_secs
        state.combat_cd_synced_at = time.monotonic()
        state.in_combat = True
    elif key == "prompt_mud":
        state.prompt_mud = value
    elif key == "net_shell":
        state.net_shell = value == "1"
    elif key == "net_prompt":
        state.net_prompt = value
    elif key == "ui_panel":
        state.pending_panel = value
        panel = _ensure_sidebar_panel(state, value)
        panel.lines = []
        panel.ui = None
    elif key == "ui_panel_end":
        if state.pending_panel:
            if state.pending_panel not in state.sidebar_stack:
                state.sidebar_stack.append(state.pending_panel)
            state.sidebar_open = True
        state.pending_panel = ""
    elif key == "refresh_sidebar":
        state.refresh_sidebar = value == "1"
    elif key == "complete_room_items":
        state.complete_room_items = parse_csv_meta(value)
    elif key == "complete_npcs":
        state.complete_npcs = parse_csv_meta(value)
    elif key == "complete_exits":
        state.complete_exits = parse_csv_meta(value)
    elif key == "complete_inventory":
        state.complete_inventory = parse_csv_meta(value)
    elif key == "complete_equipped":
        state.complete_equipped = parse_csv_meta(value)


def ordered_sidebar_stack(stack: list[str]) -> list[str]:
    order = {panel_id: idx for idx, panel_id in enumerate(SIDEBAR_PANEL_ORDER)}
    return sorted(stack, key=lambda panel_id: order.get(panel_id, len(SIDEBAR_PANEL_ORDER)))


def _ensure_sidebar_panel(state: ClientViewState, panel_id: str) -> SidebarPanel:
    panel = state.sidebar_panels.get(panel_id)
    if panel is None:
        panel = SidebarPanel()
        state.sidebar_panels[panel_id] = panel
    return panel


def sidebar_panel_is_open(state: ClientViewState, panel_id: str) -> bool:
    return panel_id in state.sidebar_stack


def toggle_sidebar_panel(state: ClientViewState, panel_id: str) -> bool:
    """Toggle panel in stack. Returns True if panel should be fetched from server."""
    if panel_id in state.sidebar_stack:
        state.sidebar_stack.remove(panel_id)
        if not state.sidebar_stack:
            state.sidebar_open = False
        return False
    state.sidebar_open = True
    return True


def should_refresh_sidebar_on_room_change(
    state: ClientViewState,
    *,
    old_room_id: str,
    new_room_id: str,
) -> bool:
    if not state.sidebar_open or not new_room_id or old_room_id == new_room_id:
        return False
    return bool(set(state.sidebar_stack) & _SIDEBAR_AUTO_REFRESH_ON_MOVE)


def panels_to_refresh_on_move(state: ClientViewState) -> list[str]:
    return [
        panel_id
        for panel_id in ordered_sidebar_stack(state.sidebar_stack)
        if panel_id in _SIDEBAR_AUTO_REFRESH_ON_MOVE
    ]


def panels_to_refresh_on_equip(state: ClientViewState) -> list[str]:
    return [
        panel_id
        for panel_id in ordered_sidebar_stack(state.sidebar_stack)
        if panel_id in _SIDEBAR_REFRESH_ON_EQUIP
    ]


def handle_panel_line(state: ClientViewState, line: str) -> None:
    if state.pending_panel:
        _ensure_sidebar_panel(state, state.pending_panel).lines.append(line)


def handle_ui_json(state: ClientViewState, payload: str) -> None:
    if not state.pending_panel:
        return
    try:
        _ensure_sidebar_panel(state, state.pending_panel).ui = json.loads(payload)
    except json.JSONDecodeError:
        _ensure_sidebar_panel(state, state.pending_panel).ui = None


def format_sidebar_content(state: ClientViewState) -> str:
    from client.ui_format import format_stacked_sidebar

    return format_stacked_sidebar(state)


def classify_server_line(line: str) -> str:
    if line.startswith(META_PREFIX):
        return "meta"
    if line.startswith(PANEL_PREFIX):
        return "panel"
    if line.startswith(UI_PREFIX):
        return "ui"
    return "text"


def status_text(state: ClientViewState, *, host: str, port: int) -> str:
    from client.ui_format import format_status_markup

    return format_status_markup(state, host=host, port=port)


def hint_text(state: ClientViewState) -> str:
    from client.ui_format import format_hint_markup

    return format_hint_markup(state)


LOCAL_COMMANDS = frozenset({"reconnect", "prompt", "quit", "theme"})
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