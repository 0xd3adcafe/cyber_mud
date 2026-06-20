from __future__ import annotations

import time

from client.cd_display import format_combat_cd_label, remaining_seconds
from client.meta_handlers import ClientViewState, SidebarPanel, ordered_sidebar_stack
from client.status_indicators import (
    animated_icon,
    combat_active,
    quest_active,
    status_needs_animation,
    vitals_alert,
)


_PANEL_HEADERS: dict[str, tuple[str, str, str]] = {
    "pda": ("F2", "◈ PDA", "個人終端"),
    "help": ("F3", "? 說明", "指令清單"),
    "map": ("F4", "◎ 地圖", "探索視圖"),
    "equipment": ("F5", "⛶ 裝備", "義體與裝備"),
    "gigs": ("F7", "◆ 委託", "任務追蹤"),
}


def panel_header(panel: str) -> str:
    key, icon, desc = _PANEL_HEADERS.get(panel, ("F6", f"◈ {panel}", "側邊面板"))
    return f"[bold magenta]❙[/]  [bold]{icon}[/]  [dim]{desc}[/]  [dim]· {key}[/]"


def format_sidebar_header(state: ClientViewState) -> str:
    stack = ordered_sidebar_stack(state.sidebar_stack)
    if not stack:
        return ""
    if len(stack) == 1:
        return panel_header(stack[0])
    labels = " · ".join(_PANEL_HEADERS.get(panel, ("", f"◈ {panel}", ""))[1] for panel in stack)
    return f"[bold magenta]❙[/]  [bold]{labels}[/]  [dim]· F6 收合[/]"


def format_info_bar(
    state: ClientViewState,
    *,
    host: str,
    port: int,
    reconnecting: bool = False,
    spinner_frame: int = 0,
) -> str:
    """Grok-style compact status strip; hint overlays when active."""
    status = format_status_markup(
        state,
        host=host,
        port=port,
        reconnecting=reconnecting,
        spinner_frame=spinner_frame,
    )
    hints = format_hint_rows(state, spinner_frame=spinner_frame)
    if hints:
        return f"{status}\n{hints}"
    return status


def format_status_markup(
    state: ClientViewState,
    *,
    host: str,
    port: int,
    reconnecting: bool = False,
    spinner_frame: int = 0,
) -> str:
    weather = f"  [dim]│[/]  [cyan]{state.weather}[/]" if state.weather else ""
    hp_alert = vitals_alert(state) or combat_active(state)
    hp_icon = animated_icon("♥", frame=spinner_frame, active=hp_alert)
    hp_style = "bold red" if vitals_alert(state) else ("bold yellow" if combat_active(state) else "green")
    net = ""
    if state.net_shell:
        net_icon = animated_icon("⎈", frame=spinner_frame, active=True)
        net = f"  [dim]│[/]  [magenta]{net_icon} NETRUN[/]"
    quest_chip = ""
    if state.quest and not combat_active(state):
        q_icon = animated_icon("◆", frame=spinner_frame, active=quest_active(state))
        quest_chip = f"  [dim]│[/]  [yellow]{q_icon} {state.quest}[/]"
    link = "  [dim]│[/]  [yellow]重連中…[/]" if reconnecting else ""
    return (
        f"[bold cyan]◈[/]  [bold]{state.room}[/]"
        f"  [dim]│[/]  [{hp_style}]{hp_icon} HP {state.hp}[/]"
        f"  [dim]│[/]  [yellow]€{state.gold}[/]"
        f"  [dim]│[/]  [dim]{state.time}  {state.period}[/]"
        f"{weather}{net}{quest_chip}{link}"
    )


def format_hotkey_bar() -> str:
    return (
        "[bold cyan]快捷鍵[/]"
        "  Tab"
        "  [magenta]F2[/]PDA"
        "  [cyan]F3[/]說明"
        "  [green]F4[/]地圖"
        "  [yellow]F5[/]裝備"
        "  F6收合"
        "  [yellow]F7[/]委託"
        "  [dim]│[/]  [yellow]/reconnect[/]"
        "  [dim]│[/]  ↑↓歷史"
    )


