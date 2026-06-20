from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from textual.theme import Theme

DEFAULT_THEME_ID = "night_city"


@dataclass(frozen=True)
class FocusPalette:
    quest_icon: str
    combat_icon: str
    quest_color: str
    combat_color: str
    command_color: str
    gradient: tuple[str, ...]
    status_color: str
    status_muted: str


@dataclass(frozen=True)
class EnvPalette:
    header: str
    scan: str
    hint: str
    desc: str
    move_marker: str
    move_label: str
    move_dir: str
    exits: str
    exit_dest: str
    items: str
    npcs: str
    corpses: str
    players: str
    weather: str

_THEME_SPECS: dict[str, dict[str, str | bool]] = {
    "night_city": {
        "label": "夜城（預設）",
        "primary": "#e94560",
        "accent": "#00fff5",
        "warning": "#ffc857",
        "error": "#ff3864",
        "success": "#2de2a6",
        "background": "#0d0d1a",
        "surface": "#151528",
        "panel": "#1a1a2e",
        "foreground": "#eaeaea",
    },
    "blade_runner": {
        "label": "Blade Runner",
        "primary": "#c9a227",
        "accent": "#3ddad7",
        "warning": "#e8b86d",
        "error": "#c0392b",
        "success": "#58d68d",
        "background": "#0a0a12",
        "surface": "#12101c",
        "panel": "#1c1524",
        "foreground": "#d4c5a9",
    },
    "matrix": {
        "label": "The Matrix",
        "primary": "#00ff41",
        "accent": "#00cc33",
        "warning": "#66ff66",
        "error": "#ff3333",
        "success": "#00ff41",
        "background": "#000000",
        "surface": "#001100",
        "panel": "#002200",
        "foreground": "#00ff41",
    },
    "mr_robot": {
        "label": "Mr. Robot",
        "primary": "#b8b8b8",
        "accent": "#e0e0e0",
        "warning": "#f5a623",
        "error": "#d0021b",
        "success": "#7ed321",
        "background": "#0b0b0b",
        "surface": "#111111",
        "panel": "#1a1a1a",
        "foreground": "#cccccc",
    },
    "hackernet": {
        "label": "Hackernet",
        "primary": "#00bcd4",
        "accent": "#ff4081",
        "warning": "#ffeb3b",
        "error": "#f44336",
        "success": "#00e676",
        "background": "#050a10",
        "surface": "#0a1520",
        "panel": "#0f1e2e",
        "foreground": "#b0bec5",
    },
    "ready_player_one": {
        "label": "Ready Player One",
        "primary": "#ff6ec7",
        "accent": "#7afcff",
        "warning": "#ffe66d",
        "error": "#ff3366",
        "success": "#39ff14",
        "background": "#1a0a2e",
        "surface": "#220f3d",
        "panel": "#2d1b4e",
        "foreground": "#f0e6ff",
    },
    "tron": {
        "label": "Tron",
        "primary": "#00d4ff",
        "accent": "#00ffff",
        "warning": "#ffaa00",
        "error": "#ff4444",
        "success": "#00ffcc",
        "background": "#000814",
        "surface": "#001020",
        "panel": "#001a33",
        "foreground": "#c8f4ff",
    },
    "grok_night": {
        "label": "Grok Night",
        "primary": "#e879f9",
        "accent": "#c084fc",
        "warning": "#fbbf24",
        "error": "#f87171",
        "success": "#4ade80",
        "background": "#0d0d0d",
        "surface": "#161616",
        "panel": "#1c1c1c",
        "foreground": "#e5e5e5",
    },
}


def _muted_hex(hex_color: str, factor: float = 0.72) -> str:
    raw = hex_color.lstrip("#")
    if len(raw) != 6:
        return hex_color
    r, g, b = int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)
    return f"#{int(r * factor):02x}{int(g * factor):02x}{int(b * factor):02x}"


_THEME_FOCUS_ICONS: dict[str, dict[str, str]] = {
    "night_city": {"quest": "◆", "combat": "⚔"},
    "blade_runner": {"quest": "◆", "combat": "⚔"},
    "matrix": {"quest": "◈", "combat": "⌗"},
    "mr_robot": {"quest": "▸", "combat": "⚡"},
    "hackernet": {"quest": "◆", "combat": "⚔"},
    "ready_player_one": {"quest": "★", "combat": "⚔"},
    "tron": {"quest": "◆", "combat": "⊹"},
    "grok_night": {"quest": "◆", "combat": "⚔"},
}


