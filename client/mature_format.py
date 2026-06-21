from __future__ import annotations

import re

from client.themes import DEFAULT_THEME_ID, MaturePalette, mature_palette_for_theme

_MATURE_PREFIX = "[M·"
_ENV_PREFIX = ">"

_ACTION_RE = re.compile(r"\*([^*]+)\*")
_DIALOGUE_RE = re.compile(r'"([^"]*)"')
_SFX_ONOMATOPOEIA_RE = re.compile(
    r"\*(?:slurp|ahh|mm+h?|ugh|thwack|splash|wet|drip|moan|pop|squelch|gasp|pant|whimper|thud|clang|buzz|hiss|crack|smack|schlick|plap)[~*]?\*",
    re.IGNORECASE,
)


def has_paired_action_markers(text: str) -> bool:
    return bool(_ACTION_RE.search(text))


def has_mature_prefix(text: str) -> bool:
    return text.strip().startswith(_MATURE_PREFIX)


_ECHO_COMMAND_RE = re.compile(r"^>\s+[a-z]+$", re.IGNORECASE)


def is_env_narrator_line(text: str) -> bool:
    stripped = text.strip()
    if not stripped.startswith(_ENV_PREFIX):
        return False
    return not _ECHO_COMMAND_RE.match(stripped)


def is_sfx_line(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if stripped.startswith("~"):
        return True
    if _SFX_ONOMATOPOEIA_RE.search(stripped):
        plain = _ACTION_RE.sub("", stripped).strip(" ~*")
        return len(plain) < 12
    if stripped.startswith("*") and stripped.endswith("*") and len(stripped) <= 32:
        return True
    return False


def is_mature_marker_line(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if has_mature_prefix(stripped):
        return True
    if is_env_narrator_line(stripped):
        return True
    if has_paired_action_markers(stripped):
        return True
    if is_sfx_line(stripped):
        return True
    return False


def format_mature_line(
    line: str,
    *,
    palette: MaturePalette | None = None,
    theme_id: str | None = None,
) -> str:
    if palette is None:
        palette = mature_palette_for_theme(theme_id or DEFAULT_THEME_ID)
    stripped = line.strip()
    if not stripped:
        return ""

    if stripped.startswith(_MATURE_PREFIX):
        stripped = stripped[len(_MATURE_PREFIX) :].lstrip()

    if is_sfx_line(stripped):
        body = stripped.lstrip("~")
        return f"[italic {palette.sfx}]{_format_inline_segments(body, palette, sfx=True)}[/]"

    if stripped.startswith(_ENV_PREFIX):
        body = stripped[1:].lstrip()
        formatted = _format_inline_segments(body, palette, env=True)
        return f"[{palette.env_marker}]▸[/] [{palette.env}]{formatted}[/]"

    return _format_inline_segments(stripped, palette)


def _format_inline_segments(
    text: str,
    palette: MaturePalette,
    *,
    env: bool = False,
    sfx: bool = False,
) -> str:
    parts: list[str] = []
    index = 0
    body_color = palette.env if env else palette.body
    action_color = palette.sfx if sfx else palette.action

    while index < len(text):
        action = _ACTION_RE.match(text, index)
        if action:
            inner = action.group(1)
            parts.append(f"[italic {action_color}]*{inner}*[/]")
            index = action.end()
            continue

        dialogue = _DIALOGUE_RE.match(text, index)
        if dialogue:
            inner = dialogue.group(1)
            parts.append(f'[{palette.dialogue}]"{inner}"[/]')
            index = dialogue.end()
            continue

        next_special = len(text)
        for marker in ("*", '"'):
            pos = text.find(marker, index)
            if pos != -1:
                next_special = min(next_special, pos)
        plain = text[index:next_special]
        if plain:
            if sfx:
                parts.append(plain)
            else:
                parts.append(f"[{body_color}]{plain}[/]")
        index = next_special

    return "".join(parts)