def _live_combat_cd(state: ClientViewState) -> str:
    if not state.in_combat:
        return ""
    synced = state.combat_cd_synced_at or time.monotonic()
    player = remaining_seconds(state.combat_player_cd, synced)
    npc = remaining_seconds(state.combat_npc_cd, synced)
    return format_combat_cd_label(player, npc)


def format_hint_rows(state: ClientViewState, *, spinner_frame: int = 0) -> str:
    rows: list[str] = []
    if combat_active(state):
        rows.append(_format_combat_hint(state, spinner_frame=spinner_frame))
    if state.hint and not combat_active(state):
        rows.append(_format_quest_hint(state, spinner_frame=spinner_frame))
    elif state.hint and combat_active(state):
        rows.append(_format_quest_hint(state, spinner_frame=spinner_frame, dimmed=True))
    if not rows and not status_needs_animation(state):
        return ""
    if not rows:
        rows.append("[dim]▸  探索夜城 · look · go · help[/]")
    return "\n".join(rows)


def _format_combat_hint(state: ClientViewState, *, spinner_frame: int) -> str:
    spin = animated_icon("⚔", frame=spinner_frame, active=True)
    target = state.combat_target
    npc_hp = state.combat_npc_hp
    target_part = ""
    if target:
        hp_bit = f" HP {npc_hp}" if npc_hp else ""
        target_part = f"  [bold red]vs {target}[/]{hp_bit}"
    cd_label = _live_combat_cd(state)
    cd_part = f"  [bold cyan]{cd_label}[/]" if cd_label else ""
    body = state.combat_log or "交戰中"
    return f"[bold red]{spin}[/]  [yellow]{body}[/]{target_part}{cd_part}"


def _format_quest_hint(state: ClientViewState, *, spinner_frame: int, dimmed: bool = False) -> str:
    spin = animated_icon("▸", frame=spinner_frame, active=True)
    quest_tag = f"[dim]（{state.quest}）[/] " if state.quest else ""
    if dimmed:
        return f"[dim]{spin}[/]  {quest_tag}[dim]{state.hint}[/]"
    return f"[bold yellow]{spin}[/]  {quest_tag}{state.hint}"


def format_hint_markup(state: ClientViewState, *, spinner_frame: int = 0) -> str:
    return format_hint_rows(state, spinner_frame=spinner_frame) or "[dim]▸  探索夜城 · look · go · help[/]"


def format_ui_sections(ui: dict) -> str:
    lines: list[str] = []
    for section in ui.get("sections", []):
        kind = section.get("kind")
        if kind == "row":
            label = section.get("label", "")
            value = section.get("value", "")
            lines.append(f"[dim]{label}[/]  [bold]{value}[/]")
        elif kind == "list":
            if section.get("title"):
                lines.append(f"\n[bold underline]{section['title']}[/]")
            for item in section.get("items", []):
                lines.append(f"  [cyan]•[/]  {item}")
        elif kind == "text":
            for line in section.get("lines", []):
                if "[@]" in line:
                    lines.append(line.replace("[@]", "[bold green on black] [@] [/]"))
                elif line.strip() in {"■", "·"}:
                    lines.append(f"[dim]{line}[/]")
                else:
                    lines.append(line)
    return "\n".join(lines)


def format_panel_content(panel: SidebarPanel, *, panel_id: str = "") -> str:
    if panel.ui:
        return format_ui_sections(panel.ui)
    if panel.lines:
        return "\n".join(panel.lines)
    return f"[dim]◈ {panel_id}[/]" if panel_id else ""


def format_stacked_sidebar(state: ClientViewState) -> str:
    blocks: list[str] = []
    for panel_id in ordered_sidebar_stack(state.sidebar_stack):
        panel = state.sidebar_panels.get(panel_id)
        if panel is None:
            continue
        blocks.append(f"[bold underline]{panel_header(panel_id)}[/]")
        content = format_panel_content(panel, panel_id=panel_id)
        if content:
            blocks.append(content)
    return "\n\n".join(blocks) if blocks else "[dim]（側欄空白 · F2–F5／F7 開啟面板）[/]"


def format_sidebar_markup(state: ClientViewState) -> str:
    if state.sidebar_stack:
        return format_stacked_sidebar(state)
    return "[dim]（側欄空白）[/]"