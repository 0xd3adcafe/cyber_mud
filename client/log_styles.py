from __future__ import annotations

from client.log_classifier import LOG_KINDS
from client.themes import DEFAULT_THEME_ID, LogPalette, log_palette_for_theme

SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
STATIC_PREFIX = "›"


def spinner_char(frame: int) -> str:
    return SPINNER_FRAMES[frame % len(SPINNER_FRAMES)]


def format_log_line(
    line: str,
    *,
    kind: str,
    frame: int = 0,
    animate: bool = False,
    theme_id: str = DEFAULT_THEME_ID,
) -> str:
    if kind not in LOG_KINDS:
        kind = "text"
    palette = log_palette_for_theme(theme_id)
    style = palette.for_kind(kind)
    prefix = spinner_char(frame) if animate else style.glyph

    if kind == "echo":
        if animate:
            return f"[bold {palette.echo_color}]{prefix}[/] {line}"
        return f"[bold {palette.echo_color}]{style.glyph}[/] {line}"

    if kind == "err":
        return f"[bold {palette.err_color}]{style.glyph}[/] [{palette.err_color}]{line}[/]"

    body = line
    if style.muted:
        body = f"[dim italic]{line}[/]"
    elif style.color:
        body = f"[{style.color}]{line}[/]"

    if style.dim_prefix:
        return f"[dim]{prefix}[/] {body}"
    return f"[bold {style.color or palette.default_color}]{prefix}[/] {body}"