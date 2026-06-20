from __future__ import annotations

import re

from client.themes import DEFAULT_THEME_ID, EnvPalette, env_palette_for_theme

_HEADER_MARK = "◈"

_EXIT_PREFIXES = ("出口：", "Exits:")
_ITEM_PREFIXES = ("地上：", "On the ground:", "物品：", "Items:")
_NPC_PREFIXES = ("這裡有：", "Here:", "人物：", "People:")
_CORPSE_PREFIXES = ("屍體：", "Corpses:")
_WEATHER_PREFIXES = ("天氣：", "Weather:")
_PLAYER_PREFIXES = ("玩家：", "Player:")
_MOVE_PREFIXES = ("你前往 ", "You go ")

_LIST_SEP_RE = re.compile(r"[、,]")


def reset_environment_state(state: dict[str, str]) -> None:
    state.clear()
    state["phase"] = "idle"
    state["desc_lines"] = 0


def format_environment_line(
    line: str,
    state: dict[str, str],
    *,
    palette: EnvPalette | None = None,
    theme_id: str | None = None,
) -> str:
    if palette is None:
        palette = env_palette_for_theme(theme_id or DEFAULT_THEME_ID)
    stripped = line.strip()
    if not stripped:
        return ""

    if stripped.startswith(_HEADER_MARK):
        state["phase"] = "desc"
        state["desc_lines"] = 0
        if "掃描" in stripped or "Scan" in stripped:
            return f"[bold {palette.scan}]{stripped}[/]"
        if "隱藏" in stripped or "Hidden clue" in stripped:
            hint = stripped.split("：", 1)[-1].split(":", 1)[-1].strip()
            return (
                f"[bold {palette.hint}]◈ 隱藏線索[/] "
                f"[italic {palette.hint}]{hint}[/]"
            )
        return f"[bold {palette.header}]{stripped}[/]"

    for prefix in _MOVE_PREFIXES:
        if stripped.startswith(prefix):
            state["phase"] = "idle"
            direction = stripped[len(prefix) :].rstrip("。").rstrip(".")
            return (
                f"[{palette.move_marker}]▸[/] "
                f"[{palette.move_label}]移動[/] "
                f"[bold {palette.move_dir}]{direction}[/]"
            )

    for prefix in _WEATHER_PREFIXES:
        if stripped.startswith(prefix):
            state["phase"] = "meta"
            value = stripped[len(prefix) :].strip()
            return f"[{palette.weather}]▸ {prefix}[/][{palette.weather}]{value}[/]"

    for prefix in _EXIT_PREFIXES:
        if stripped.startswith(prefix):
            state["phase"] = "meta"
            body = stripped[len(prefix) :].strip()
            return _format_labeled_list(prefix, body, palette.exits, _format_entity_label)

    for prefix in _ITEM_PREFIXES:
        if stripped.startswith(prefix):
            state["phase"] = "meta"
            body = stripped[len(prefix) :].strip()
            return _format_labeled_list(prefix, body, palette.items, _format_entity_label)

    for prefix in _NPC_PREFIXES:
        if stripped.startswith(prefix):
            state["phase"] = "meta"
            body = stripped[len(prefix) :].strip()
            return _format_labeled_list(prefix, body, palette.npcs, _format_entity_label)

    for prefix in _CORPSE_PREFIXES:
        if stripped.startswith(prefix):
            state["phase"] = "meta"
            body = stripped[len(prefix) :].strip()
            return _format_labeled_list(prefix, body, palette.corpses, _format_entity_label)

    for prefix in _PLAYER_PREFIXES:
        if stripped.startswith(prefix):
            state["phase"] = "meta"
            value = stripped[len(prefix) :].strip()
            return (
                f"[bold {palette.players}]▸ {prefix}[/]"
                f"[{_emphasis_color(palette.players)}]{value}[/]"
            )

    if state.get("phase") == "desc":
        desc_lines = int(state.get("desc_lines", 0))
        state["desc_lines"] = desc_lines + 1
        if desc_lines > 0:
            return f"[dim italic {palette.desc}]{stripped}[/]"
        return f"[italic {palette.desc}]{stripped}[/]"

    return line


def _emphasis_color(color: str) -> str:
    if color.startswith("#"):
        return f"bold {color}"
    return f"bright_{color}"


def _format_labeled_list(
    prefix: str,
    body: str,
    color: str,
    formatter,
) -> str:
    parts = [part.strip() for part in _LIST_SEP_RE.split(body) if part.strip()]
    if not parts:
        return f"[bold {color}]▸ {prefix}[/]"
    sep = "、" if "、" in body else ", "
    joined = sep.join(formatter(part, color) for part in parts)
    return f"[bold {color}]▸ {prefix}[/] {joined}"


def _format_entity_label(label: str, color: str) -> str:
    match = re.match(r"^(.+?)\s*\(([^)]+)\)\s*$", label)
    if match:
        name, suffix = match.group(1).strip(), match.group(2).strip()
        emphasis = _emphasis_color(color)
        return f"[{color}]{name}[/][dim] ([/][{emphasis}]{suffix}[/][dim])[/]"
    return f"[{color}]{label}[/]"