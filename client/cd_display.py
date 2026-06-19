from __future__ import annotations

import re
import time

_CD_LINE_ZH = re.compile(r"^(行動冷卻中)（(\d+)s?）。(.*)$")
_CD_LINE_EN = re.compile(r"^(Action on cooldown) \((\d+)s?\)\.(.*)$")
_COMBAT_CD_META = re.compile(r"P:(\d+)\s+N:(\d+)")


def parse_cooldown_line(line: str) -> tuple[str, int] | None:
    for pattern in (_CD_LINE_ZH, _CD_LINE_EN):
        match = pattern.match(line.strip())
        if match:
            return match.group(1), int(match.group(2))
    return None


def format_cooldown_line(prefix: str, seconds: int, *, suffix: str = "") -> str:
    remaining = max(0, seconds)
    tail = suffix or "。"
    if not tail.startswith("。") and not tail.startswith("."):
        if tail:
            tail = f" {tail}"
        else:
            tail = "。"
    return f"{prefix}（{remaining}s）{tail}"


def parse_combat_cd_meta(value: str) -> tuple[int, int]:
    match = _COMBAT_CD_META.match(value.strip())
    if match is None:
        return 0, 0
    return int(match.group(1)), int(match.group(2))


def remaining_seconds(total: int, synced_at: float, *, now: float | None = None) -> int:
    if total <= 0:
        return 0
    current = now if now is not None else time.monotonic()
    elapsed = max(0, int(current - synced_at))
    return max(0, total - elapsed)


def format_combat_cd_label(player_secs: int, npc_secs: int) -> str:
    parts: list[str] = []
    if player_secs > 0:
        parts.append(f"P:{player_secs}s")
    if npc_secs > 0:
        parts.append(f"N:{npc_secs}s")
    return " ".join(parts)