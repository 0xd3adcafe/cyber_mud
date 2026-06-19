from __future__ import annotations

import re

REPEAT_MAX = 99
REPEAT_INTERVAL_SECONDS = 0.5

REPEAT_BLOCKED = frozenset(
    {
        "quit",
        "login",
        "register",
        "help",
        "map",
        "pda",
        "equipment",
        "prompt",
        "look",
        "scan",
        "shop",
        "buy",
        "sell",
        "time",
        "net",
        "netrun",
    }
)

_PREFIX_COUNT = re.compile(r"^(\d+)\s+(.+)$")
_DOT_COUNT = re.compile(r"^(.+)\.(\d+)$")


def parse_repeat(line: str) -> tuple[int, str]:
    text = line.strip()
    if not text:
        return 1, text

    prefix = _PREFIX_COUNT.match(text)
    if prefix:
        count = min(max(int(prefix.group(1)), 1), REPEAT_MAX)
        return count, prefix.group(2).strip()

    parts = text.split(maxsplit=1)
    verb_token = parts[0]
    rest = parts[1] if len(parts) > 1 else ""
    dot = _DOT_COUNT.match(verb_token)
    if dot and dot.group(1):
        count = min(max(int(dot.group(2)), 1), REPEAT_MAX)
        rebuilt = f"{dot.group(1)} {rest}".strip() if rest else dot.group(1)
        return count, rebuilt

    return 1, text