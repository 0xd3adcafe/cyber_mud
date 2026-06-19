from __future__ import annotations

from shared.protocol import ERR_PREFIX, MOTD_PREFIX, SYS_PREFIX

SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
STATIC_PREFIX = "›"


def spinner_char(frame: int) -> str:
    return SPINNER_FRAMES[frame % len(SPINNER_FRAMES)]


def classify_output_line(line: str) -> str:
    if line.startswith(MOTD_PREFIX):
        return "motd"
    if line.startswith(SYS_PREFIX):
        return "sys"
    if line.startswith(ERR_PREFIX):
        return "err"
    return "text"


def format_output_line(
    line: str,
    *,
    kind: str | None = None,
    frame: int = 0,
    animate: bool = False,
) -> str:
    kind = kind or classify_output_line(line)
    if kind == "echo":
        if animate:
            spin = spinner_char(frame)
            return f"[bold magenta]{spin}[/] {line}"
        return f"[bold magenta]❯[/] {line}"
    if kind == "err":
        return f"[bold red]✗[/] [red]{line}[/]"
    prefix = spinner_char(frame) if animate else STATIC_PREFIX
    if kind == "motd":
        return f"[cyan]{prefix}[/] [cyan]{line}[/]"
    if kind == "sys":
        return f"[yellow]{prefix}[/] [yellow]{line}[/]"
    return f"[dim]{prefix}[/] {line}"


def format_local_line(text: str) -> str:
    return format_output_line(text, kind="echo")