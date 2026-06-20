from __future__ import annotations

from client.log_classifier import classify_log_line
from client.log_styles import SPINNER_FRAMES, format_log_line, spinner_char

STATIC_PREFIX = "›"


def classify_output_line(line: str) -> str:
    return classify_log_line(line)


def format_output_line(
    line: str,
    *,
    kind: str | None = None,
    frame: int = 0,
    animate: bool = False,
    theme_id: str | None = None,
) -> str:
    resolved = classify_log_line(line, kind=kind)
    return format_log_line(
        line,
        kind=resolved,
        frame=frame,
        animate=animate,
        theme_id=theme_id or "night_city",
    )


def format_local_line(text: str, *, theme_id: str | None = None) -> str:
    return format_log_line(text, kind="echo", theme_id=theme_id or "night_city")