from __future__ import annotations

import re

from client.meta_handlers import ClientViewState
from client.output_prefix import spinner_char

_HP_RATIO = re.compile(r"(\d+)\s*/\s*(\d+)")
_LOW_HP_RATIO = 0.35
_LOW_RAM_RATIO = 0.25


def _parse_ratio(value: str) -> float | None:
    match = _HP_RATIO.match(value.strip())
    if match is None:
        return None
    current, maximum = int(match.group(1)), int(match.group(2))
    if maximum <= 0:
        return None
    return current / maximum


def hp_ratio(state: ClientViewState) -> float | None:
    return _parse_ratio(state.hp)


def ram_ratio(state: ClientViewState) -> float | None:
    return _parse_ratio(state.ram)


def vitals_alert(state: ClientViewState) -> bool:
    hp = hp_ratio(state)
    if hp is not None and hp <= _LOW_HP_RATIO:
        return True
    if state.net_shell:
        ram = ram_ratio(state)
        if ram is not None and ram <= _LOW_RAM_RATIO:
            return True
    return False


def combat_active(state: ClientViewState) -> bool:
    return state.in_combat


def quest_active(state: ClientViewState) -> bool:
    return bool(state.hint or state.quest)


def status_needs_animation(state: ClientViewState) -> bool:
    return combat_active(state) or quest_active(state) or vitals_alert(state) or state.net_shell


def spin(frame: int) -> str:
    return spinner_char(frame)


def animated_icon(icon: str, *, frame: int, active: bool) -> str:
    if not active:
        return icon
    return spin(frame)