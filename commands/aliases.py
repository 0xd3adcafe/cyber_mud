from __future__ import annotations

from entities.player import Player

DEFAULT_ALIASES: dict[str, str] = {
    "l": "look",
    "i": "inventory",
    "inv": "inventory",
    "get": "take",
    "n": "go north",
    "s": "go south",
    "e": "go east",
    "w": "go west",
    "u": "go up",
    "d": "go down",
    "h": "help",
    "q": "quit",
    "eq": "equipment",
    "st": "status",
    "sc": "scan",
}


def expand_line(line: str, player: Player) -> str:
    text = line.strip()
    if not text:
        return text
    parts = text.split(maxsplit=1)
    key = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""
    expanded = DEFAULT_ALIASES.get(key)
    if expanded is None:
        return text
    return f"{expanded} {rest}".strip() if rest else expanded