def focus_palette_for_theme(theme_id: str) -> FocusPalette:
    resolved = resolve_theme_id(theme_id) or DEFAULT_THEME_ID
    spec = _THEME_SPECS[resolved]
    accent = str(spec["accent"])
    primary = str(spec["primary"])
    warning = str(spec["warning"])
    error = str(spec["error"])
    surface = str(spec["surface"])
    panel = str(spec["panel"])
    icons = _THEME_FOCUS_ICONS.get(resolved, _THEME_FOCUS_ICONS["night_city"])
    return FocusPalette(
        quest_icon=icons["quest"],
        combat_icon=icons["combat"],
        quest_color=warning,
        combat_color=error,
        command_color=accent,
        gradient=(
            surface,
            panel,
            _muted_hex(accent, 0.42),
            _muted_hex(accent, 0.68),
            accent,
            primary,
        ),
        status_color=accent,
        status_muted=_muted_hex(str(spec["foreground"]), 0.55),
    )


def env_palette_for_theme(theme_id: str) -> EnvPalette:
    resolved = resolve_theme_id(theme_id) or DEFAULT_THEME_ID
    spec = _THEME_SPECS[resolved]
    foreground = str(spec["foreground"])
    return EnvPalette(
        header=foreground,
        scan=str(spec["accent"]),
        hint=str(spec["warning"]),
        desc=_muted_hex(foreground),
        move_marker=str(spec["accent"]),
        move_label=str(spec["accent"]),
        move_dir=str(spec["warning"]),
        exits=str(spec["warning"]),
        exit_dest=str(spec["success"]),
        items=str(spec["success"]),
        npcs=str(spec["primary"]),
        corpses=str(spec["error"]),
        players=str(spec.get("info", spec["accent"])),
        weather=str(spec["accent"]),
    )


def theme_ids() -> tuple[str, ...]:
    return tuple(_THEME_SPECS.keys())


def theme_label(theme_id: str) -> str:
    spec = _THEME_SPECS.get(theme_id)
    if spec is None:
        return theme_id
    return str(spec["label"])


def resolve_theme_id(raw: str) -> str | None:
    key = raw.strip().lower().replace("-", "_")
    if key in _THEME_SPECS:
        return key
    for theme_id, spec in _THEME_SPECS.items():
        if key == str(spec["label"]).lower():
            return theme_id
    return None


def build_textual_theme(theme_id: str) -> Theme:
    resolved = resolve_theme_id(theme_id) or DEFAULT_THEME_ID
    spec = _THEME_SPECS[resolved]
    return Theme(
        name=resolved,
        primary=str(spec["primary"]),
        accent=str(spec["accent"]),
        warning=str(spec["warning"]),
        error=str(spec["error"]),
        success=str(spec["success"]),
        background=str(spec["background"]),
        surface=str(spec["surface"]),
        panel=str(spec["panel"]),
        foreground=str(spec["foreground"]),
        dark=True,
    )


def format_theme_list() -> str:
    lines = ["可用主題："]
    for theme_id in theme_ids():
        lines.append(f"  {theme_id} — {theme_label(theme_id)}")
    return "\n".join(lines)


def parse_theme_command(args: str) -> tuple[str, str | None]:
    """Return (action, theme_id). action: list | set | invalid."""
    text = args.strip()
    if not text or text == "list":
        return "list", None
    resolved = resolve_theme_id(text)
    if resolved is None:
        return "invalid", None
    return "set", resolved


def select_options() -> tuple[tuple[str, str], ...]:
    return tuple((theme_label(theme_id), theme_id) for theme_id in theme_ids())


def settings_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "cyber_mud" / "settings.json"
    return Path.home() / ".config" / "cyber_mud" / "settings.json"


def load_theme_id() -> str:
    path = settings_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return DEFAULT_THEME_ID
    raw = data.get("theme", DEFAULT_THEME_ID)
    return resolve_theme_id(str(raw)) or DEFAULT_THEME_ID


def save_theme_id(theme_id: str) -> None:
    resolved = resolve_theme_id(theme_id) or DEFAULT_THEME_ID
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"theme": resolved}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")