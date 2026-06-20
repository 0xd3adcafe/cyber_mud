from __future__ import annotations

import re

from client.meta_handlers import SidebarPanel

_LINE_RE = re.compile(r"^\s*(?P<name>\S+)\s+[—–-]\s+(?P<desc>.+)$")


def help_overlay_header() -> str:
    return "[bold magenta]❙[/]  [bold]? 指令說明[/]  [dim]· F3 / Esc 關閉[/]"


def _format_entry(name: str, desc: str) -> str:
    return f"[bold cyan]{name:<16}[/] [dim]{desc}[/]"


def _entries_from_panel_lines(lines: list[str]) -> list[str]:
    rows: list[str] = []
    for line in lines:
        if not line.strip() or line.strip().startswith("◈"):
            continue
        match = _LINE_RE.match(line.strip())
        if match:
            rows.append(_format_entry(match.group("name"), match.group("desc")))
        else:
            rows.append(f"[dim]{line.strip()}[/]")
    return rows


def _entries_from_ui(panel: SidebarPanel) -> list[str]:
    if not panel.ui:
        return []
    rows: list[str] = []
    for section in panel.ui.get("sections", []):
        if section.get("kind") != "list":
            continue
        for item in section.get("items", []):
            text = str(item)
            if " — " in text:
                name, desc = text.split(" — ", 1)
                rows.append(_format_entry(name.strip(), desc.strip()))
            elif " - " in text:
                name, desc = text.split(" - ", 1)
                rows.append(_format_entry(name.strip(), desc.strip()))
            else:
                rows.append(f"[dim]{text}[/]")
    return rows


def format_help_overlay_content(panel: SidebarPanel | None) -> str:
    if panel is None:
        return "[dim]載入指令說明…[/]"
    rows = _entries_from_ui(panel)
    if not rows:
        rows = _entries_from_panel_lines(panel.lines)
    if not rows:
        return "[dim]（無說明內容）[/]"
    return "\n".join(rows)