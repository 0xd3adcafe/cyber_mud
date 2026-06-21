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
from shared.i18n import t

_PANEL_KEYS: dict[str, tuple[str, str]] = {
    "pda": ("F1", "pda"),
    "help": ("F2", "help"),
    "map": ("F3", "map"),
    "equipment": ("F4", "equipment"),
    "gigs": ("F5", "gigs"),
    "mesh": ("F6", "mesh"),
}


def _ui(locale: str, key: str, **kwargs: str) -> str:
    return t(locale, f"client.ui.{key}", **kwargs)


def panel_header(panel: str, *, locale: str = "en") -> str:
    hotkey, panel_key = _PANEL_KEYS.get(panel, ("F6", "generic"))
    if panel_key == "generic":
        icon = _ui(locale, "panels.generic.icon", panel=panel)
        desc = _ui(locale, "panels.generic.desc")
    else:
        icon = _ui(locale, f"panels.{panel_key}.icon")
        desc = _ui(locale, f"panels.{panel_key}.desc")
    return f"[bold magenta]❙[/]  [bold]{icon}[/]  [dim]{desc}[/]  [dim]· {hotkey}[/]"


def format_sidebar_header(state: ClientViewState) -> str:
    locale = state.locale or "en"
    stack = ordered_sidebar_stack(state.sidebar_stack)
    if not stack:
        return ""
    if len(stack) == 1:
        return panel_header(stack[0], locale=locale)
    labels: list[str] = []
    for panel_id in stack:
        panel_key = _PANEL_KEYS.get(panel_id, (None, "generic"))[1]
        if panel_key == "generic":
            labels.append(_ui(locale, "panels.generic.icon", panel=panel_id))
        else:
            labels.append(_ui(locale, f"panels.{panel_key}.icon"))
    joined = " · ".join(labels)
    collapse = _ui(locale, "panels.collapse")
    return f"[bold magenta]❙[/]  [bold]{joined}[/]  [dim]· {collapse}[/]"


def format_info_bar(
    state: ClientViewState,
    *,
    host: str,
    port: int,
    reconnecting: bool = False,
    spinner_frame: int = 0,
) -> str:
    """Compact status strip; quest/combat hints live in #focus_block above prompt."""
    return format_status_markup(
        state,
        host=host,
        port=port,
        reconnecting=reconnecting,
        spinner_frame=spinner_frame,
    )


def format_status_markup(
    state: ClientViewState,
    *,
    host: str,
    port: int,
    reconnecting: bool = False,
    spinner_frame: int = 0,
) -> str:
    locale = state.locale or "en"
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
    link = ""
    if reconnecting:
        link = f"  [dim]│[/]  [yellow]{_ui(locale, 'status.reconnecting')}[/]"
    return (
        f"[bold cyan]◈[/]  [bold]{state.room}[/]"
        f"  [dim]│[/]  [{hp_style}]{hp_icon} HP {state.hp}[/]"
        f"  [dim]│[/]  [yellow]€{state.gold}[/]"
        f"  [dim]│[/]  [dim]{state.time}  {state.period}[/]"
        f"{weather}{net}{quest_chip}{link}"
    )


def format_hotkey_bar(*, locale: str = "en", net_shell: bool = False) -> str:
    hk = lambda key: _ui(locale, f"hotkeys.{key}")
    base = (
        f"[bold cyan]{hk('label')}[/]"
        f"  {hk('tab')}"
        f"  [magenta]F1[/]{hk('f1_pda')}"
        f"  [cyan]F2[/]{hk('f2_help')}"
        f"  [green]F3[/]{hk('f3_map')}"
        f"  [yellow]F4[/]{hk('f4_equip')}"
        f"  F5{hk('f5_gigs')}"
        f"  [magenta]F6[/]{hk('f6_mesh')}"
        f"  F11{hk('f11_sidebar')}"
    )
    if net_shell:
        base += f"  [magenta]F12[/]{hk('f12_netrun')}"
    base += f"  [dim]│[/]  [yellow]/reconnect[/]  [dim]│[/]  {hk('history')}"
    return base


def _live_combat_cd(state: ClientViewState) -> str:
    if not state.in_combat:
        return ""
    synced = state.combat_cd_synced_at or time.monotonic()
    player = remaining_seconds(state.combat_player_cd, synced)
    npc = remaining_seconds(state.combat_npc_cd, synced)
    return format_combat_cd_label(player, npc)


def format_hint_rows(state: ClientViewState, *, spinner_frame: int = 0) -> str:
    locale = state.locale or "en"
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
        rows.append(f"[dim]{_ui(locale, 'hint.explore')}[/]")
    return "\n".join(rows)


def _format_combat_hint(state: ClientViewState, *, spinner_frame: int) -> str:
    locale = state.locale or "en"
    spin = animated_icon("⚔", frame=spinner_frame, active=True)
    target = state.combat_target
    npc_hp = state.combat_npc_hp
    target_part = ""
    if target:
        hp_bit = f" HP {npc_hp}" if npc_hp else ""
        target_part = f"  [bold red]vs {target}[/]{hp_bit}"
    cd_label = _live_combat_cd(state)
    cd_part = f"  [bold cyan]{cd_label}[/]" if cd_label else ""
    body = state.combat_log or t(locale, "focus.combat_default")
    return f"[bold red]{spin}[/]  [yellow]{body}[/]{target_part}{cd_part}"


def _format_quest_hint(state: ClientViewState, *, spinner_frame: int, dimmed: bool = False) -> str:
    spin = animated_icon("▸", frame=spinner_frame, active=True)
    quest_tag = f"[dim]（{state.quest}）[/] " if state.quest else ""
    if dimmed:
        return f"[dim]{spin}[/]  {quest_tag}[dim]{state.hint}[/]"
    return f"[bold yellow]{spin}[/]  {quest_tag}{state.hint}"


def format_hint_markup(state: ClientViewState, *, spinner_frame: int = 0) -> str:
    locale = state.locale or "en"
    return format_hint_rows(state, spinner_frame=spinner_frame) or f"[dim]{_ui(locale, 'hint.explore')}[/]"


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
    locale = state.locale or "en"
    blocks: list[str] = []
    for panel_id in ordered_sidebar_stack(state.sidebar_stack):
        panel = state.sidebar_panels.get(panel_id)
        if panel is None:
            continue
        blocks.append(f"[bold underline]{panel_header(panel_id, locale=locale)}[/]")
        content = format_panel_content(panel, panel_id=panel_id)
        if content:
            blocks.append(content)
    if blocks:
        return "\n\n".join(blocks)
    return f"[dim]{_ui(locale, 'sidebar.empty_hint')}[/]"


def format_sidebar_markup(state: ClientViewState) -> str:
    locale = state.locale or "en"
    if state.sidebar_stack:
        return format_stacked_sidebar(state)
    return f"[dim]{_ui(locale, 'sidebar.empty')}[/]"